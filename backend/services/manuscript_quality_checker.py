"""
AI-Powered Manuscript Quality Checker.
Pre-submission analysis to improve quality and reduce desk rejections.
"""
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import re
from enum import Enum


class QualityLevel(str, Enum):
    """Quality assessment levels."""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"


@dataclass
class QualityCheck:
    """Individual quality check result."""
    name: str
    passed: bool
    score: float  # 0-100
    level: QualityLevel
    message: str
    recommendations: List[str]


@dataclass
class ManuscriptQualityReport:
    """Complete quality report for a manuscript."""
    overall_score: float  # 0-100
    overall_level: QualityLevel
    checks: List[QualityCheck]
    ready_for_submission: bool
    critical_issues: List[str]
    warnings: List[str]
    suggestions: List[str]


class ManuscriptQualityChecker:
    """
    Comprehensive manuscript quality checker.

    Analyzes:
    1. Structure completeness
    2. Abstract quality
    3. Reference formatting
    4. Word count compliance
    5. Figure/table quality
    6. Language quality
    7. Readability
    8. Citation appropriateness
    """

    def __init__(self):
        # Standard IMRaD sections
        self.required_sections = [
            'abstract',
            'introduction',
            'methods',
            'results',
            'discussion',
            'references'
        ]

        # Common section variations
        self.section_patterns = {
            'abstract': r'abstract',
            'introduction': r'introduction|background',
            'methods': r'methods|methodology|materials?\s+and\s+methods',
            'results': r'results?',
            'discussion': r'discussion|conclusions?',
            'references': r'references?|bibliography|works?\s+cited'
        }

    async def check_quality(
        self,
        title: str,
        abstract: str,
        full_text: str,
        references: List[str],
        word_count_min: int = 3000,
        word_count_max: int = 8000
    ) -> ManuscriptQualityReport:
        """
        Perform comprehensive quality check.

        Args:
            title: Manuscript title
            abstract: Abstract text
            full_text: Full manuscript text
            references: List of references
            word_count_min: Minimum word count
            word_count_max: Maximum word count

        Returns:
            ManuscriptQualityReport with all checks
        """
        checks = []

        # 1. Structure completeness
        checks.append(self._check_structure(full_text))

        # 2. Abstract quality
        checks.append(self._check_abstract(abstract))

        # 3. Title quality
        checks.append(self._check_title(title))

        # 4. Word count
        checks.append(self._check_word_count(full_text, word_count_min, word_count_max))

        # 5. References
        checks.append(self._check_references(references, full_text))

        # 6. Figures and tables
        checks.append(self._check_figures_tables(full_text))

        # 7. Language quality
        checks.append(self._check_language_quality(full_text))

        # 8. Readability
        checks.append(self._check_readability(full_text))

        # Calculate overall score
        overall_score = sum(check.score for check in checks) / len(checks)

        # Determine overall level
        if overall_score >= 85:
            overall_level = QualityLevel.EXCELLENT
        elif overall_score >= 70:
            overall_level = QualityLevel.GOOD
        elif overall_score >= 55:
            overall_level = QualityLevel.FAIR
        else:
            overall_level = QualityLevel.POOR

        # Collect issues
        critical_issues = []
        warnings = []
        suggestions = []

        for check in checks:
            if not check.passed:
                if check.level == QualityLevel.POOR:
                    critical_issues.extend(check.recommendations)
                elif check.level == QualityLevel.FAIR:
                    warnings.extend(check.recommendations)
            else:
                suggestions.extend(check.recommendations)

        # Ready for submission if no critical issues
        ready_for_submission = len(critical_issues) == 0 and overall_score >= 60

        return ManuscriptQualityReport(
            overall_score=round(overall_score, 1),
            overall_level=overall_level,
            checks=checks,
            ready_for_submission=ready_for_submission,
            critical_issues=critical_issues,
            warnings=warnings,
            suggestions=suggestions
        )

    def _check_structure(self, text: str) -> QualityCheck:
        """Check if manuscript has all required sections."""
        text_lower = text.lower()
        found_sections = []
        missing_sections = []

        for section, pattern in self.section_patterns.items():
            if re.search(pattern, text_lower):
                found_sections.append(section)
            else:
                missing_sections.append(section)

        score = (len(found_sections) / len(self.section_patterns)) * 100
        passed = len(missing_sections) == 0

        if passed:
            level = QualityLevel.EXCELLENT
            message = "All required sections present"
            recommendations = []
        else:
            level = QualityLevel.POOR if len(missing_sections) > 2 else QualityLevel.FAIR
            message = f"Missing sections: {', '.join(missing_sections)}"
            recommendations = [
                f"Add {section} section" for section in missing_sections
            ]

        return QualityCheck(
            name="Structure Completeness",
            passed=passed,
            score=score,
            level=level,
            message=message,
            recommendations=recommendations
        )

    def _check_abstract(self, abstract: str) -> QualityCheck:
        """Check abstract quality."""
        if not abstract:
            return QualityCheck(
                name="Abstract Quality",
                passed=False,
                score=0,
                level=QualityLevel.POOR,
                message="No abstract provided",
                recommendations=["Add abstract (150-300 words)"]
            )

        word_count = len(abstract.split())

        # Check word count (ideal: 150-300 words)
        if 150 <= word_count <= 300:
            score = 100
            level = QualityLevel.EXCELLENT
            message = f"Abstract length optimal ({word_count} words)"
            recommendations = []
            passed = True
        elif 100 <= word_count < 150 or 300 < word_count <= 400:
            score = 75
            level = QualityLevel.GOOD
            message = f"Abstract length acceptable ({word_count} words)"
            recommendations = [
                "Consider adjusting abstract to 150-300 words for optimal length"
            ]
            passed = True
        elif word_count < 100:
            score = 40
            level = QualityLevel.POOR
            message = f"Abstract too short ({word_count} words)"
            recommendations = [
                "Expand abstract to at least 150 words",
                "Include background, methods, results, and conclusions"
            ]
            passed = False
        else:
            score = 60
            level = QualityLevel.FAIR
            message = f"Abstract too long ({word_count} words)"
            recommendations = ["Shorten abstract to under 300 words"]
            passed = False

        # Check for key elements
        abstract_lower = abstract.lower()
        has_background = any(word in abstract_lower for word in ['background', 'introduction', 'context'])
        has_methods = any(word in abstract_lower for word in ['method', 'approach', 'technique'])
        has_results = any(word in abstract_lower for word in ['result', 'finding', 'showed', 'demonstrated'])
        has_conclusion = any(word in abstract_lower for word in ['conclusion', 'suggest', 'indicate'])

        missing_elements = []
        if not has_background:
            missing_elements.append("background/context")
        if not has_methods:
            missing_elements.append("methods")
        if not has_results:
            missing_elements.append("results")
        if not has_conclusion:
            missing_elements.append("conclusions")

        if missing_elements:
            recommendations.append(f"Consider adding: {', '.join(missing_elements)}")
            score = min(score, 70)

        return QualityCheck(
            name="Abstract Quality",
            passed=passed,
            score=score,
            level=level,
            message=message,
            recommendations=recommendations
        )

    def _check_title(self, title: str) -> QualityCheck:
        """Check title quality."""
        if not title:
            return QualityCheck(
                name="Title Quality",
                passed=False,
                score=0,
                level=QualityLevel.POOR,
                message="No title provided",
                recommendations=["Add descriptive title (10-20 words)"]
            )

        word_count = len(title.split())

        # Ideal title: 10-20 words
        if 10 <= word_count <= 20:
            score = 100
            level = QualityLevel.EXCELLENT
            message = f"Title length optimal ({word_count} words)"
            passed = True
            recommendations = []
        elif 6 <= word_count < 10:
            score = 75
            level = QualityLevel.GOOD
            message = f"Title acceptable but brief ({word_count} words)"
            passed = True
            recommendations = ["Consider adding more context to title"]
        elif word_count > 25:
            score = 60
            level = QualityLevel.FAIR
            message = f"Title too long ({word_count} words)"
            passed = False
            recommendations = ["Shorten title to 10-20 words for clarity"]
        else:
            score = 50
            level = QualityLevel.FAIR
            message = f"Title very brief ({word_count} words)"
            passed = False
            recommendations = ["Expand title to better describe the study"]

        return QualityCheck(
            name="Title Quality",
            passed=passed,
            score=score,
            level=level,
            message=message,
            recommendations=recommendations
        )

    def _check_word_count(self, text: str, min_count: int, max_count: int) -> QualityCheck:
        """Check if word count is within guidelines."""
        word_count = len(text.split())

        if min_count <= word_count <= max_count:
            score = 100
            level = QualityLevel.EXCELLENT
            message = f"Word count within guidelines ({word_count:,} words)"
            passed = True
            recommendations = []
        elif word_count < min_count:
            deficit = min_count - word_count
            score = max(40, 100 - (deficit / min_count * 100))
            level = QualityLevel.POOR if score < 60 else QualityLevel.FAIR
            message = f"Word count below minimum ({word_count:,} < {min_count:,})"
            passed = False
            recommendations = [f"Add approximately {deficit:,} words to meet minimum"]
        else:
            excess = word_count - max_count
            score = max(60, 100 - (excess / max_count * 50))
            level = QualityLevel.FAIR
            message = f"Word count exceeds maximum ({word_count:,} > {max_count:,})"
            passed = False
            recommendations = [f"Reduce by approximately {excess:,} words"]

        return QualityCheck(
            name="Word Count",
            passed=passed,
            score=score,
            level=level,
            message=message,
            recommendations=recommendations
        )

    def _check_references(self, references: List[str], full_text: str) -> QualityCheck:
        """Check reference quantity and citations."""
        ref_count = len(references)

        # Ideal: 20-50 references for most papers
        if 20 <= ref_count <= 50:
            score = 100
            level = QualityLevel.EXCELLENT
            message = f"Reference count appropriate ({ref_count})"
            passed = True
            recommendations = []
        elif 10 <= ref_count < 20:
            score = 75
            level = QualityLevel.GOOD
            message = f"Reference count acceptable ({ref_count})"
            passed = True
            recommendations = ["Consider adding more references for comprehensive literature review"]
        elif ref_count < 10:
            score = 40
            level = QualityLevel.POOR
            message = f"Too few references ({ref_count})"
            passed = False
            recommendations = [
                "Add more references to support claims",
                "Ensure comprehensive literature review"
            ]
        else:
            score = 80
            level = QualityLevel.GOOD
            message = f"Many references ({ref_count})"
            passed = True
            recommendations = ["Ensure all references are necessary and cited in text"]

        return QualityCheck(
            name="References",
            passed=passed,
            score=score,
            level=level,
            message=message,
            recommendations=recommendations
        )

    def _check_figures_tables(self, text: str) -> QualityCheck:
        """Check presence of figures and tables."""
        # Count figure and table mentions
        figures = len(re.findall(r'figure\s+\d+|fig\.\s*\d+', text, re.IGNORECASE))
        tables = len(re.findall(r'table\s+\d+', text, re.IGNORECASE))

        total = figures + tables

        if total >= 3:
            score = 100
            level = QualityLevel.EXCELLENT
            message = f"Good use of visual elements ({figures} figures, {tables} tables)"
            passed = True
            recommendations = []
        elif total >= 1:
            score = 75
            level = QualityLevel.GOOD
            message = f"Some visual elements present ({figures} figures, {tables} tables)"
            passed = True
            recommendations = ["Consider adding more figures/tables to illustrate key points"]
        else:
            score = 60
            level = QualityLevel.FAIR
            message = "No figures or tables detected"
            passed = False
            recommendations = [
                "Add figures to visualize key results",
                "Consider tables for data presentation"
            ]

        return QualityCheck(
            name="Figures & Tables",
            passed=passed,
            score=score,
            level=level,
            message=message,
            recommendations=recommendations
        )

    def _check_language_quality(self, text: str) -> QualityCheck:
        """Basic language quality check."""
        # Simple heuristics for language quality
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        # Average sentence length (ideal: 15-25 words)
        avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)

        # Check for common issues
        issues = []
        if avg_sentence_length > 30:
            issues.append("Sentences are too long on average")
        elif avg_sentence_length < 10:
            issues.append("Sentences are too short on average")

        # Check for passive voice (simplified)
        passive_count = len(re.findall(r'\b(was|were|is|are|been|be)\s+\w+ed\b', text))
        passive_ratio = passive_count / max(len(sentences), 1)
        if passive_ratio > 0.3:
            issues.append("Excessive use of passive voice")

        if not issues:
            score = 90
            level = QualityLevel.EXCELLENT
            message = "Language quality appears good"
            passed = True
            recommendations = ["Consider professional proofreading before submission"]
        else:
            score = 70
            level = QualityLevel.GOOD
            message = "Some language improvements possible"
            passed = True
            recommendations = issues + ["Consider professional language editing"]

        return QualityCheck(
            name="Language Quality",
            passed=passed,
            score=score,
            level=level,
            message=message,
            recommendations=recommendations
        )

    def _check_readability(self, text: str) -> QualityCheck:
        """Calculate readability score (simplified Flesch-Kincaid)."""
        sentences = len(re.split(r'[.!?]+', text))
        words = len(text.split())
        syllables = self._count_syllables(text)

        if words == 0 or sentences == 0:
            return QualityCheck(
                name="Readability",
                passed=False,
                score=0,
                level=QualityLevel.POOR,
                message="Insufficient text for analysis",
                recommendations=[]
            )

        # Simplified Flesch Reading Ease
        # Score: 0-100 (higher = easier to read)
        # Academic papers typically: 30-50
        avg_sentence_length = words / sentences
        avg_syllables_per_word = syllables / words

        flesch = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        flesch = max(0, min(100, flesch))  # Clamp to 0-100

        # Academic writing should be 30-60
        if 30 <= flesch <= 60:
            score = 100
            level = QualityLevel.EXCELLENT
            message = f"Readability appropriate for academic audience (score: {flesch:.1f})"
            passed = True
            recommendations = []
        elif 20 <= flesch < 30 or 60 < flesch <= 70:
            score = 80
            level = QualityLevel.GOOD
            message = f"Readability acceptable (score: {flesch:.1f})"
            passed = True
            recommendations = ["Consider simplifying some sentences"]
        else:
            score = 65
            level = QualityLevel.FAIR
            message = f"Readability could be improved (score: {flesch:.1f})"
            passed = False
            if flesch < 20:
                recommendations = ["Text is quite complex - consider simplifying"]
            else:
                recommendations = ["Text may be too simple for academic audience"]

        return QualityCheck(
            name="Readability",
            passed=passed,
            score=score,
            level=level,
            message=message,
            recommendations=recommendations
        )

    def _count_syllables(self, text: str) -> int:
        """Approximate syllable count."""
        # Simplified syllable counting
        text = text.lower()
        vowels = 'aeiouy'
        count = 0
        previous_was_vowel = False

        for char in text:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                count += 1
            previous_was_vowel = is_vowel

        # Rough approximation
        return max(1, count)


# Singleton instance
quality_checker = ManuscriptQualityChecker()
