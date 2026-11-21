"""
Academia–Industry Skill Matcher.
Compares academic curriculum skills with industry job requirements.
Identifies Exact matches, Semantic/Related matches, and Unmapped requirements.
"""

from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class SkillMatcher:
    def __init__(self, semantic_threshold: float = 0.50):
        self.semantic_threshold = semantic_threshold

    def calculate_semantic_similarity(self, text_a: str, text_b: str) -> float:
        """Calculate TF-IDF cosine similarity between two skill descriptions/names."""
        if not text_a or not text_b:
            return 0.0
        
        try:
            vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
            tfidf_matrix = vectorizer.fit_transform([text_a, text_b])
            sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(np.round(sim, 3))
        except Exception:
            # Fallback to Jaccard word set similarity
            tokens_a = set(text_a.lower().split())
            tokens_b = set(text_b.lower().split())
            intersection = tokens_a.intersection(tokens_b)
            union = tokens_a.union(tokens_b)
            return float(len(intersection) / len(union)) if union else 0.0

    def match_curriculum_to_job(
        self,
        academic_skills: List[Dict[str, Any]],
        job_skills: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Compare academic course skills against job required skills.
        
        Returns:
            - matched_pairs: List of mapped skill relationships
            - unmapped_job_skills: Industry skills missing from academia
            - curriculum_coverage_pct: Overall percentage of job skills covered
        """
        academic_by_name = {s["canonical_name"].lower(): s for s in academic_skills}
        
        matched_pairs = []
        unmapped_job_skills = []
        total_weight = 0.0
        covered_weight = 0.0

        for js in job_skills:
            job_skill_name = js["canonical_name"]
            weight = js.get("importance_weight", 3.0)
            total_weight += weight
            
            # 1. Exact match check
            if job_skill_name.lower() in academic_by_name:
                matched_pairs.append({
                    "job_skill": job_skill_name,
                    "academic_skill": job_skill_name,
                    "mapping_type": "exact",
                    "confidence": 1.0,
                    "importance_weight": weight,
                    "course_info": academic_by_name[job_skill_name.lower()].get("course_code", "Curriculum")
                })
                covered_weight += weight * 1.0
                continue

            # 2. Semantic / Related match check
            best_semantic_match = None
            best_sim_score = 0.0

            for acad_name, acad_skill in academic_by_name.items():
                # Form composite string for semantic comparison
                sim = self.calculate_semantic_similarity(
                    f"{job_skill_name} {js.get('category', '')}",
                    f"{acad_name} {acad_skill.get('category', '')}"
                )
                if sim > best_sim_score:
                    best_sim_score = sim
                    best_semantic_match = acad_skill

            if best_sim_score >= self.semantic_threshold:
                matched_pairs.append({
                    "job_skill": job_skill_name,
                    "academic_skill": best_semantic_match["canonical_name"],
                    "mapping_type": "semantic",
                    "confidence": best_sim_score,
                    "importance_weight": weight,
                    "course_info": best_semantic_match.get("course_code", "Curriculum")
                })
                # Related matches contribute partial coverage (0.5)
                covered_weight += weight * 0.5
            else:
                unmapped_job_skills.append({
                    "job_skill": job_skill_name,
                    "importance_weight": weight,
                    "category": js.get("category", "General"),
                    "required_proficiency": js.get("required_proficiency", "intermediate")
                })

        # Calculate coverage percentages
        num_required = len(job_skills)
        num_covered = len(matched_pairs)
        unweighted_cov = round((num_covered / num_required * 100), 2) if num_required > 0 else 0.0
        weighted_cov = round((covered_weight / total_weight * 100), 2) if total_weight > 0 else 0.0

        return {
            "matched_pairs": matched_pairs,
            "unmapped_job_skills": unmapped_job_skills,
            "unweighted_coverage": unweighted_cov,
            "weighted_coverage": weighted_cov,
            "total_job_skills": num_required,
            "covered_job_skills": num_covered
        }

default_matcher = SkillMatcher()
