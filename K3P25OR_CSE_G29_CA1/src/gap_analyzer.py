"""
Student Skill-Gap Analysis & Learning Recommendation Engine.
Implements unweighted & weighted coverage formulas and gap-targeted resource ranking.
"""

from typing import List, Dict, Any

class SkillGapAnalyzer:
    @staticmethod
    def analyze_student_gap(
        job_skills: List[Dict[str, Any]],
        student_skills: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze gaps between target job role requirements and student verified skills.
        
        Args:
            job_skills: List of dicts with keys: canonical_name, importance_weight, required_proficiency
            student_skills: List of dicts with keys: canonical_name, proficiency_level, evidence_source, verified
        
        Returns:
            Dict containing coverage metrics, categorized skills, and overall gap scores.
        """
        student_skill_map = {
            s["canonical_name"].lower(): s for s in student_skills
        }
        
        demonstrated = []
        partially_demonstrated = []
        missing = []

        total_weight = 0.0
        covered_weight = 0.0
        covered_count = 0

        for js in job_skills:
            skill_name = js["canonical_name"]
            weight = float(js.get("importance_weight", 3.0))
            required_prof = js.get("required_proficiency", "intermediate").lower()
            total_weight += weight

            student_record = student_skill_map.get(skill_name.lower())

            if student_record:
                student_prof = student_record.get("proficiency_level", "intermediate").lower()
                is_verified = student_record.get("verified", False)
                evidence = student_record.get("evidence_source", "coursework")

                # Proficiency levels: beginner < intermediate < advanced
                prof_scores = {"beginner": 1, "intermediate": 2, "advanced": 3}
                student_score = prof_scores.get(student_prof, 1)
                required_score = prof_scores.get(required_prof, 2)

                if student_score >= required_score:
                    # Fully demonstrated
                    c_i = 1.0
                    demonstrated.append({
                        "canonical_name": skill_name,
                        "category": js.get("category", "General"),
                        "importance_weight": weight,
                        "student_proficiency": student_prof,
                        "required_proficiency": required_prof,
                        "evidence_source": evidence,
                        "verified": is_verified,
                        "coverage_score": c_i
                    })
                    covered_weight += weight * c_i
                    covered_count += 1
                else:
                    # Partially demonstrated (proficiency below target or unverified)
                    c_i = 0.5
                    partially_demonstrated.append({
                        "canonical_name": skill_name,
                        "category": js.get("category", "General"),
                        "importance_weight": weight,
                        "student_proficiency": student_prof,
                        "required_proficiency": required_prof,
                        "evidence_source": evidence,
                        "verified": is_verified,
                        "coverage_score": c_i
                    })
                    covered_weight += weight * c_i
                    # Count partial as 0.5 in unweighted count
                    covered_count += 0.5
            else:
                # Completely missing
                c_i = 0.0
                missing.append({
                    "canonical_name": skill_name,
                    "category": js.get("category", "General"),
                    "importance_weight": weight,
                    "required_proficiency": required_prof,
                    "coverage_score": c_i
                })

        # Calculate standard unweighted coverage and gap
        num_required = len(job_skills)
        unweighted_coverage = round((covered_count / num_required * 100), 2) if num_required > 0 else 0.0
        unweighted_gap = round(100.0 - unweighted_coverage, 2)

        # Calculate weighted coverage and gap
        weighted_coverage = round((covered_weight / total_weight * 100), 2) if total_weight > 0 else 0.0
        weighted_gap = round(100.0 - weighted_coverage, 2)

        # Sort missing and partial skills by importance weight descending
        missing.sort(key=lambda x: x["importance_weight"], reverse=True)
        partially_demonstrated.sort(key=lambda x: x["importance_weight"], reverse=True)

        return {
            "unweighted_coverage": unweighted_coverage,
            "unweighted_gap": unweighted_gap,
            "weighted_coverage": weighted_coverage,
            "weighted_gap": weighted_gap,
            "demonstrated": demonstrated,
            "partially_demonstrated": partially_demonstrated,
            "missing": missing,
            "total_required_skills": num_required,
            "demonstrated_count": len(demonstrated),
            "partial_count": len(partially_demonstrated),
            "missing_count": len(missing)
        }

    @staticmethod
    def rank_recommendations(
        gap_analysis: Dict[str, Any],
        catalog_resources: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Rank learning resources addressing missing and partially demonstrated skills.
        High-priority missing skills with higher importance weight are ranked first.
        """
        gaps_to_address = {}
        for skill in gap_analysis.get("missing", []):
            gaps_to_address[skill["canonical_name"].lower()] = {
                "skill": skill["canonical_name"],
                "urgency": "High (Missing Core Skill)",
                "weight": skill["importance_weight"] * 1.5  # Boost missing skills
            }
        for skill in gap_analysis.get("partially_demonstrated", []):
            gaps_to_address[skill["canonical_name"].lower()] = {
                "skill": skill["canonical_name"],
                "urgency": "Medium (Proficiency Upgrade)",
                "weight": skill["importance_weight"] * 1.0
            }

        ranked = []
        for res in catalog_resources:
            skill_name = res.get("skill_name", "").lower()
            if skill_name in gaps_to_address:
                gap_info = gaps_to_address[skill_name]
                score = gap_info["weight"]
                ranked.append({
                    "resource_id": res.get("resource_id"),
                    "title": res.get("title"),
                    "provider": res.get("provider"),
                    "url": res.get("url"),
                    "skill_name": gap_info["skill"],
                    "difficulty": res.get("difficulty", "Intermediate"),
                    "resource_type": res.get("resource_type", "Course"),
                    "reason": f"Directly addresses {gap_info['urgency']} for target role with importance weight {res.get('importance_weight', 3.0):.1f}",
                    "relevance_score": round(score, 2)
                })

        ranked.sort(key=lambda x: x["relevance_score"], reverse=True)
        for i, item in enumerate(ranked):
            item["rank"] = i + 1

        return ranked[:top_k]

default_gap_analyzer = SkillGapAnalyzer()
