import pytest
from backend.app.nlp.evaluator import default_evaluator, GROUND_TRUTH_DATASET

def test_ground_truth_dataset_integrity():
    assert len(GROUND_TRUTH_DATASET) >= 5
    for sample in GROUND_TRUTH_DATASET:
        assert "id" in sample
        assert "text" in sample
        assert "ground_truth_skills" in sample
        assert len(sample["ground_truth_skills"]) > 0

def test_model_evaluation_metrics_validity():
    result = default_evaluator.evaluate_extraction_on_dataset()

    nlp = result["proposed_nlp_pipeline"]
    assert 0.0 <= nlp["precision"] <= 1.0
    assert 0.0 <= nlp["recall"] <= 1.0
    assert 0.0 <= nlp["f1_score"] <= 1.0
    assert nlp["true_positives"] > 0

    base = result["keyword_baseline"]
    assert 0.0 <= base["precision"] <= 1.0
    assert 0.0 <= base["recall"] <= 1.0
    assert 0.0 <= base["f1_score"] <= 1.0

    # The NLP pipeline with word boundary guards and synonyms should achieve higher precision/F1
    assert nlp["f1_score"] >= base["f1_score"]
    assert "error_samples" in result
