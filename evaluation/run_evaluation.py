#!/usr/bin/env python3
"""
Betty v4.3 Local Evaluation Runner
Executes the 50-question testset and generates scoring metrics optimized for v4.3 MODE system
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

class BettyEvaluator:
    """Evaluates Betty's responses against the testset"""

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
            # Try loading from Streamlit secrets
            try:
                import streamlit as st
                api_key = st.secrets["ANTHROPIC_API_KEY"]
            except:
                raise ValueError("ANTHROPIC_API_KEY not found in environment or Streamlit secrets")
        self.client = anthropic.Anthropic(api_key=api_key)

        # Initialize embedding model for semantic similarity
        print("Loading embedding model...")
        self.embedding_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

        # Initialize vector store for RAG
        print("Loading vector store...")
        self.vector_store = VectorStore()

        print("✓ Evaluator initialized")

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
        """Query Betty with a prompt and return response, execution time, and error"""
        start_time = time.time()

        try:
            # Get relevant context from RAG if enabled
            context = ""
            if use_rag:
                search_results = self.vector_store.search_collection(
                    collection_name=AppConfig.KNOWLEDGE_COLLECTION_NAME,
                    query=prompt,
                    n_results=8
                )
                if search_results and len(search_results) > 0:
                    # Extract document text from search results
                    context_docs = [doc['document'] for doc in search_results if 'document' in doc]
                    context = "\n\n".join([f"Context {i+1}:\n{doc}" for i, doc in enumerate(context_docs)])

            # Build full prompt with context
            full_prompt = prompt
            if context:
                full_prompt = f"Relevant context from knowledge base:\n\n{context}\n\n---\n\nUser question: {prompt}"

            # Query Claude with Betty's system prompt
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

    def calculate_exact_match(self, expected: str, actual: str) -> int:
        """Calculate exact match (0 or 1)"""
        return 1 if expected.strip().lower() == actual.strip().lower() else 0

    def calculate_semantic_similarity(self, expected: str, actual: str) -> float:
        """Calculate semantic similarity using embeddings"""
        if not expected or not actual:
            return 0.0

        # Generate embeddings
        expected_emb = self.embedding_model.encode([expected])
        actual_emb = self.embedding_model.encode([actual])

        # Calculate cosine similarity
        similarity = cosine_similarity(expected_emb, actual_emb)[0][0]
        return float(similarity)

    def calculate_rubric_precision(self, expected: str, actual: str, target: int) -> Tuple[int, str]:
        """
        Calculate rubric precision score (0-3)
        Evaluates length accuracy and concept precision
        """
        expected_words = len(expected.split())
        actual_words = len(actual.split())
        word_diff = abs(expected_words - actual_words)

        # Length precision
        if word_diff <= 2:
            length_score = 3
        elif word_diff <= 5:
            length_score = 2
        elif word_diff <= 15:
            length_score = 1
        else:
            length_score = 0

        # Concept precision (simple keyword overlap)
        expected_keywords = set(expected.lower().split())
        actual_keywords = set(actual.lower().split())

        if len(expected_keywords) > 0:
            overlap = len(expected_keywords & actual_keywords) / len(expected_keywords)
        else:
            overlap = 0.0

        if overlap >= 0.9:
            concept_score = 3
        elif overlap >= 0.7:
            concept_score = 2
        elif overlap >= 0.5:
            concept_score = 1
        else:
            concept_score = 0

        # Average the scores
        precision_score = (length_score + concept_score) // 2

        notes = f"Length: {actual_words} vs {expected_words} words (diff: {word_diff}), Concept overlap: {overlap:.2%}"

        return precision_score, notes

    def calculate_rubric_adherence(self, response: str, category: str) -> Tuple[int, str]:
        """
        Calculate rubric adherence score (0-3) optimized for v4.3 MODE system
        Checks OBT compliance rules with MODE-aware expectations
        """
        notes = []
        violations = 0

        # v4.3 MODE 1 & 2: Expect CONCISE responses
        if category in ['outcome_rewriting', 'classification']:
            word_count = len(response.split())

            # MODE 1 (outcome_rewriting): ≤15 words total for ≤10-word requests
            if category == 'outcome_rewriting':
                if word_count > 15:
                    violations += 1
                    notes.append(f"Word count: {word_count} > 15 (MODE 1 violation)")

            # MODE 2 (classification): ≤3 words for classification
            elif category == 'classification':
                if word_count > 5:
                    violations += 1
                    notes.append(f"Word count: {word_count} > 5 (MODE 2 violation)")

        # Check for metrics in outcome statements
        if category in ['outcome_rewriting']:
            if any(char.isdigit() for char in response):
                violations += 1
                notes.append("Contains numbers/metrics")

        # Check for How verbs
        how_verbs = ['implement', 'deploy', 'create', 'build', 'install', 'configure']
        response_lower = response.lower()
        found_how_verbs = [verb for verb in how_verbs if verb in response_lower]
        if found_how_verbs and category == 'outcome_rewriting':
            violations += 1
            notes.append(f"How verbs: {', '.join(found_how_verbs)}")

        # Score based on violations
        if violations == 0:
            score = 3
        elif violations <= 2:
            score = 2
        elif violations <= 4:
            score = 1
        else:
            score = 0

        notes_str = "; ".join(notes) if notes else "No OBT violations"

        return score, notes_str

    def calculate_rubric_explanation(self, response: str, category: str = None) -> Tuple[int, str]:
        """
        Calculate rubric explanation score (0-3) optimized for v4.3 MODE system
        MODE 1 & 2 responses are concise by design - don't penalize brevity
        """
        word_count = len(response.split())

        # v4.3 MODE 1 & 2: Concise answers don't need justification
        if category in ['outcome_rewriting', 'classification']:
            # For MODE responses, conciseness is correct behavior
            if word_count <= 15:
                score = 3
                notes = "Concise MODE response (correct)"
            else:
                # Longer responses should have justification
                has_reasoning = any(word in response.lower() for word in ['because', 'since', 'therefore', 'thus', 'why'])
                has_evidence = any(word in response.lower() for word in ['data', 'source', 'level', 'measure', 'evidence'])

                if has_reasoning and has_evidence:
                    score = 2
                    notes = "Adequate explanation (verbose)"
                else:
                    score = 1
                    notes = "Verbose without justification"
        else:
            # For other categories, use traditional rubric
            has_reasoning = any(word in response.lower() for word in ['because', 'since', 'therefore', 'thus', 'why'])
            has_evidence = any(word in response.lower() for word in ['data', 'source', 'level', 'measure', 'evidence'])

            if has_reasoning and has_evidence and word_count > 20:
                score = 3
                notes = "Clear justification with evidence"
            elif has_reasoning or has_evidence:
                score = 2
                notes = "Adequate explanation"
            elif word_count > 10:
                score = 1
                notes = "Minimal reasoning"
            else:
                score = 0
                notes = "No justification"

        return score, notes

    def calculate_overall_score(self, exact_match: int, semantic_sim: float,
                               precision: int, adherence: int, explanation: int) -> float:
        """Calculate weighted overall score"""
        score = (
            (exact_match * 0.15) +
            (semantic_sim * 0.25) +
            ((precision / 3) * 0.20) +
            ((adherence / 3) * 0.25) +
            ((explanation / 3) * 0.15)
        )
        return round(score, 4)

    def evaluate_question(self, question: Dict, question_num: int, total: int) -> Dict:
        """Evaluate a single question"""
        print(f"\n[{question_num}/{total}] Evaluating: {question['prompt'][:60]}...")

        # Query Betty
        response, exec_time, error = self.query_betty(question['prompt'])

        if error:
            print(f"  ✗ Error: {error}")
            return {
                'test_id': question['test_id'],
                'category': question['category'],
                'domain': question['domain'],
                'prompt': question['prompt'],
                'expected_response': question['expected_response'],
                'agent_response': '',
                'exact_match': 0,
                'semantic_similarity': 0.0,
                'rubric_precision': 0,
                'rubric_adherence': 0,
                'rubric_explanation': 0,
                'overall_score': 0.0,
                'execution_time_ms': exec_time,
                'error': error,
                'analysis_notes': f'Evaluation failed: {error}'
            }

        # Calculate metrics
        exact_match = self.calculate_exact_match(question['expected_response'], response)
        semantic_sim = self.calculate_semantic_similarity(question['expected_response'], response)

        try:
            precision_target = int(question.get('rubric_precision_target', 2))
        except (ValueError, TypeError):
            precision_target = 2  # Default if parsing fails

        precision_score, precision_notes = self.calculate_rubric_precision(
            question['expected_response'], response, precision_target
        )

        adherence_score, adherence_notes = self.calculate_rubric_adherence(
            response, question['category']
        )

        explanation_score, explanation_notes = self.calculate_rubric_explanation(
            response, question['category']
        )

        overall_score = self.calculate_overall_score(
            exact_match, semantic_sim, precision_score, adherence_score, explanation_score
        )

        # Compile analysis notes
        analysis_notes = f"Precision: {precision_notes} | Adherence: {adherence_notes} | Explanation: {explanation_notes}"

        print(f"  ✓ Score: {overall_score:.3f} | Semantic: {semantic_sim:.3f} | Time: {exec_time}ms")

        return {
            'test_id': question['test_id'],
            'category': question['category'],
            'domain': question['domain'],
            'prompt': question['prompt'],
            'expected_response': question['expected_response'],
            'agent_response': response,
            'exact_match': exact_match,
            'semantic_similarity': round(semantic_sim, 4),
            'rubric_precision': precision_score,
            'rubric_adherence': adherence_score,
            'rubric_explanation': explanation_score,
            'overall_score': overall_score,
            'execution_time_ms': exec_time,
            'error': error or '',
            'analysis_notes': analysis_notes
        }

    def run_evaluation(self, max_questions: Optional[int] = None) -> List[Dict]:
        """Run full evaluation"""
        questions = self.load_testset()

        if max_questions:
            questions = questions[:max_questions]
            print(f"⚠ Running limited evaluation: {max_questions} questions")

        print(f"\n{'='*70}")
        print(f"Starting Betty v4.3 Evaluation - {len(questions)} questions")
        print(f"{'='*70}")

        results = []
        for i, question in enumerate(questions, 1):
            result = self.evaluate_question(question, i, len(questions))
            results.append(result)

            # Brief pause to avoid rate limiting
            time.sleep(0.5)

        self.results = results
        return results

    def save_results(self, output_path: str):
        """Save results to CSV"""
        if not self.results:
            print("⚠ No results to save")
            return

        fieldnames = [
            'test_id', 'category', 'domain', 'prompt', 'expected_response',
            'agent_response', 'exact_match', 'semantic_similarity',
            'rubric_precision', 'rubric_adherence', 'rubric_explanation',
            'overall_score', 'execution_time_ms', 'error', 'analysis_notes'
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
        avg_semantic = np.mean([r['semantic_similarity'] for r in self.results])
        avg_precision = np.mean([r['rubric_precision'] for r in self.results])
        avg_adherence = np.mean([r['rubric_adherence'] for r in self.results])
        avg_explanation = np.mean([r['rubric_explanation'] for r in self.results])
        avg_time = np.mean([r['execution_time_ms'] for r in self.results])

        print(f"\n{'='*70}")
        print("EVALUATION SUMMARY")
        print(f"{'='*70}")
        print(f"Total Questions: {total}")
        print(f"Errors: {errors} ({errors/total*100:.1f}%)")
        print(f"\nOverall Score: {avg_overall:.3f}")
        print(f"  - Semantic Similarity: {avg_semantic:.3f}")
        print(f"  - Rubric Precision: {avg_precision:.2f}/3")
        print(f"  - Rubric Adherence: {avg_adherence:.2f}/3")
        print(f"  - Rubric Explanation: {avg_explanation:.2f}/3")
        print(f"\nAvg Response Time: {avg_time:.0f}ms")

        # Performance rating
        if avg_overall >= 0.85:
            rating = "EXCELLENT ✓"
        elif avg_overall >= 0.75:
            rating = "GOOD"
        elif avg_overall >= 0.65:
            rating = "ACCEPTABLE"
        else:
            rating = "NEEDS IMPROVEMENT"

        print(f"\nPerformance Rating: {rating}")
        print(f"{'='*70}\n")


def main():
    """Main evaluation runner"""
    # Paths
    base_dir = Path(__file__).parent.parent
    system_prompt_path = base_dir / "system_prompt_v4.3.txt"
    testset_path = Path(__file__).parent / "betty_testset_50q.csv"

    # Create results directory
    results_dir = Path(__file__).parent / "results"
    results_dir.mkdir(exist_ok=True)

    # Output file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = results_dir / f"evaluation_{timestamp}.csv"

    # Check if files exist
    if not system_prompt_path.exists():
        print(f"✗ System prompt not found: {system_prompt_path}")
        return

    if not testset_path.exists():
        print(f"✗ Testset not found: {testset_path}")
        return

    # Initialize evaluator
    evaluator = BettyEvaluator(
        system_prompt_path=str(system_prompt_path),
        testset_path=str(testset_path)
    )

    # Run evaluation
    # Start with first 5 questions for testing, then run full 50
    print("\n⚡ Running quick test with first 5 questions...")
    evaluator.run_evaluation(max_questions=5)
    evaluator.print_summary()
    evaluator.save_results(str(output_path))

    print(f"\n💡 Quick test complete! To run full 50-question evaluation, use:")
    print(f"   python evaluation/run_evaluation.py --full")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run Betty evaluation")
    parser.add_argument("--full", action="store_true", help="Run full 50-question evaluation")
    parser.add_argument("--questions", type=int, help="Number of questions to evaluate")

    args = parser.parse_args()

    if args.full:
        # Run full evaluation
        base_dir = Path(__file__).parent.parent
        system_prompt_path = base_dir / "system_prompt_v4.3.txt"
        testset_path = Path(__file__).parent / "betty_testset_50q.csv"

        results_dir = Path(__file__).parent / "results"
        results_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = results_dir / f"evaluation_full_{timestamp}.csv"

        evaluator = BettyEvaluator(
            system_prompt_path=str(system_prompt_path),
            testset_path=str(testset_path)
        )

        max_q = args.questions if args.questions else None
        evaluator.run_evaluation(max_questions=max_q)
        evaluator.print_summary()
        evaluator.save_results(str(output_path))
    else:
        main()
