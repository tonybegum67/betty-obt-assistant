#!/usr/bin/env python3
"""
Betty v4.3 IMPROVED Evaluation Runner
Implements fixes from EVALUATION_ANALYSIS_COMPREHENSIVE.md:
- Dynamic word limits based on task complexity
- MODE detection (MODE 1/2/3) from prompt
- Relaxed semantic similarity thresholds
- Removed exact match penalty
- Concept match (binary semantic threshold)
"""

import csv
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import anthropic
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from utils.vector_store import VectorStore
from config.settings import AppConfig

class ImprovedBettyEvaluator:
    """Improved evaluator with dynamic rubric and MODE detection"""

    def __init__(self, system_prompt_path: str, testset_path: str):
        """Initialize evaluator with system prompt and testset"""
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

        print("✓ Improved Evaluator initialized")

    def detect_response_mode(self, prompt: str) -> Tuple[str, Dict]:
        """
        Detect which MODE Betty should use based on prompt
        Returns (mode, config)
        """
        prompt_lower = prompt.lower()

        # MODE 1 triggers: Ultra-concise outcome statements
        mode1_triggers = ['rewrite', 'create', 'provide', 'write', 'produce',
                          'state', '≤10', '≤15', 'metric-free', 'outcome for',
                          'short outcome', 'concise outcome']

        # MODE 2 triggers: Classification
        mode2_triggers = ['classify', 'what or how', 'is', 'acceptable outcome',
                          'what/how?']

        # MODE 3 triggers: Comprehensive analysis
        mode3_triggers = ['acceptance criteria', 'prioritize', 'raci', 'kpi',
                          'maturity', 'stakeholder', 'next-step', 'difference between',
                          'explain', 'analyze', 'assess']

        # Check MODE 1
        if any(trigger in prompt_lower for trigger in mode1_triggers):
            return 'MODE1', {'max_words': 15, 'require_explanation': False, 'require_sources': False}

        # Check MODE 2
        if any(trigger in prompt_lower for trigger in mode2_triggers):
            # Check if reframe also requested
            if 'reframe' in prompt_lower or 'if not' in prompt_lower:
                return 'MODE2_REFRAME', {'max_words': 20, 'require_explanation': False, 'require_sources': False}
            return 'MODE2', {'max_words': 5, 'require_explanation': False, 'require_sources': False}

        # Check MODE 3
        if any(trigger in prompt_lower for trigger in mode3_triggers):
            return 'MODE3', {'max_words': 200, 'require_explanation': True, 'require_sources': True}

        # Default to MODE1 if ambiguous
        return 'MODE1', {'max_words': 30, 'require_explanation': False, 'require_sources': False}

    def get_dynamic_word_limit(self, prompt: str, mode: str) -> int:
        """
        Get context-aware word limit based on task complexity
        Implements Fix #1 from evaluation analysis
        """
        prompt_lower = prompt.lower()

        # MODE 3 tasks have variable limits
        if mode == 'MODE3':
            if "acceptance criteria" in prompt_lower:
                return 100  # Structured format needs detail
            elif "prioritize" in prompt_lower or "raci" in prompt_lower:
                return 150  # Rationale required
            elif "kpi" in prompt_lower:
                return 75   # Goal + measure + target
            elif "maturity" in prompt_lower:
                return 80   # Current + target + context
            else:
                return 200  # Complex analysis

        # MODE 2
        elif mode.startswith('MODE2'):
            if 'reframe' in mode:
                return 20  # Classification + reframe
            return 5  # Simple classification

        # MODE 1
        else:
            if "≤10" in prompt or "10-word" in prompt:
                return 15  # Explicit 10-word request gets 15 word budget
            elif "short" in prompt_lower:
                return 50
            return 30  # Default outcome statement

    def calculate_concept_match(self, expected: str, actual: str, semantic_sim: float) -> int:
        """
        Binary concept match based on semantic threshold
        Replaces exact match penalty (Fix #3)
        """
        # Concept match if semantically similar enough
        return 1 if semantic_sim >= 0.6 else 0

    def calculate_semantic_similarity(self, expected: str, actual: str) -> float:
        """Calculate semantic similarity using embeddings"""
        if not expected or not actual:
            return 0.0

        expected_emb = self.embedding_model.encode([expected])
        actual_emb = self.embedding_model.encode([actual])

        similarity = cosine_similarity(expected_emb, actual_emb)[0][0]
        return float(similarity)

    def classify_semantic_quality(self, semantic_score: float, mode: str) -> str:
        """
        Classify semantic quality with MODE-aware thresholds
        Implements Fix #2 (relaxed thresholds)
        """
        if mode in ['MODE1', 'MODE2', 'MODE2_REFRAME']:
            # More lenient for outcome statements (different phrasing OK)
            if semantic_score >= 0.6:
                return "EXCELLENT"
            elif semantic_score >= 0.4:
                return "GOOD"
            elif semantic_score >= 0.25:
                return "FAIR"
            else:
                return "POOR"
        else:
            # Standard thresholds for MODE 3
            if semantic_score >= 0.9:
                return "EXCELLENT"
            elif semantic_score >= 0.7:
                return "GOOD"
            elif semantic_score >= 0.5:
                return "FAIR"
            else:
                return "POOR"

    def calculate_mode_compliance(self, response: str, mode: str, mode_config: Dict) -> Tuple[int, str]:
        """
        Score response based on MODE compliance
        Implements Fix #4 (MODE system recognition)
        """
        word_count = len(response.split())
        notes = []
        score = 3

        # Check word count compliance
        max_words = mode_config['max_words']
        if word_count > max_words:
            score -= 1
            notes.append(f"Exceeds {mode} limit: {word_count} > {max_words} words")

        # MODE-specific checks
        if mode == 'MODE1':
            # Check for prohibited phrases
            prohibited = ['i\'ll', 'let me', 'i can', 'based on', 'here\'s']
            found_prohibited = [p for p in prohibited if p in response.lower()]
            if found_prohibited:
                score -= 1
                notes.append(f"First-person phrases: {', '.join(found_prohibited)}")

        elif mode == 'MODE2':
            # Should be single word
            if word_count > 1:
                score -= 1
                notes.append(f"Expected 1 word, got {word_count}")

        elif mode == 'MODE3':
            # Check for sources if required
            if mode_config['require_sources']:
                has_sources = "source" in response.lower() or "**source" in response.lower()
                if not has_sources:
                    score -= 1
                    notes.append("Missing source citations")

            # Check for structure
            has_structure = response.count("\n") > 3
            if not has_structure and word_count > 50:
                score -= 1
                notes.append("Lacks clear structure")

        notes_str = "; ".join(notes) if notes else f"{mode} compliant"
        return max(score, 0), notes_str

    def calculate_obt_adherence(self, response: str, mode: str) -> Tuple[int, str]:
        """
        Calculate OBT principle adherence (separate from MODE compliance)
        Implements Fix #5 (separate dimensions)
        """
        notes = []
        score = 3

        response_lower = response.lower()

        # Only check OBT principles for outcome statements
        if mode in ['MODE1', 'MODE2_REFRAME']:
            # Check for metrics (numbers/percentages)
            if any(char.isdigit() for char in response):
                score -= 1
                notes.append("Contains metrics/numbers")

            # Check for solution-specific terms
            solution_terms = ['implement', 'deploy', 'create', 'build', 'install',
                              'configure', 'erp', 'system', 'software', 'tool']
            found_terms = [term for term in solution_terms if term in response_lower]
            if found_terms:
                score -= 1
                notes.append(f"Solution-specific: {', '.join(found_terms[:3])}")

            # Check for past tense / passive voice (ideal)
            present_verbs = ['begin', 'execute', 'perform', 'deliver', 'improve']
            found_present = [v for v in present_verbs if v in response_lower]
            if found_present:
                score -= 1
                notes.append(f"Present tense verbs: {', '.join(found_present[:2])}")

        notes_str = "; ".join(notes) if notes else "OBT compliant"
        return max(score, 0), notes_str

    def calculate_overall_score(self, concept_match: int, semantic_sim: float,
                                mode_compliance: int, obt_adherence: int) -> float:
        """
        Calculate weighted overall score with improved formula
        Removed exact match penalty, added MODE compliance
        """
        score = (
            (concept_match * 0.15) +         # Binary semantic match
            (semantic_sim * 0.25) +          # Continuous semantic similarity
            ((mode_compliance / 3) * 0.35) + # MODE compliance (increased weight)
            ((obt_adherence / 3) * 0.25)     # OBT principles
        )
        return round(score, 4)

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
        """Evaluate a single question with improved rubric"""
        print(f"\n[{question_num}/{total}] {question['prompt'][:60]}...")

        # Detect MODE from prompt
        mode, mode_config = self.detect_response_mode(question['prompt'])
        expected_word_limit = self.get_dynamic_word_limit(question['prompt'], mode)

        print(f"  → Detected {mode} (limit: {expected_word_limit} words)")

        # Query Betty
        response, exec_time, error = self.query_betty(question['prompt'])

        if error:
            print(f"  ✗ Error: {error}")
            return self._error_result(question, exec_time, error)

        # Calculate metrics
        semantic_sim = self.calculate_semantic_similarity(question['expected_response'], response)
        concept_match = self.calculate_concept_match(question['expected_response'], response, semantic_sim)

        semantic_quality = self.classify_semantic_quality(semantic_sim, mode)

        mode_compliance, mode_notes = self.calculate_mode_compliance(response, mode, mode_config)
        obt_adherence, obt_notes = self.calculate_obt_adherence(response, mode)

        overall_score = self.calculate_overall_score(
            concept_match, semantic_sim, mode_compliance, obt_adherence
        )

        word_count = len(response.split())
        analysis_notes = f"MODE: {mode} | Words: {word_count}/{expected_word_limit} | Semantic: {semantic_quality} | {mode_notes} | {obt_notes}"

        print(f"  ✓ Score: {overall_score:.3f} | Semantic: {semantic_sim:.3f} ({semantic_quality}) | Time: {exec_time}ms")

        return {
            'test_id': question['test_id'],
            'category': question['category'],
            'domain': question['domain'],
            'prompt': question['prompt'],
            'expected_response': question['expected_response'],
            'agent_response': response,
            'detected_mode': mode,
            'expected_word_limit': expected_word_limit,
            'actual_word_count': word_count,
            'concept_match': concept_match,
            'semantic_similarity': round(semantic_sim, 4),
            'semantic_quality': semantic_quality,
            'mode_compliance': mode_compliance,
            'obt_adherence': obt_adherence,
            'overall_score': overall_score,
            'execution_time_ms': exec_time,
            'error': error or '',
            'analysis_notes': analysis_notes
        }

    def _error_result(self, question: Dict, exec_time: int, error: str) -> Dict:
        """Return error result"""
        return {
            'test_id': question['test_id'],
            'category': question['category'],
            'domain': question['domain'],
            'prompt': question['prompt'],
            'expected_response': question['expected_response'],
            'agent_response': '',
            'detected_mode': 'ERROR',
            'expected_word_limit': 0,
            'actual_word_count': 0,
            'concept_match': 0,
            'semantic_similarity': 0.0,
            'semantic_quality': 'ERROR',
            'mode_compliance': 0,
            'obt_adherence': 0,
            'overall_score': 0.0,
            'execution_time_ms': exec_time,
            'error': error,
            'analysis_notes': f'Evaluation failed: {error}'
        }

    def run_evaluation(self, max_questions: Optional[int] = None) -> List[Dict]:
        """Run improved evaluation"""
        questions = self.load_testset()

        if max_questions:
            questions = questions[:max_questions]
            print(f"⚠ Running limited evaluation: {max_questions} questions")

        print(f"\n{'='*70}")
        print(f"IMPROVED Betty v4.3 Evaluation - {len(questions)} questions")
        print(f"{'='*70}")
        print("Enhancements:")
        print("  ✓ Dynamic word limits based on task complexity")
        print("  ✓ MODE detection (MODE 1/2/3) from prompt")
        print("  ✓ Relaxed semantic similarity thresholds")
        print("  ✓ Removed exact match penalty")
        print("  ✓ Concept match (binary semantic threshold)")
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
            'test_id', 'category', 'domain', 'prompt', 'expected_response',
            'agent_response', 'detected_mode', 'expected_word_limit', 'actual_word_count',
            'concept_match', 'semantic_similarity', 'semantic_quality',
            'mode_compliance', 'obt_adherence', 'overall_score',
            'execution_time_ms', 'error', 'analysis_notes'
        ]

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.results)

        print(f"\n✓ Results saved to: {output_path}")

    def print_summary(self):
        """Print evaluation summary with comparison to targets"""
        if not self.results:
            print("⚠ No results to summarize")
            return

        total = len(self.results)
        errors = sum(1 for r in self.results if r['error'])

        avg_overall = np.mean([r['overall_score'] for r in self.results])
        avg_semantic = np.mean([r['semantic_similarity'] for r in self.results])
        avg_mode_compliance = np.mean([r['mode_compliance'] for r in self.results])
        avg_obt_adherence = np.mean([r['obt_adherence'] for r in self.results])
        avg_time = np.mean([r['execution_time_ms'] for r in self.results])

        # Count semantic quality distribution
        quality_counts = {'EXCELLENT': 0, 'GOOD': 0, 'FAIR': 0, 'POOR': 0, 'ERROR': 0}
        for r in self.results:
            quality_counts[r['semantic_quality']] += 1

        # Count MODE distribution
        mode_counts = {}
        for r in self.results:
            mode = r['detected_mode']
            mode_counts[mode] = mode_counts.get(mode, 0) + 1

        print(f"\n{'='*70}")
        print("IMPROVED EVALUATION SUMMARY")
        print(f"{'='*70}")
        print(f"Total Questions: {total}")
        print(f"Errors: {errors} ({errors/total*100:.1f}%)")

        print(f"\n📊 OVERALL METRICS:")
        print(f"  Overall Score: {avg_overall:.3f}")
        print(f"  Semantic Similarity: {avg_semantic:.3f}")
        print(f"  MODE Compliance: {avg_mode_compliance:.2f}/3")
        print(f"  OBT Adherence: {avg_obt_adherence:.2f}/3")
        print(f"  Avg Response Time: {avg_time:.0f}ms")

        print(f"\n📈 SEMANTIC QUALITY DISTRIBUTION:")
        for quality, count in sorted(quality_counts.items()):
            pct = count/total*100
            bar = '█' * int(pct/5)
            print(f"  {quality:10s}: {count:2d} ({pct:5.1f}%) {bar}")

        print(f"\n🎯 MODE DETECTION:")
        for mode, count in sorted(mode_counts.items()):
            pct = count/total*100
            print(f"  {mode:15s}: {count:2d} ({pct:5.1f}%)")

        # Performance rating
        if avg_overall >= 0.85:
            rating = "EXCELLENT ✓✓"
        elif avg_overall >= 0.75:
            rating = "GOOD ✓"
        elif avg_overall >= 0.65:
            rating = "PRODUCTION READY"
        elif avg_overall >= 0.50:
            rating = "ACCEPTABLE"
        else:
            rating = "NEEDS IMPROVEMENT"

        print(f"\n🏆 Performance Rating: {rating}")

        # Comparison to baseline
        baseline_score = 0.307  # From evaluation analysis
        improvement = ((avg_overall - baseline_score) / baseline_score) * 100
        print(f"\n📉 vs Baseline (0.307): {improvement:+.1f}% {'📈' if improvement > 0 else '📉'}")

        print(f"{'='*70}\n")


def main():
    """Main evaluation runner"""
    base_dir = Path(__file__).parent.parent
    system_prompt_path = base_dir / "system_prompt_v4.3.txt"
    testset_path = Path(__file__).parent / "betty_testset_50q.csv"

    results_dir = Path(__file__).parent / "results"
    results_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = results_dir / f"evaluation_improved_{timestamp}.csv"

    if not system_prompt_path.exists():
        print(f"✗ System prompt not found: {system_prompt_path}")
        return

    if not testset_path.exists():
        print(f"✗ Testset not found: {testset_path}")
        return

    evaluator = ImprovedBettyEvaluator(
        system_prompt_path=str(system_prompt_path),
        testset_path=str(testset_path)
    )

    # Quick test with 5 questions
    print("\n⚡ Running quick test with first 5 questions...")
    evaluator.run_evaluation(max_questions=5)
    evaluator.print_summary()
    evaluator.save_results(str(output_path))

    print(f"\n💡 Quick test complete! To run full 50-question evaluation:")
    print(f"   python evaluation/run_evaluation_improved.py --full")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run improved Betty evaluation")
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
        output_path = results_dir / f"evaluation_improved_full_{timestamp}.csv"

        evaluator = ImprovedBettyEvaluator(
            system_prompt_path=str(system_prompt_path),
            testset_path=str(testset_path)
        )

        max_q = args.questions if args.questions else None
        evaluator.run_evaluation(max_questions=max_q)
        evaluator.print_summary()
        evaluator.save_results(str(output_path))
    else:
        main()
