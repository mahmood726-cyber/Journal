"""
Comprehensive Rules-Based Intelligence Engine.

Provides smart automation and decision support across all journal workflows:
- Submission guidance and validation
- Editorial decision support
- Reviewer matching and management
- Quality gates and compliance checks
- Deadline management and escalation
- Publication readiness validation

No ML required - uses heuristics, rules, and statistical analysis.
"""
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import re
from dataclasses import dataclass


# ============================================================================
# Smart Submission Assistant
# ============================================================================

class SubmissionIssue(Enum):
    """Types of submission issues."""
    CRITICAL = "critical"  # Blocks submission
    WARNING = "warning"    # Should fix but can submit
    SUGGESTION = "suggestion"  # Nice to have


@dataclass
class SubmissionCheck:
    """Result of a submission validation check."""
    category: str
    issue_type: SubmissionIssue
    message: str
    details: Optional[str] = None
    fix_suggestion: Optional[str] = None


class SmartSubmissionAssistant:
    """
    Guides authors through submission with intelligent validation.

    Checks:
    - Manuscript completeness
    - Author information quality
    - Reference formatting
    - File requirements
    - Ethical statements
    - Funding disclosure
    """

    def validate_submission(
        self,
        title: str,
        abstract: str,
        authors: List[Dict],
        references: List[str],
        keywords: List[str],
        manuscript_file: Optional[str] = None,
        figures: Optional[List] = None,
        funding_statement: Optional[str] = None,
        ethics_statement: Optional[str] = None,
        data_availability: Optional[str] = None
    ) -> Tuple[bool, List[SubmissionCheck]]:
        """
        Comprehensive submission validation.

        Returns:
            (can_submit, list of issues)
        """
        issues = []

        # Title validation
        issues.extend(self._validate_title(title))

        # Abstract validation
        issues.extend(self._validate_abstract(abstract))

        # Authors validation
        issues.extend(self._validate_authors(authors))

        # References validation
        issues.extend(self._validate_references(references))

        # Keywords validation
        issues.extend(self._validate_keywords(keywords))

        # File validation
        if manuscript_file:
            issues.extend(self._validate_manuscript_file(manuscript_file))

        # Required statements
        issues.extend(self._validate_required_statements(
            funding_statement, ethics_statement, data_availability
        ))

        # Check if any critical issues
        has_critical = any(i.issue_type == SubmissionIssue.CRITICAL for i in issues)
        can_submit = not has_critical

        return can_submit, issues

    def _validate_title(self, title: str) -> List[SubmissionCheck]:
        """Validate manuscript title."""
        issues = []

        if not title or len(title) < 10:
            issues.append(SubmissionCheck(
                category="Title",
                issue_type=SubmissionIssue.CRITICAL,
                message="Title too short (minimum 10 characters)",
                fix_suggestion="Write a descriptive title that summarizes your research"
            ))

        if len(title) > 250:
            issues.append(SubmissionCheck(
                category="Title",
                issue_type=SubmissionIssue.WARNING,
                message="Title too long (250+ characters)",
                details=f"Current length: {len(title)} characters",
                fix_suggestion="Shorten to 150-200 characters for better readability"
            ))

        # Check for question marks
        if '?' in title:
            issues.append(SubmissionCheck(
                category="Title",
                issue_type=SubmissionIssue.WARNING,
                message="Title contains question mark",
                details="Titles are typically declarative statements",
                fix_suggestion="Consider rephrasing as a statement"
            ))

        # Check for all caps
        if title.isupper():
            issues.append(SubmissionCheck(
                category="Title",
                issue_type=SubmissionIssue.WARNING,
                message="Title is all uppercase",
                fix_suggestion="Use title case for better readability"
            ))

        # Check for common abbreviations
        common_abbrev = ['DNA', 'RNA', 'HIV', 'COVID']
        abbrev_pattern = r'\b([A-Z]{2,})\b'
        abbreviations = re.findall(abbrev_pattern, title)
        undefined_abbrev = [a for a in abbreviations if a not in common_abbrev]

        if undefined_abbrev:
            issues.append(SubmissionCheck(
                category="Title",
                issue_type=SubmissionIssue.SUGGESTION,
                message="Title contains abbreviations",
                details=f"Found: {', '.join(undefined_abbrev)}",
                fix_suggestion="Spell out abbreviations in title for clarity"
            ))

        return issues

    def _validate_abstract(self, abstract: str) -> List[SubmissionCheck]:
        """Validate abstract structure and content."""
        issues = []

        if not abstract or len(abstract) < 150:
            issues.append(SubmissionCheck(
                category="Abstract",
                issue_type=SubmissionIssue.CRITICAL,
                message="Abstract too short (minimum 150 characters)",
                fix_suggestion="Include background, methods, results, and conclusions"
            ))

        word_count = len(abstract.split())

        if word_count < 100:
            issues.append(SubmissionCheck(
                category="Abstract",
                issue_type=SubmissionIssue.WARNING,
                message=f"Abstract too brief ({word_count} words)",
                fix_suggestion="Most journals require 150-300 words"
            ))

        if word_count > 500:
            issues.append(SubmissionCheck(
                category="Abstract",
                issue_type=SubmissionIssue.WARNING,
                message=f"Abstract too long ({word_count} words)",
                fix_suggestion="Condense to 250-300 words"
            ))

        # Check for structured elements
        abstract_lower = abstract.lower()
        has_background = any(word in abstract_lower for word in ['background', 'introduction', 'context'])
        has_methods = any(word in abstract_lower for word in ['method', 'approach', 'design'])
        has_results = any(word in abstract_lower for word in ['result', 'finding', 'found', 'showed'])
        has_conclusion = any(word in abstract_lower for word in ['conclusion', 'implication', 'suggest'])

        missing_sections = []
        if not has_background:
            missing_sections.append("background")
        if not has_methods:
            missing_sections.append("methods")
        if not has_results:
            missing_sections.append("results")
        if not has_conclusion:
            missing_sections.append("conclusions")

        if len(missing_sections) >= 2:
            issues.append(SubmissionCheck(
                category="Abstract",
                issue_type=SubmissionIssue.WARNING,
                message="Abstract may be missing key sections",
                details=f"Possibly missing: {', '.join(missing_sections)}",
                fix_suggestion="Include background, methods, results, and conclusions"
            ))

        # Check for citations in abstract
        if '[' in abstract or '(' in abstract:
            issues.append(SubmissionCheck(
                category="Abstract",
                issue_type=SubmissionIssue.SUGGESTION,
                message="Abstract may contain citations",
                details="Citations are typically not included in abstracts",
                fix_suggestion="Remove references from abstract"
            ))

        return issues

    def _validate_authors(self, authors: List[Dict]) -> List[SubmissionCheck]:
        """Validate author information completeness."""
        issues = []

        if not authors or len(authors) == 0:
            issues.append(SubmissionCheck(
                category="Authors",
                issue_type=SubmissionIssue.CRITICAL,
                message="No authors listed",
                fix_suggestion="Add at least one author"
            ))
            return issues

        # Check for corresponding author
        has_corresponding = any(a.get('is_corresponding', False) for a in authors)
        if not has_corresponding:
            issues.append(SubmissionCheck(
                category="Authors",
                issue_type=SubmissionIssue.WARNING,
                message="No corresponding author marked",
                fix_suggestion="Designate one author as corresponding author"
            ))

        # Check each author's information
        for idx, author in enumerate(authors, 1):
            name = author.get('name', '')
            email = author.get('email', '')
            affiliation = author.get('affiliation', '')
            orcid = author.get('orcid', '')

            # Name validation
            if not name or len(name) < 3:
                issues.append(SubmissionCheck(
                    category="Authors",
                    issue_type=SubmissionIssue.CRITICAL,
                    message=f"Author {idx}: Name missing or incomplete",
                    fix_suggestion="Provide full name (first and last)"
                ))

            # Email validation (for corresponding author)
            if author.get('is_corresponding') and not email:
                issues.append(SubmissionCheck(
                    category="Authors",
                    issue_type=SubmissionIssue.CRITICAL,
                    message=f"Author {idx}: Corresponding author must have email",
                    fix_suggestion="Add email address for corresponding author"
                ))

            # Affiliation validation
            if not affiliation:
                issues.append(SubmissionCheck(
                    category="Authors",
                    issue_type=SubmissionIssue.WARNING,
                    message=f"Author {idx} ({name}): No affiliation",
                    fix_suggestion="Add institutional affiliation"
                ))

            # ORCID suggestion
            if not orcid:
                issues.append(SubmissionCheck(
                    category="Authors",
                    issue_type=SubmissionIssue.SUGGESTION,
                    message=f"Author {idx} ({name}): No ORCID",
                    details="ORCID iDs help identify researchers uniquely",
                    fix_suggestion="Add ORCID iD (get free at orcid.org)"
                ))

        return issues

    def _validate_references(self, references: List[str]) -> List[SubmissionCheck]:
        """Validate reference list quality."""
        issues = []

        if not references or len(references) == 0:
            issues.append(SubmissionCheck(
                category="References",
                issue_type=SubmissionIssue.CRITICAL,
                message="No references provided",
                fix_suggestion="Add citations to support your research"
            ))
            return issues

        ref_count = len(references)

        # Check reference count
        if ref_count < 10:
            issues.append(SubmissionCheck(
                category="References",
                issue_type=SubmissionIssue.WARNING,
                message=f"Few references ({ref_count})",
                details="Most research articles cite 20-50 sources",
                fix_suggestion="Consider adding more supporting literature"
            ))

        if ref_count > 100:
            issues.append(SubmissionCheck(
                category="References",
                issue_type=SubmissionIssue.WARNING,
                message=f"Many references ({ref_count})",
                details="Unless this is a review article, consider reducing",
                fix_suggestion="Focus on most relevant citations"
            ))

        # Check reference recency
        current_year = datetime.now().year
        years_found = []
        for ref in references:
            year_matches = re.findall(r'\b(19\d{2}|20\d{2})\b', ref)
            years_found.extend([int(y) for y in year_matches])

        if years_found:
            avg_year = sum(years_found) / len(years_found)
            years_old = current_year - avg_year

            if years_old > 10:
                issues.append(SubmissionCheck(
                    category="References",
                    issue_type=SubmissionIssue.WARNING,
                    message="References may be outdated",
                    details=f"Average citation year: {int(avg_year)}",
                    fix_suggestion="Include recent literature from last 5 years"
                ))

            # Check for very recent references
            recent_refs = [y for y in years_found if current_year - y <= 2]
            if len(recent_refs) / len(years_found) < 0.2:
                issues.append(SubmissionCheck(
                    category="References",
                    issue_type=SubmissionIssue.SUGGESTION,
                    message="Few recent references",
                    details=f"Only {len(recent_refs)} from last 2 years",
                    fix_suggestion="Include current literature to show field awareness"
                ))

        # Check for DOIs
        refs_with_doi = sum(1 for ref in references if 'doi' in ref.lower() or '10.' in ref)
        doi_percentage = (refs_with_doi / ref_count) * 100

        if doi_percentage < 30:
            issues.append(SubmissionCheck(
                category="References",
                issue_type=SubmissionIssue.SUGGESTION,
                message="Few references with DOIs",
                details=f"Only {refs_with_doi}/{ref_count} have DOIs",
                fix_suggestion="Add DOIs to references for better tracking"
            ))

        return issues

    def _validate_keywords(self, keywords: List[str]) -> List[SubmissionCheck]:
        """Validate keyword selection."""
        issues = []

        if not keywords or len(keywords) == 0:
            issues.append(SubmissionCheck(
                category="Keywords",
                issue_type=SubmissionIssue.CRITICAL,
                message="No keywords provided",
                fix_suggestion="Add 3-6 keywords for discoverability"
            ))
            return issues

        keyword_count = len(keywords)

        if keyword_count < 3:
            issues.append(SubmissionCheck(
                category="Keywords",
                issue_type=SubmissionIssue.WARNING,
                message=f"Too few keywords ({keyword_count})",
                fix_suggestion="Provide 3-6 keywords for better discoverability"
            ))

        if keyword_count > 10:
            issues.append(SubmissionCheck(
                category="Keywords",
                issue_type=SubmissionIssue.WARNING,
                message=f"Too many keywords ({keyword_count})",
                fix_suggestion="Focus on 3-6 most relevant keywords"
            ))

        # Check keyword quality
        for keyword in keywords:
            if len(keyword) < 3:
                issues.append(SubmissionCheck(
                    category="Keywords",
                    issue_type=SubmissionIssue.WARNING,
                    message=f"Keyword too short: '{keyword}'",
                    fix_suggestion="Use meaningful terms (3+ characters)"
                ))

            if len(keyword.split()) > 4:
                issues.append(SubmissionCheck(
                    category="Keywords",
                    issue_type=SubmissionIssue.SUGGESTION,
                    message=f"Long keyword phrase: '{keyword}'",
                    fix_suggestion="Use concise terms (1-3 words)"
                ))

        return issues

    def _validate_manuscript_file(self, manuscript_file: str) -> List[SubmissionCheck]:
        """Validate manuscript file."""
        issues = []

        # Check file format
        allowed_formats = ['.pdf', '.doc', '.docx']
        file_ext = manuscript_file.lower()[-4:]

        if not any(file_ext.endswith(fmt) for fmt in allowed_formats):
            issues.append(SubmissionCheck(
                category="Files",
                issue_type=SubmissionIssue.CRITICAL,
                message="Manuscript file format not supported",
                details=f"Found: {file_ext}",
                fix_suggestion="Upload as PDF, DOC, or DOCX"
            ))

        return issues

    def _validate_required_statements(
        self,
        funding: Optional[str],
        ethics: Optional[str],
        data_availability: Optional[str]
    ) -> List[SubmissionCheck]:
        """Validate required statements."""
        issues = []

        # Funding statement
        if not funding or len(funding.strip()) < 10:
            issues.append(SubmissionCheck(
                category="Statements",
                issue_type=SubmissionIssue.WARNING,
                message="Funding statement missing or incomplete",
                fix_suggestion="State funding sources or 'No funding received'"
            ))

        # Ethics statement (for human/animal studies)
        if not ethics or len(ethics.strip()) < 10:
            issues.append(SubmissionCheck(
                category="Statements",
                issue_type=SubmissionIssue.WARNING,
                message="Ethics statement missing",
                details="Required for human/animal research",
                fix_suggestion="Provide ethics approval or state 'Not applicable'"
            ))

        # Data availability
        if not data_availability or len(data_availability.strip()) < 10:
            issues.append(SubmissionCheck(
                category="Statements",
                issue_type=SubmissionIssue.SUGGESTION,
                message="Data availability statement missing",
                details="Many journals now require this",
                fix_suggestion="State where data can be accessed or 'Available on request'"
            ))

        return issues


# Singleton instance
submission_assistant = SmartSubmissionAssistant()
