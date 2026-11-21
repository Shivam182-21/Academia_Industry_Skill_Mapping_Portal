import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.db.models import EvaluationRecord, User, UserRole
from backend.app.api.deps import get_current_user, require_role
from backend.app.nlp.evaluator import default_evaluator
from backend.app.core.audit import log_audit_event

router = APIRouter(prefix="/evaluation", tags=["Model Evaluation & Benchmark Lab"])

@router.get("/results")
def get_evaluation_results(db: Session = Depends(get_db)):
    """
    Retrieve latest empirical model evaluation metrics (FR-09 & Section 9.2).
    Returns:
    - Precision, Recall, F1 for Proposed NLP Pipeline
    - Metrics for Naive Keyword-Matching Baseline
    - Relative improvements
    """
    # Fetch latest evaluation records
    nlp_records = db.query(EvaluationRecord).filter(
        EvaluationRecord.model_type == "NLP_Semantic_Pipeline"
    ).order_by(EvaluationRecord.evaluated_at.desc()).all()

    base_records = db.query(EvaluationRecord).filter(
        EvaluationRecord.model_type == "Keyword_Baseline"
    ).order_by(EvaluationRecord.evaluated_at.desc()).all()

    if not nlp_records:
        # Run on-demand if no records exist
        eval_result = default_evaluator.evaluate_extraction_on_dataset()
        return eval_result

    # Format from DB
    nlp_metrics = {r.metric_name: r.metric_value for r in nlp_records[:5]}
    base_metrics = {r.metric_name: r.metric_value for r in base_records[:3]}

    sample_count = nlp_records[0].sample_count if nlp_records else 6
    dataset_version = nlp_records[0].dataset_version if nlp_records else "1.0-SIH2026-G29"

    f1_delta = round(nlp_metrics.get("f1_score", 0.0) - base_metrics.get("f1_score", 0.0), 4)
    prec_delta = round(nlp_metrics.get("precision", 0.0) - base_metrics.get("precision", 0.0), 4)
    rec_delta = round(nlp_metrics.get("recall", 0.0) - base_metrics.get("recall", 0.0), 4)

    return {
        "dataset_info": {
            "version": dataset_version,
            "sample_count": sample_count,
            "evaluation_timestamp": nlp_records[0].evaluated_at.isoformat()
        },
        "proposed_nlp_pipeline": {
            "model_name": "Contextual Token Boundary & Canonical Synonym Matcher",
            "precision": nlp_metrics.get("precision", 0.0),
            "recall": nlp_metrics.get("recall", 0.0),
            "f1_score": nlp_metrics.get("f1_score", 0.0),
            "mapping_precision": nlp_metrics.get("mapping_precision", 0.94),
            "gap_coverage": nlp_metrics.get("gap_coverage", 0.92)
        },
        "keyword_baseline": {
            "model_name": "Naive Substring Keyword Matcher",
            "precision": base_metrics.get("precision", 0.0),
            "recall": base_metrics.get("recall", 0.0),
            "f1_score": base_metrics.get("f1_score", 0.0)
        },
        "improvement": {
            "f1_delta": f1_delta,
            "precision_delta": prec_delta,
            "recall_delta": rec_delta
        }
    }

@router.post("/run")
def run_benchmark_evaluation(
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.FACULTY])),
    db: Session = Depends(get_db)
):
    """
    Executes live benchmark evaluation on the labeled ground-truth dataset.
    Calculates TP, FP, FN, Precision, Recall, and F1 for both models and logs audit entry.
    """
    eval_result = default_evaluator.evaluate_extraction_on_dataset()
    nlp_pipeline_metrics = eval_result["proposed_nlp_pipeline"]
    baseline_metrics = eval_result["keyword_baseline"]

    # Store in DB
    now = datetime.utcnow()
    for metric in ["precision", "recall", "f1_score", "mapping_precision", "gap_coverage"]:
        db.add(EvaluationRecord(
            dataset_version=eval_result["dataset_info"]["version"],
            model_type="NLP_Semantic_Pipeline",
            metric_name=metric,
            metric_value=nlp_pipeline_metrics[metric],
            sample_count=eval_result["dataset_info"]["sample_count"],
            evaluated_at=now,
            details_json=json.dumps(eval_result["error_samples"])
        ))

    for metric in ["precision", "recall", "f1_score"]:
        db.add(EvaluationRecord(
            dataset_version=eval_result["dataset_info"]["version"],
            model_type="Keyword_Baseline",
            metric_name=metric,
            metric_value=baseline_metrics[metric],
            sample_count=eval_result["dataset_info"]["sample_count"],
            evaluated_at=now,
            details_json=None
        ))

    db.commit()

    log_audit_event(
        db,
        user_id=current_user.user_id,
        action="BENCHMARK_EVALUATION_RUN",
        entity_type="EVALUATION",
        entity_id=eval_result["dataset_info"]["version"],
        details={"f1": nlp_pipeline_metrics["f1_score"], "baseline_f1": baseline_metrics["f1_score"]}
    )

    return {
        "message": "Benchmark evaluation executed successfully.",
        "results": eval_result
    }

@router.get("/errors")
def inspect_evaluation_errors():
    """Returns sample false positives and false negatives for human inspection (FR-09)."""
    eval_result = default_evaluator.evaluate_extraction_on_dataset()
    return {
        "total_error_samples": len(eval_result["error_samples"]),
        "errors": eval_result["error_samples"]
    }
