"""
NLP and Skill Intelligence Package.
"""
from backend.app.nlp.taxonomy import CANONICAL_SKILLS, get_canonical_skill_by_name
from backend.app.nlp.extractor import SkillExtractor, default_extractor
from backend.app.nlp.matcher import SkillMatcher, default_matcher
from backend.app.nlp.gap_analyzer import SkillGapAnalyzer, default_gap_analyzer
from backend.app.nlp.evaluator import ModelEvaluator, default_evaluator

__all__ = [
    "CANONICAL_SKILLS",
    "get_canonical_skill_by_name",
    "SkillExtractor",
    "default_extractor",
    "SkillMatcher",
    "default_matcher",
    "SkillGapAnalyzer",
    "default_gap_analyzer",
    "ModelEvaluator",
    "default_evaluator"
]
