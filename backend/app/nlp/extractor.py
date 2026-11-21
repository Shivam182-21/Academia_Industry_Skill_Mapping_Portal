"""
Skill Extraction Engine.
Extracts, normalizes, and contextualizes skills from academic course syllabi and industry job descriptions.
"""

import re
from typing import List, Dict, Any
from backend.app.nlp.taxonomy import CANONICAL_SKILLS

class SkillExtractor:
    def __init__(self, taxonomy: List[Dict[str, Any]] = None):
        self.taxonomy = taxonomy or CANONICAL_SKILLS
        self._compiled_patterns = self._build_compiled_patterns()

    def _build_compiled_patterns(self) -> List[Dict[str, Any]]:
        compiled = []
        for item in self.taxonomy:
            canonical = item["canonical_name"]
            category = item["category"]
            patterns = []
            
            # Sort aliases by length descending so longer phrases match before shorter substrings
            all_tokens = [canonical] + item.get("aliases", [])
            all_tokens = sorted(list(set(all_tokens)), key=len, reverse=True)
            
            for token in all_tokens:
                # Escape regex special characters, except handle & or / smoothly
                escaped = re.escape(token)
                # Word boundaries: \b on start and end
                pattern_str = r"(?<!\w)" + escaped + r"(?!\w)"
                patterns.append(re.compile(pattern_str, re.IGNORECASE))
                
            compiled.append({
                "canonical_name": canonical,
                "category": category,
                "description": item.get("description", ""),
                "patterns": patterns
            })
        return compiled

    def clean_text(self, text: str) -> str:
        """Normalize line breaks, multiple whitespaces, and punctuation."""
        if not text:
            return ""
        cleaned = re.sub(r"[\r\n\t]+", " ", text)
        cleaned = re.sub(r"\s{2,}", " ", cleaned)
        return cleaned.strip()

    def extract_skills(self, text: str) -> List[Dict[str, Any]]:
        """
        Extracts skills from text with context evidence and confidence estimation.
        Returns a deduplicated list of matched canonical skills.
        """
        if not text or not text.strip():
            return []

        cleaned_text = self.clean_text(text)
        sentences = re.split(r"(?<=[.!?])\s+", cleaned_text)
        
        extracted = {}

        for entry in self._compiled_patterns:
            canonical = entry["canonical_name"]
            category = entry["category"]
            description = entry["description"]
            
            match_count = 0
            evidence_snippets = []

            for pattern in entry["patterns"]:
                # Check occurrence in the full cleaned text
                matches = list(pattern.finditer(cleaned_text))
                if matches:
                    match_count += len(matches)
                    # Find sentence snippet for evidence
                    for m in matches[:2]:  # Keep top 2 context snippets
                        start_pos = max(0, m.start() - 40)
                        end_pos = min(len(cleaned_text), m.end() + 40)
                        snippet = cleaned_text[start_pos:end_pos].strip()
                        if snippet and not snippet.startswith("..."):
                            snippet = "..." + snippet
                        if snippet and not snippet.endswith("..."):
                            snippet = snippet + "..."
                        evidence_snippets.append(snippet)

            if match_count > 0:
                # Base confidence starts at 0.85; increased with multiple occurrences
                confidence = min(0.98, 0.85 + (0.04 * (match_count - 1)))
                extracted[canonical] = {
                    "canonical_name": canonical,
                    "category": category,
                    "description": description,
                    "frequency": match_count,
                    "confidence": round(confidence, 2),
                    "evidence_snippet": evidence_snippets[0] if evidence_snippets else cleaned_text[:100]
                }

        return list(extracted.values())

    def extract_skills_naive_keyword_baseline(self, text: str) -> List[str]:
        """
        Baseline comparator: naive substring matching without token boundary guards or synonym expansion.
        Used for FR-09 baseline empirical comparison.
        """
        if not text:
            return []
        lower_text = text.lower()
        matched = []
        for item in self.taxonomy:
            # Naive substring check on canonical name only
            if item["canonical_name"].lower() in lower_text:
                matched.append(item["canonical_name"])
        return matched

# Singleton instance
default_extractor = SkillExtractor()
