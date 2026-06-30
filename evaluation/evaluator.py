
# Evaluates CodeIS against a set of QA pairs.

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass, field

from rouge_score import rouge_scorer
from tqdm import tqdm

from generation.rag_engine import get_rag_engine
from config import QA_DIR
from utils.logger import get_logger

log = get_logger(__name__)

QA_FILE = QA_DIR / "qa_pairs.json"


# QA pair schema 

@dataclass
class QAPair:
    id:              str
    question:        str
    expected_answer: str
    expected_clauses: List[str]   
    part:            str           
    is_multi_hop:    bool = False


@dataclass
class EvalResult:
    qa_id:              str
    question:           str
    predicted_answer:   str
    expected_answer:    str
    rouge_l:            float
    clause_hit:         bool    
    clause_precision:   float   
    clause_recall:      float   
    hallucination_flag: bool    
    latency_s:          float


# Evaluator 

class Evaluator:
    HALLUCINATION_MARKERS = [
        "as per is 456",
        "as per is 800",
        "clause 7.2.3",    
        "i believe",
        "typically",
        "generally speaking",
        "in most cases",
    ]

    def __init__(self):
        self._engine  = get_rag_engine()
        self._scorer  = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)

    # Public API 

    def evaluate(
        self,
        qa_pairs: List[QAPair],
        output_file: Path | None = None,
    ) -> Dict[str, Any]:
        """
        Run evaluation over all QA pairs.
        Returns aggregate metrics and per-question results.
        """
        log.info(f"Starting evaluation on {len(qa_pairs)} QA pairs...")
        results: List[EvalResult] = []

        for qa in tqdm(qa_pairs, desc="Evaluating"):
            result = self._evaluate_single(qa)
            results.append(result)

        # Aggregate
        metrics = self._aggregate(results)
        metrics["per_question"] = [self._result_to_dict(r) for r in results]

        # Save
        if output_file:
            with open(output_file, "w") as f:
                json.dump(metrics, f, indent=2)
            log.success(f"Evaluation results saved to {output_file}")

        self._print_summary(metrics)
        return metrics

    def evaluate_from_file(self, qa_file: Path = QA_FILE) -> Dict[str, Any]:
        pairs = self.load_qa_pairs(qa_file)
        output = QA_DIR / "eval_results.json"
        return self.evaluate(pairs, output_file=output)

    # Single QA evaluation

    def _evaluate_single(self, qa: QAPair) -> EvalResult:
        try:
            response = self._engine.query(
                question   = qa.question,
                multi_hop  = qa.is_multi_hop,
                filter_part = qa.part if not qa.is_multi_hop else None,
            )
            predicted = response.answer
            retrieved_clauses = [
                c.get("metadata", {}).get("clause_number", "")
                for c in response.source_chunks
            ]
        except Exception as e:
            log.error(f"Query failed for QA {qa.id}: {e}")
            predicted         = ""
            retrieved_clauses = []

        rouge_l            = self._rouge_l(predicted, qa.expected_answer)
        clause_hit, cp, cr = self._clause_metrics(retrieved_clauses, qa.expected_clauses)
        hallucination      = self._is_hallucinated(predicted)

        return EvalResult(
            qa_id              = qa.id,
            question           = qa.question,
            predicted_answer   = predicted,
            expected_answer    = qa.expected_answer,
            rouge_l            = rouge_l,
            clause_hit         = clause_hit,
            clause_precision   = cp,
            clause_recall      = cr,
            hallucination_flag = hallucination,
            latency_s          = 0.0,
        )

    # Metrics

    def _rouge_l(self, predicted: str, expected: str) -> float:
        if not predicted or not expected:
            return 0.0
        scores = self._scorer.score(expected, predicted)
        return round(scores["rougeL"].fmeasure, 4)

    def _clause_metrics(
        self,
        retrieved: List[str],
        expected: List[str],
    ) -> tuple[bool, float, float]:
        if not expected:
            return True, 1.0, 1.0
        retrieved_set = set(r.strip() for r in retrieved if r)
        expected_set  = set(e.strip() for e in expected if e)
        hits          = retrieved_set & expected_set
        precision     = len(hits) / len(retrieved_set) if retrieved_set else 0.0
        recall        = len(hits) / len(expected_set)  if expected_set  else 0.0
        clause_hit    = bool(hits)
        return clause_hit, round(precision, 4), round(recall, 4)

    def _is_hallucinated(self, answer: str) -> bool:
        answer_lower = answer.lower()
        return any(m in answer_lower for m in self.HALLUCINATION_MARKERS)

    #  Aggregate 

    def _aggregate(self, results: List[EvalResult]) -> Dict[str, Any]:
        n = len(results)
        if n == 0:
            return {}
        return {
            "total_questions":          n,
            "avg_rouge_l":              round(sum(r.rouge_l for r in results) / n, 4),
            "clause_hit_rate":          round(sum(r.clause_hit for r in results) / n, 4),
            "avg_clause_precision":     round(sum(r.clause_precision for r in results) / n, 4),
            "avg_clause_recall":        round(sum(r.clause_recall for r in results) / n, 4),
            "hallucination_rate":       round(sum(r.hallucination_flag for r in results) / n, 4),
        }

    # Helpers 

    @staticmethod
    def load_qa_pairs(path: Path) -> List[QAPair]:
        if not path.exists():
            raise FileNotFoundError(
                f"QA file not found: {path}\n"
                "Run: python evaluation/generate_qa.py to create it."
            )
        with open(path) as f:
            raw = json.load(f)
        return [
            QAPair(
                id               = item["id"],
                question         = item["question"],
                expected_answer  = item["expected_answer"],
                expected_clauses = item.get("expected_clauses", []),
                part             = item.get("part", ""),
                is_multi_hop     = item.get("is_multi_hop", False),
            )
            for item in raw
        ]

    @staticmethod
    def _result_to_dict(r: EvalResult) -> dict:
        return {
            "id":               r.qa_id,
            "question":         r.question,
            "predicted":        r.predicted_answer[:300],
            "expected":         r.expected_answer[:300],
            "rouge_l":          r.rouge_l,
            "clause_hit":       r.clause_hit,
            "clause_precision": r.clause_precision,
            "clause_recall":    r.clause_recall,
            "hallucination":    r.hallucination_flag,
        }

    @staticmethod
    def _print_summary(metrics: Dict):
        log.info("=" * 50)
        log.info("EVALUATION SUMMARY")
        log.info("=" * 50)
        for k, v in metrics.items():
            if k != "per_question":
                log.info(f"  {k:35s}: {v}")
        log.info("=" * 50)


if __name__ == "__main__":
    evaluator = Evaluator()
    evaluator.evaluate_from_file()
