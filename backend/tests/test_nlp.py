import pytest
from backend.app.nlp.extractor import default_extractor
from backend.app.nlp.taxonomy import get_canonical_skill_by_name

def test_canonical_skill_lookup():
    item = get_canonical_skill_by_name("python")
    assert item is not None
    assert item["canonical_name"] == "Python"

    item_alias = get_canonical_skill_by_name("js")
    assert item_alias is not None
    assert item_alias["canonical_name"] == "JavaScript"

def test_skill_extraction_simple():
    text = "We teach Python programming, data structures, and database management with SQL."
    extracted = default_extractor.extract_skills(text)
    extracted_names = [e["canonical_name"] for e in extracted]
    
    assert "Python" in extracted_names
    assert "Data Structures & Algorithms" in extracted_names
    assert "SQL & Relational Databases" in extracted_names

def test_word_boundary_guards():
    # Should not match "js" inside words like "adjust" or "json"
    text = "Please adjust the settings and download the json file."
    extracted = default_extractor.extract_skills(text)
    extracted_names = [e["canonical_name"] for e in extracted]
    assert "JavaScript" not in extracted_names

def test_context_snippet_generation():
    text = "Students will construct web services using FastAPI and deploy them inside Docker containers."
    extracted = default_extractor.extract_skills(text)
    fastapi_match = next((e for e in extracted if e["canonical_name"] == "FastAPI"), None)
    assert fastapi_match is not None
    assert "FastAPI" in fastapi_match["evidence_snippet"]
    assert fastapi_match["confidence"] >= 0.85
