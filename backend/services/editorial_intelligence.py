"""
Editorial Intelligence System.

Smart decision support for editors:
- Desk rejection prediction
- Editor assignment recommendations
- Review timeline management
- Quality signals detection
- Conflict of interest detection
"""
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass


class DeskDecision(Enum):
    """Desk decision recommendations."""
    STRONG_ACCEPT = "strong_accept"  # Send to review immediately
    ACCEPT = "accept"  # Likely suitable for review
    BORDERLINE = "borderline"  # Needs careful evaluation
    REJECT = "reject"  # Likely desk rejection
    STRONG_REJECT = "strong_reject"  # Clear desk rejection


@dataclass
class DeskRecommendation:
    """Desk review recommendation."""
    decision: DeskDecision
    confidence: float  # 0-1
    reasons: List[str]
    red_flags: List[str]
    green_flags: List[str]
    score: int  # 0-100


class EditorialIntelligence:
    """
    Provides intelligent decision support for editors.

    Uses rules-based analysis to:
    - Predict desk rejection likelihood
    - Identify quality signals
    - Detect potential issues
    - Recommend actions
    """

    def analyze_for_desk_decision(
        self,
        title: str,
        abstract: str,
        authors: List[Dict],
        references: List[str],
        keywords: List[str],
        manuscript_type: str,
        author_previous_publications: Optional[int] = None,
        author_h_index: Optional[int] = None,
        submission_quality_score: Optional[float] = None
    ) -> DeskRecommendation:
        """
        Analyze manuscript for desk decision.

        Returns recommendation with reasoning.
        """
        score = 0
        reasons = []
        red_flags = []
        green_flags = []

        # 1. Quality signals (30 points)
        quality_score = self._analyze_quality_signals(
            title, abstract, references, keywords
        )
        score += quality_score
        if quality_score >= 25:
            green_flags.append(f"High quality signals ({quality_score}/30)")
        elif quality_score < 15:
            red_flags.append(f"Low quality indicators ({quality_score}/30)")

        # 2. Scope and fit (20 points)
        scope_score = self._analyze_scope_fit(title, abstract, keywords, manuscript_type)
        score += scope_score
        if scope_score >= 15:
            green_flags.append("Strong fit with journal scope")
        elif scope_score < 10:
            red_flags.append("Questionable fit with journal scope")

        # 3. Author track record (15 points)
        if author_previous_publications is not None:
            author_score = self._analyze_author_track_record(
                author_previous_publications, author_h_index
            )
            score += author_score
            if author_score >= 12:
                green_flags.append("Strong author credentials")

        # 4. Novelty indicators (20 points)
        novelty_score = self._analyze_novelty(title, abstract)
        score += novelty_score
        if novelty_score >= 15:
            green_flags.append("Novel contribution indicated")
        elif novelty_score < 8:
            red_flags.append("Limited novelty apparent")

        # 5. Technical rigor (15 points)
        rigor_score = self._analyze_technical_rigor(abstract)
        score += rigor_score
        if rigor_score >= 12:
            green_flags.append("Rigorous methodology described")
        elif rigor_score < 6:
            red_flags.append("Methodological concerns")

        # Submission quality bonus
        if submission_quality_score and submission_quality_score >= 80:
            score += 10
            green_flags.append("Excellent submission quality")

        # Determine decision
        if score >= 80:
            decision = DeskDecision.STRONG_ACCEPT
            confidence = 0.9
            reasons.append("Excellent fit, high quality, strong novelty")
        elif score >= 65:
            decision = DeskDecision.ACCEPT
            confidence = 0.75
            reasons.append("Good quality submission, suitable for peer review")
        elif score >= 45:
            decision = DeskDecision.BORDERLINE
            confidence = 0.6
            reasons.append("Mixed signals, editor judgment needed")
        elif score >= 30:
            decision = DeskDecision.REJECT
            confidence = 0.75
            reasons.append("Multiple quality concerns, likely not suitable")
        else:
            decision = DeskDecision.STRONG_REJECT
            confidence = 0.9
            reasons.append("Significant issues, desk rejection recommended")

        return DeskRecommendation(
            decision=decision,
            confidence=confidence,
            reasons=reasons,
            red_flags=red_flags,
            green_flags=green_flags,
            score=score
        )

    def _analyze_quality_signals(
        self,
        title: str,
        abstract: str,
        references: List[str],
        keywords: List[str]
    ) -> int:
        """Analyze quality signals (0-30 points)."""
        score = 0

        # Title quality (0-5)
        if 50 <= len(title) <= 150:
            score += 5
        elif 20 <= len(title) <= 200:
            score += 3

        # Abstract quality (0-10)
        word_count = len(abstract.split())
        if 200 <= word_count <= 350:
            score += 5
        elif 150 <= word_count <= 450:
            score += 3

        # Check for structured elements in abstract
        abstract_lower = abstract.lower()
        structure_words = ['background', 'method', 'result', 'conclusion']
        structure_count = sum(1 for word in structure_words if word in abstract_lower)
        score += min(structure_count, 5)

        # References quality (0-10)
        ref_count = len(references)
        if 20 <= ref_count <= 60:
            score += 5
        elif 10 <= ref_count <= 100:
            score += 3

        # Check reference recency
        current_year = datetime.now().year
        recent_refs = 0
        for ref in references[:10]:  # Sample first 10
            if str(current_year) in ref or str(current_year - 1) in ref:
                recent_refs += 1
        if recent_refs >= 3:
            score += 5
        elif recent_refs >= 1:
            score += 2

        # Keywords quality (0-5)
        if 3 <= len(keywords) <= 6:
            score += 5
        elif len(keywords) >= 2:
            score += 2

        return score

    def _analyze_scope_fit(
        self,
        title: str,
        abstract: str,
        keywords: List[str],
        manuscript_type: str
    ) -> int:
        """Analyze fit with journal scope (0-20 points)."""
        score = 0

        # Journal's primary topics (customize for your journal)
        primary_topics = [
            'biology', 'genetics', 'biochemistry', 'molecular',
            'cell', 'microbiology', 'immunology', 'neuroscience'
        ]

        # Check title for topic match
        title_lower = title.lower()
        title_matches = sum(1 for topic in primary_topics if topic in title_lower)
        score += min(title_matches * 3, 6)

        # Check abstract for topic match
        abstract_lower = abstract.lower()
        abstract_matches = sum(1 for topic in primary_topics if topic in abstract_lower)
        score += min(abstract_matches * 2, 8)

        # Check keywords for topic match
        keywords_lower = [k.lower() for k in keywords]
        keyword_matches = sum(
            1 for topic in primary_topics
            for keyword in keywords_lower
            if topic in keyword
        )
        score += min(keyword_matches * 2, 6)

        return score

    def _analyze_author_track_record(
        self,
        previous_pubs: int,
        h_index: Optional[int]
    ) -> int:
        """Analyze author credentials (0-15 points)."""
        score = 0

        # Previous publications
        if previous_pubs >= 20:
            score += 8
        elif previous_pubs >= 10:
            score += 6
        elif previous_pubs >= 5:
            score += 4
        elif previous_pubs >= 1:
            score += 2

        # H-index (if available)
        if h_index:
            if h_index >= 20:
                score += 7
            elif h_index >= 10:
                score += 5
            elif h_index >= 5:
                score += 3

        return score

    def _analyze_novelty(self, title: str, abstract: str) -> int:
        """Analyze novelty indicators (0-20 points)."""
        score = 0

        # Novelty keywords
        novelty_words = [
            'novel', 'new', 'first', 'unprecedented', 'innovative',
            'discovery', 'breakthrough', 'advance', 'pioneer'
        ]

        text = (title + ' ' + abstract).lower()

        # Presence of novelty indicators
        novelty_count = sum(1 for word in novelty_words if word in text)
        score += min(novelty_count * 3, 9)

        # Check for comparative language (suggests improvement)
        comparative_words = ['better', 'improved', 'enhanced', 'superior', 'faster', 'more efficient']
        comparative_count = sum(1 for word in comparative_words if word in text)
        score += min(comparative_count * 2, 6)

        # Check for specific contributions
        contribution_words = ['demonstrate', 'show', 'reveal', 'find', 'discover', 'identify']
        contribution_count = sum(1 for word in contribution_words if word in text)
        score += min(contribution_count, 5)

        return score

    def _analyze_technical_rigor(self, abstract: str) -> int:
        """Analyze technical rigor indicators (0-15 points)."""
        score = 0

        abstract_lower = abstract.lower()

        # Methodology indicators
        method_words = [
            'experiment', 'analysis', 'model', 'test', 'measure',
            'quantify', 'assess', 'evaluate', 'statistical'
        ]
        method_count = sum(1 for word in method_words if word in abstract_lower)
        score += min(method_count * 2, 8)

        # Data/sample size mentions
        if any(word in abstract_lower for word in ['n =', 'n=', 'sample size', 'participants']):
            score += 3

        # Statistical terminology
        stats_words = ['significant', 'p <', 'p<', 'correlation', 'regression', 'anova']
        if any(word in abstract_lower for word in stats_words):
            score += 4

        return score

    def detect_conflicts_of_interest(
        self,
        manuscript_authors: List[Dict],
        potential_reviewer: Dict,
        recent_collaborations_years: int = 3
    ) -> Tuple[bool, List[str]]:
        """
        Detect potential conflicts of interest.

        Returns:
            (has_conflict, list of conflict reasons)
        """
        conflicts = []

        author_names = [a.get('name', '').lower() for a in manuscript_authors]
        author_affiliations = [a.get('affiliation', '').lower() for a in manuscript_authors]
        author_emails = [a.get('email', '').lower() for a in manuscript_authors if a.get('email')]

        reviewer_name = potential_reviewer.get('name', '').lower()
        reviewer_affiliation = potential_reviewer.get('affiliation', '').lower()
        reviewer_email = potential_reviewer.get('email', '').lower()

        # 1. Same person
        if reviewer_name in author_names:
            conflicts.append("Reviewer is an author on the manuscript")

        # 2. Same institution
        if reviewer_affiliation:
            for affil in author_affiliations:
                if affil and reviewer_affiliation in affil:
                    conflicts.append(f"Same institution: {affil}")

        # 3. Same email domain (suggests same institution)
        if reviewer_email:
            reviewer_domain = reviewer_email.split('@')[-1]
            for author_email in author_emails:
                author_domain = author_email.split('@')[-1]
                if reviewer_domain == author_domain and reviewer_domain != 'gmail.com':
                    conflicts.append(f"Same email domain: @{reviewer_domain}")

        # 4. Recent collaboration (if we have this data)
        reviewer_recent_collabs = potential_reviewer.get('recent_collaborators', [])
        if reviewer_recent_collabs:
            for author_name in author_names:
                if author_name in [c.lower() for c in reviewer_recent_collabs]:
                    conflicts.append(f"Recent collaboration with {author_name}")

        has_conflict = len(conflicts) > 0
        return has_conflict, conflicts


@dataclass
class DeadlineAlert:
    """Deadline alert information."""
    manuscript_id: int
    manuscript_title: str
    stage: str  # 'review', 'revision', 'production'
    person: str  # Who needs to act
    person_role: str
    deadline: datetime
    days_remaining: int
    urgency: str  # 'ok', 'approaching', 'urgent', 'overdue'
    message: str


class DeadlineManagement:
    """
    Smart deadline tracking and escalation.

    Monitors deadlines and generates appropriate alerts.
    """

    def generate_deadline_alerts(
        self,
        manuscripts: List[Dict]
    ) -> List[DeadlineAlert]:
        """
        Generate deadline alerts for all active manuscripts.
        """
        alerts = []
        now = datetime.now()

        for manuscript in manuscripts:
            # Review deadlines
            if manuscript.get('stage') == 'under_review':
                for review in manuscript.get('reviews', []):
                    if review.get('status') == 'pending':
                        deadline = review.get('deadline')
                        if deadline:
                            days_left = (deadline - now).days
                            urgency = self._calculate_urgency(days_left)

                            alerts.append(DeadlineAlert(
                                manuscript_id=manuscript['id'],
                                manuscript_title=manuscript['title'],
                                stage='review',
                                person=review['reviewer_name'],
                                person_role='Reviewer',
                                deadline=deadline,
                                days_remaining=days_left,
                                urgency=urgency,
                                message=self._generate_deadline_message(
                                    'review', days_left, urgency
                                )
                            ))

            # Revision deadlines
            if manuscript.get('stage') == 'revisions_requested':
                deadline = manuscript.get('revision_deadline')
                if deadline:
                    days_left = (deadline - now).days
                    urgency = self._calculate_urgency(days_left)

                    alerts.append(DeadlineAlert(
                        manuscript_id=manuscript['id'],
                        manuscript_title=manuscript['title'],
                        stage='revision',
                        person=manuscript['submitter_name'],
                        person_role='Author',
                        deadline=deadline,
                        days_remaining=days_left,
                        urgency=urgency,
                        message=self._generate_deadline_message(
                            'revision', days_left, urgency
                        )
                    ))

        # Sort by urgency and days remaining
        urgency_order = {'overdue': 0, 'urgent': 1, 'approaching': 2, 'ok': 3}
        alerts.sort(key=lambda x: (urgency_order[x.urgency], x.days_remaining))

        return alerts

    def _calculate_urgency(self, days_remaining: int) -> str:
        """Calculate urgency level."""
        if days_remaining < 0:
            return 'overdue'
        elif days_remaining <= 3:
            return 'urgent'
        elif days_remaining <= 7:
            return 'approaching'
        else:
            return 'ok'

    def _generate_deadline_message(
        self,
        stage: str,
        days_remaining: int,
        urgency: str
    ) -> str:
        """Generate appropriate message based on urgency."""
        if urgency == 'overdue':
            if stage == 'review':
                return f"Review is {abs(days_remaining)} days overdue. Please complete urgently."
            else:
                return f"Revision deadline passed {abs(days_remaining)} days ago."

        elif urgency == 'urgent':
            if stage == 'review':
                return f"Review due in {days_remaining} days. Please prioritize."
            else:
                return f"Revision deadline in {days_remaining} days. Please submit soon."

        elif urgency == 'approaching':
            if stage == 'review':
                return f"Review due in {days_remaining} days."
            else:
                return f"Revision deadline in {days_remaining} days."

        else:
            if stage == 'review':
                return f"Review due in {days_remaining} days. On track."
            else:
                return f"Revision deadline in {days_remaining} days."


# Singleton instances
editorial_intelligence = EditorialIntelligence()
deadline_manager = DeadlineManagement()
