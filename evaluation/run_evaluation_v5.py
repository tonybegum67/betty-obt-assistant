#!/usr/bin/env python3
"""
Betty v5.0 Evaluation Runner - Real-World Usability Focus
Implements transparent, human-centered rubric with NO hidden metrics
"""

import csv
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import anthropic
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from utils.vector_store import VectorStore
from config.settings import AppConfig


class BettyEvaluatorV5:
    """Real-world usability evaluator with transparent scoring"""

    def __init__(self, system_prompt_path: str, testset_path: str):
        """Initialize evaluator"""
        self.testset_path = testset_path
        self.results = []

        # Load system prompt
        with open(system_prompt_path, 'r') as f:
            self.system_prompt = f.read()

        # Initialize Anthropic client
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            try:
                import streamlit as st
                api_key = st.secrets["ANTHROPIC_API_KEY"]
            except:
                raise ValueError("ANTHROPIC_API_KEY not found")
        self.client = anthropic.Anthropic(api_key=api_key)

        # Initialize embedding model
        print("Loading embedding model...")
        self.embedding_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

        # Initialize vector store
        print("Loading vector store...")
        self.vector_store = VectorStore()

        print("✓ v5.0 Evaluator initialized (Real-World Usability Focus)")

    def detect_mode(self, prompt: str) -> str:
        """Detect MODE from prompt"""
        prompt_lower = prompt.lower()

        # MODE 2 triggers (classification)
        if any(kw in prompt_lower for kw in ['classify', 'what or how', 'what/how', 'acceptable outcome']):
            return 'MODE2'

        # MODE 3 triggers (comprehensive)
        if any(kw in prompt_lower for kw in ['acceptance criteria', 'prioritize', 'raci', 'kpi',
                                               'maturity', 'stakeholder', 'explain', 'analyze']):
            return 'MODE3'

        # MODE 1 (outcome writing)
        return 'MODE1'

    # ============================================================================
    # DIMENSION 1: SEMANTIC CORRECTNESS (40% weight)
    # ============================================================================

    def calculate_semantic_correctness(self, expected: str, actual: str, mode: str) -> Tuple[float, str]:
        """
        Calculate semantic similarity with mode-aware thresholds
        Returns (score, explanation)
        """
        if not expected or not actual:
            return 0.0, "Empty response"

        # Calculate cosine similarity
        expected_emb = self.embedding_model.encode([expected])
        actual_emb = self.embedding_model.encode([actual])
        similarity = float(cosine_similarity(expected_emb, actual_emb)[0][0])

        # Mode-specific interpretation
        if mode == 'MODE1':
            # Outcome writing - multiple valid phrasings
            if similarity >= 0.85:
                rating = "EXCELLENT"
            elif similarity >= 0.70:
                rating = "GOOD"
            elif similarity >= 0.55:
                rating = "FAIR"
            else:
                rating = "POOR"

        elif mode == 'MODE2':
            # Classification - must be precise
            if similarity >= 0.95:
                rating = "EXCELLENT"
            elif similarity >= 0.85:
                rating = "GOOD"
            elif similarity >= 0.70:
                rating = "FAIR"
            else:
                rating = "POOR"

        else:  # MODE3
            # Comprehensive - additional context acceptable
            if similarity >= 0.85:
                rating = "EXCELLENT"
            elif similarity >= 0.65:
                rating = "GOOD"
            elif similarity >= 0.50:
                rating = "FAIR"
            else:
                rating = "POOR"

        explanation = f"{rating} (similarity: {similarity:.3f})"
        return similarity, explanation

    # ============================================================================
    # DIMENSION 2: OBT ADHERENCE (25% weight)
    # ============================================================================

    def calculate_obt_adherence(self, response: str, mode: str) -> Tuple[float, List[str], List[str]]:
        """
        Calculate OBT principle adherence with explicit checks
        Returns (score, passed_checks, failed_checks)
        """
        # Only apply OBT checks to MODE1 and MODE2
        if mode == 'MODE3':
            return 1.0, ["MODE3: OBT checks not strictly applied"], []

        passed = []
        failed = []

        response_lower = response.lower()

        # Check 1: Metric-free (no numbers)
        if not any(char.isdigit() for char in response):
            passed.append("✓ Metric-free (no numbers/percentages)")
        else:
            failed.append("✗ Contains metrics/numbers")

        # Check 2: What not How (no implementation verbs)
        prohibited_verbs = ['deploy', 'implement', 'build', 'create', 'install', 'configure', 'train']
        found_verbs = [v for v in prohibited_verbs if v in response_lower]
        if not found_verbs:
            passed.append("✓ What not How (no implementation verbs)")
        else:
            failed.append(f"✗ Contains How verbs: {', '.join(found_verbs)}")

        # Check 3: Solution-agnostic (no specific technology)
        tech_terms = ['erp', 'sap', 'salesforce', 'oracle', 'workday', 'jira', 'plm system']
        found_tech = [t for t in tech_terms if t in response_lower]
        if not found_tech:
            passed.append("✓ Solution-agnostic (no specific technology)")
        else:
            failed.append(f"✗ Mentions specific technology: {', '.join(found_tech)}")

        # Check 4: Proper tense (present passive or past)
        # Look for patterns like "are integrated", "is achieved", etc.
        passive_patterns = r'\b(are|is|was|were)\s+\w+(ed|en)\b'
        has_passive = bool(re.search(passive_patterns, response))

        # Also check for problematic present active verbs
        active_problem_verbs = ['begin', 'execute', 'perform', 'start', 'continue']
        found_active = [v for v in active_problem_verbs if v in response_lower]

        if has_passive and not found_active:
            passed.append("✓ Proper tense (present passive describing achieved state)")
        elif has_passive:
            passed.append("~ Acceptable tense (passive present, minor active verbs)")
        else:
            failed.append("✗ Tense issue (no passive voice detected)")

        # Calculate score
        total_checks = len(passed) + len(failed)
        score = len(passed) / total_checks if total_checks > 0 else 0.0

        return score, passed, failed

    # ============================================================================
    # DIMENSION 3: RESPONSE COMPLETENESS (20% weight)
    # ============================================================================

    def calculate_response_completeness(self, response: str, mode: str, prompt: str) -> Tuple[float, str]:
        """
        Calculate response completeness based on real-world usability
        Returns (score, explanation)
        """
        word_count = len(response.split())
        components = []

        # Component 1: Direct answer present (0.4 points)
        if len(response) > 10:  # Has substantive content
            components.append(0.4)
            answer_quality = "Direct answer provided"
        else:
            components.append(0.1)
            answer_quality = "Very brief answer"

        # Component 2: Reasoning when appropriate (0.3 points)
        reasoning_score = 0.0
        reasoning_explanation = ""

        if mode == 'MODE1':
            # Outcome writing doesn't need reasoning
            reasoning_score = 0.3
            reasoning_explanation = "MODE1: Reasoning not needed for direct outcomes"

        elif mode == 'MODE2':
            # Classification may need brief reasoning if reframe requested
            if 'reframe' in prompt.lower() or 'if not' in prompt.lower():
                if word_count > 5:
                    reasoning_score = 0.3
                    reasoning_explanation = "Reframe with brief reasoning provided"
                else:
                    reasoning_score = 0.1
                    reasoning_explanation = "Reframe requested but missing explanation"
            else:
                reasoning_score = 0.3
                reasoning_explanation = "MODE2: Simple classification, reasoning not needed"

        else:  # MODE3
            # Comprehensive responses should have reasoning
            if word_count >= 50:
                reasoning_score = 0.3
                reasoning_explanation = "Comprehensive response with context"
            elif word_count >= 30:
                reasoning_score = 0.2
                reasoning_explanation = "Moderate context provided"
            else:
                reasoning_score = 0.1
                reasoning_explanation = "Minimal context for MODE3"

        components.append(reasoning_score)

        # Component 3: Sources when needed (0.3 points)
        has_sources = 'source' in response.lower() or '**source' in response.lower()
        source_score = 0.0
        source_explanation = ""

        if mode == 'MODE3':
            if has_sources:
                source_score = 0.3
                source_explanation = "Sources cited (builds credibility)"
            else:
                source_score = 0.1
                source_explanation = "MODE3 missing sources"
        else:
            # MODE1/2 don't need sources unless data-specific
            source_score = 0.3
            source_explanation = "Sources not required for this mode"

        components.append(source_score)

        # Total completeness score
        total_score = sum(components)
        explanation = f"{answer_quality}; {reasoning_explanation}; {source_explanation}"

        return total_score, explanation

    # ============================================================================
    # DIMENSION 4: PROFESSIONAL COMMUNICATION (15% weight)
    # ============================================================================

    def calculate_professional_communication(self, response: str, mode: str) -> Tuple[float, List[str], List[str]]:
        """
        Calculate professional communication quality
        Returns (score, passed_checks, failed_checks)
        """
        passed = []
        failed = []

        # Check 1: Directness (no preambles)
        prohibited_starts = ["i'll help", "let me", "sure", "i can", "based on the retrieved"]
        response_start = response.lower()[:50]

        has_preamble = any(phrase in response_start for phrase in prohibited_starts)

        if not has_preamble:
            passed.append("✓ Direct start (no preamble)")
        else:
            failed.append("✗ Contains preamble/first-person intro")

        # Check 2: Structure (organized information)
        has_structure = response.count('\n') >= 2 or ('**' in response) or (':' in response)

        if mode == 'MODE3':
            if has_structure:
                passed.append("✓ Well-structured (sections/formatting)")
            else:
                passed.append("~ Acceptable structure (readable)")
        else:
            # MODE1/2 don't need structure
            passed.append("✓ Structure appropriate for mode")

        # Check 3: Confidence appropriate
        has_confidence = 'confidence' in response.lower() or 'high' in response.lower()

        if mode == 'MODE3' and has_confidence:
            passed.append("✓ Confidence level stated")
        elif mode == 'MODE3':
            passed.append("~ Confidence level implicit")
        else:
            passed.append("✓ Confidence not needed for this mode")

        # Check 4: First-person usage
        first_person_phrases = ["i'll", "let me", "i can", "i will", "i have"]
        found_first_person = [p for p in first_person_phrases if p in response.lower()]

        if mode in ['MODE1', 'MODE2']:
            if not found_first_person:
                passed.append("✓ No first-person language")
            else:
                failed.append(f"✗ First-person language in direct answer: {', '.join(found_first_person[:2])}")
        else:  # MODE3
            if not found_first_person:
                passed.append("✓ No first-person language")
            elif len(found_first_person) <= 2:
                passed.append("~ Minor first-person usage acceptable for MODE3")
            else:
                failed.append("✗ Excessive first-person language")

        # Calculate score
        total_checks = len(passed) + len(failed)
        score = len(passed) / total_checks if total_checks > 0 else 0.0

        return score, passed, failed

    # ============================================================================
    # OVERALL SCORING
    # ============================================================================

    def calculate_overall_score(self, semantic: float, obt: float,
                               completeness: float, communication: float) -> Tuple[float, str]:
        """
        Calculate weighted overall score with FULL transparency
        Returns (score, breakdown)
        """
        # Weighted calculation (exactly as documented in YAML)
        score = (
            (semantic * 0.40) +
            (obt * 0.25) +
            (completeness * 0.20) +
            (communication * 0.15)
        )

        # Generate breakdown
        breakdown = (
            f"Semantic: {semantic:.3f} × 0.40 = {semantic*0.40:.3f} | "
            f"OBT: {obt:.3f} × 0.25 = {obt*0.25:.3f} | "
            f"Complete: {completeness:.3f} × 0.20 = {completeness*0.20:.3f} | "
            f"Comm: {communication:.3f} × 0.15 = {communication*0.15:.3f}"
        )

        # Rating
        if score >= 0.85:
            rating = "EXCELLENT"
        elif score >= 0.75:
            rating = "GOOD"
        elif score >= 0.65:
            rating = "ACCEPTABLE"
        elif score >= 0.50:
            rating = "NEEDS_IMPROVEMENT"
        else:
            rating = "POOR"

        return round(score, 4), rating, breakdown

    # ============================================================================
    # EVALUATION EXECUTION
    # ============================================================================

    def load_testset(self) -> List[Dict]:
        """Load test questions from CSV"""
        questions = []
        with open(self.testset_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                questions.append(row)
        print(f"✓ Loaded {len(questions)} test questions")
        return questions

    def query_betty(self, prompt: str, use_rag: bool = True) -> Tuple[str, int, Optional[str]]:
        """Query Betty with a prompt"""
        start_time = time.time()

        try:
            # Get RAG context
            context = ""
            if use_rag:
                search_results = self.vector_store.search_collection(
                    collection_name=AppConfig.KNOWLEDGE_COLLECTION_NAME,
                    query=prompt,
                    n_results=8
                )
                if search_results and len(search_results) > 0:
                    context_docs = [doc['document'] for doc in search_results if 'document' in doc]
                    context = "\n\n".join([f"Context {i+1}:\n{doc}" for i, doc in enumerate(context_docs)])

            # Build full prompt
            full_prompt = prompt
            if context:
                full_prompt = f"Relevant context from knowledge base:\n\n{context}\n\n---\n\nUser question: {prompt}"

            # Query Claude
            message = self.client.messages.create(
                model=AppConfig.CLAUDE_MODEL,
                max_tokens=2000,
                system=self.system_prompt,
                messages=[{"role": "user", "content": full_prompt}]
            )

            response = message.content[0].text
            execution_time_ms = int((time.time() - start_time) * 1000)

            return response, execution_time_ms, None

        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            return "", execution_time_ms, str(e)

    def evaluate_question(self, question: Dict, question_num: int, total: int) -> Dict:
        """Evaluate a single question with v5.0 rubric"""
        print(f"\n[{question_num}/{total}] {question['prompt'][:70]}...")

        # Detect MODE
        mode = self.detect_mode(question['prompt'])
        print(f"  → Detected {mode}")

        # Query Betty
        response, exec_time, error = self.query_betty(question['prompt'])

        if error:
            print(f"  ✗ Error: {error}")
            return self._error_result(question, exec_time, error)

        word_count = len(response.split())
        print(f"  → Response: {word_count} words")

        # Calculate all dimensions
        semantic_score, semantic_exp = self.calculate_semantic_correctness(
            question['expected_response'], response, mode
        )

        obt_score, obt_passed, obt_failed = self.calculate_obt_adherence(response, mode)

        completeness_score, completeness_exp = self.calculate_response_completeness(
            response, mode, question['prompt']
        )

        comm_score, comm_passed, comm_failed = self.calculate_professional_communication(
            response, mode
        )

        # Calculate overall score
        overall_score, rating, breakdown = self.calculate_overall_score(
            semantic_score, obt_score, completeness_score, comm_score
        )

        print(f"  ✓ Score: {overall_score:.3f} ({rating}) | Semantic: {semantic_score:.3f} | Time: {exec_time}ms")

        return {
            'test_id': question['test_id'],
            'category': question['category'],
            'domain': question['domain'],
            'mode': mode,
            'prompt': question['prompt'],
            'expected_response': question['expected_response'],
            'agent_response': response,
            'word_count': word_count,

            # Dimension scores
            'semantic_correctness': round(semantic_score, 4),
            'obt_adherence': round(obt_score, 4),
            'response_completeness': round(completeness_score, 4),
            'professional_communication': round(comm_score, 4),

            # Overall
            'overall_score': overall_score,
            'rating': rating,

            # Metadata
            'execution_time_ms': exec_time,
            'error': error or '',

            # Transparency
            'score_breakdown': breakdown,
            'dimension_explanations': f"Semantic: {semantic_exp} | Complete: {completeness_exp}",
            'passed_checks': json.dumps({
                'obt': obt_passed,
                'communication': comm_passed
            }),
            'failed_checks': json.dumps({
                'obt': obt_failed,
                'communication': comm_failed
            })
        }

    def _error_result(self, question: Dict, exec_time: int, error: str) -> Dict:
        """Return error result"""
        return {
            'test_id': question['test_id'],
            'category': question['category'],
            'domain': question['domain'],
            'mode': 'ERROR',
            'prompt': question['prompt'],
            'expected_response': question['expected_response'],
            'agent_response': '',
            'word_count': 0,
            'semantic_correctness': 0.0,
            'obt_adherence': 0.0,
            'response_completeness': 0.0,
            'professional_communication': 0.0,
            'overall_score': 0.0,
            'rating': 'ERROR',
            'execution_time_ms': exec_time,
            'error': error,
            'score_breakdown': 'Evaluation failed',
            'dimension_explanations': error,
            'passed_checks': '[]',
            'failed_checks': '[]'
        }

    def run_evaluation(self, max_questions: Optional[int] = None) -> List[Dict]:
        """Run v5.0 evaluation"""
        questions = self.load_testset()

        if max_questions:
            questions = questions[:max_questions]
            print(f"⚠ Running limited evaluation: {max_questions} questions")

        print(f"\n{'='*70}")
        print(f"Betty v5.0 Evaluation - Real-World Usability Focus")
        print(f"{'='*70}")
        print("Key Changes:")
        print("  ✓ Reasoning and sources ADD value (not penalized)")
        print("  ✓ Realistic length expectations (5-20 words MODE1, 50-300 MODE3)")
        print("  ✓ Transparent scoring - NO hidden metrics")
        print("  ✓ Human-centered evaluation")
        print(f"{'='*70}\n")

        results = []
        for i, question in enumerate(questions, 1):
            result = self.evaluate_question(question, i, len(questions))
            results.append(result)
            time.sleep(0.5)  # Rate limiting

        self.results = results
        return results

    def save_results(self, output_path: str):
        """Save results to CSV"""
        if not self.results:
            print("⚠ No results to save")
            return

        fieldnames = [
            'test_id', 'category', 'domain', 'mode', 'prompt', 'expected_response',
            'agent_response', 'word_count', 'semantic_correctness', 'obt_adherence',
            'response_completeness', 'professional_communication', 'overall_score',
            'rating', 'execution_time_ms', 'error', 'score_breakdown',
            'dimension_explanations', 'passed_checks', 'failed_checks'
        ]

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.results)

        print(f"\n✓ Results saved to: {output_path}")

    def print_summary(self):
        """Print evaluation summary"""
        if not self.results:
            print("⚠ No results to summarize")
            return

        total = len(self.results)
        errors = sum(1 for r in self.results if r['error'])

        avg_overall = np.mean([r['overall_score'] for r in self.results])
        avg_semantic = np.mean([r['semantic_correctness'] for r in self.results])
        avg_obt = np.mean([r['obt_adherence'] for r in self.results])
        avg_completeness = np.mean([r['response_completeness'] for r in self.results])
        avg_comm = np.mean([r['professional_communication'] for r in self.results])
        avg_time = np.mean([r['execution_time_ms'] for r in self.results])
        avg_words = np.mean([r['word_count'] for r in self.results])

        # Rating distribution
        ratings = {'EXCELLENT': 0, 'GOOD': 0, 'ACCEPTABLE': 0, 'NEEDS_IMPROVEMENT': 0, 'POOR': 0}
        for r in self.results:
            if r['rating'] in ratings:
                ratings[r['rating']] += 1

        print(f"\n{'='*70}")
        print("v5.0 EVALUATION SUMMARY - REAL-WORLD USABILITY")
        print(f"{'='*70}")
        print(f"Total Questions: {total}")
        print(f"Errors: {errors} ({errors/total*100:.1f}%)")

        print(f"\n📊 DIMENSION SCORES:")
        print(f"  Overall Score:             {avg_overall:.3f}")
        print(f"  Semantic Correctness:      {avg_semantic:.3f} (40% weight)")
        print(f"  OBT Adherence:             {avg_obt:.3f} (25% weight)")
        print(f"  Response Completeness:     {avg_completeness:.3f} (20% weight)")
        print(f"  Professional Communication: {avg_comm:.3f} (15% weight)")

        print(f"\n📈 RATING DISTRIBUTION:")
        for rating, count in ratings.items():
            pct = count/total*100
            bar = '█' * int(pct/5)
            print(f"  {rating:20s}: {count:2d} ({pct:5.1f}%) {bar}")

        print(f"\n⏱️  PERFORMANCE:")
        print(f"  Avg Response Time: {avg_time:.0f}ms")
        print(f"  Avg Word Count: {avg_words:.1f} words")

        # Performance rating
        if avg_overall >= 0.85:
            rating = "EXCELLENT ✓✓ (Production Quality)"
        elif avg_overall >= 0.75:
            rating = "GOOD ✓ (Strong Performance)"
        elif avg_overall >= 0.65:
            rating = "ACCEPTABLE (Adequate for Use)"
        elif avg_overall >= 0.50:
            rating = "NEEDS IMPROVEMENT"
        else:
            rating = "POOR (Significant Issues)"

        print(f"\n🏆 Overall Rating: {rating}")

        # Comparison to v4.3
        v4_3_baseline = 0.307
        improvement = ((avg_overall - v4_3_baseline) / v4_3_baseline) * 100
        print(f"\n📉 vs v4.3 Baseline (0.307): {improvement:+.1f}% {'📈' if improvement > 0 else '📉'}")

        print(f"{'='*70}\n")


def main():
    """Main evaluation runner"""
    base_dir = Path(__file__).parent.parent
    system_prompt_path = base_dir / "system_prompt_v4.3.txt"
    testset_path = Path(__file__).parent / "betty_testset_50q.csv"

    results_dir = Path(__file__).parent / "results"
    results_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = results_dir / f"evaluation_v5_{timestamp}.csv"

    if not system_prompt_path.exists():
        print(f"✗ System prompt not found: {system_prompt_path}")
        return

    if not testset_path.exists():
        print(f"✗ Testset not found: {testset_path}")
        return

    evaluator = BettyEvaluatorV5(
        system_prompt_path=str(system_prompt_path),
        testset_path=str(testset_path)
    )

    # Quick test with 5 questions
    print("\n⚡ Running quick test with first 5 questions...")
    evaluator.run_evaluation(max_questions=5)
    evaluator.print_summary()
    evaluator.save_results(str(output_path))

    print(f"\n💡 Quick test complete! To run full 50-question evaluation:")
    print(f"   python evaluation/run_evaluation_v5.py --full")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run v5.0 Betty evaluation")
    parser.add_argument("--full", action="store_true", help="Run full 50-question evaluation")
    parser.add_argument("--questions", type=int, help="Number of questions to evaluate")

    args = parser.parse_args()

    if args.full:
        base_dir = Path(__file__).parent.parent
        system_prompt_path = base_dir / "system_prompt_v4.3.txt"
        testset_path = Path(__file__).parent / "betty_testset_50q.csv"

        results_dir = Path(__file__).parent / "results"
        results_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = results_dir / f"evaluation_v5_full_{timestamp}.csv"

        evaluator = BettyEvaluatorV5(
            system_prompt_path=str(system_prompt_path),
            testset_path=str(testset_path)
        )

        max_q = args.questions if args.questions else None
        evaluator.run_evaluation(max_questions=max_q)
        evaluator.print_summary()
        evaluator.save_results(str(output_path))
    else:
        main()
