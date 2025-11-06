"""
AI-powered email template generation service using local Llama.
Generates personalized, contextual emails for journal workflow events.
"""
from typing import List, Dict, Optional
from pydantic import BaseModel
from datetime import datetime
from enum import Enum

from .llm_service import get_llm_service, LocalLLMService


class EmailTone(str, Enum):
    """Email tone options."""
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    FORMAL = "formal"
    ENCOURAGING = "encouraging"
    CONGRATULATORY = "congratulatory"


class EmailTemplateType(str, Enum):
    """Email template types."""
    REVIEW_INVITATION = "review_invitation"
    REVIEW_REMINDER = "review_reminder"
    REVIEW_THANK_YOU = "review_thank_you"
    REVISION_REQUEST = "revision_request"
    MINOR_REVISIONS = "minor_revisions"
    MAJOR_REVISIONS = "major_revisions"
    ACCEPTANCE = "acceptance"
    REJECTION = "rejection"
    DESK_REJECT = "desk_reject"
    SUBMISSION_CONFIRMATION = "submission_confirmation"
    COPYEDITING_REQUEST = "copyediting_request"
    PRODUCTION_NOTIFICATION = "production_notification"
    PUBLICATION_ANNOUNCEMENT = "publication_announcement"


class EmailContent(BaseModel):
    """Generated email content."""
    subject: str
    body: str
    tone: str
    template_type: str
    generated_at: datetime
    tokens_used: int


class AIEmailTemplateService:
    """
    AI-powered email template generation using local LLM.

    Features:
    - Dynamic, personalized email generation
    - Context-aware content
    - Multiple tone options
    - Multi-language support (coming soon)
    """

    def __init__(self, llm_service: Optional[LocalLLMService] = None):
        """Initialize email template service."""
        self.llm = llm_service or get_llm_service()

    async def generate_email(
        self,
        template_type: EmailTemplateType,
        context: Dict,
        tone: EmailTone = EmailTone.PROFESSIONAL,
        custom_instructions: Optional[str] = None
    ) -> EmailContent:
        """
        Generate personalized email using local LLM.

        Args:
            template_type: Type of email to generate
            context: Dictionary with email context variables
            tone: Desired email tone
            custom_instructions: Additional instructions for generation

        Returns:
            EmailContent with subject and body
        """
        # Get template prompt
        prompt = self._get_template_prompt(template_type, context, tone, custom_instructions)

        # Generate email
        response = await self.llm.generate(
            prompt=prompt,
            temperature=0.7,  # Some creativity for natural language
            max_tokens=500,
            cache_key=self._get_cache_key(template_type, context, tone)
        )

        email_text = response.text

        # Parse subject and body
        subject, body = self._parse_email(email_text, template_type, context)

        return EmailContent(
            subject=subject,
            body=body,
            tone=tone.value,
            template_type=template_type.value,
            generated_at=datetime.utcnow(),
            tokens_used=response.tokens_used
        )

    async def personalize_template(
        self,
        template: str,
        recipient_name: str,
        recipient_context: Dict,
        tone: EmailTone = EmailTone.PROFESSIONAL
    ) -> str:
        """
        Personalize an existing template for a specific recipient.

        Args:
            template: Base email template
            recipient_name: Recipient's name
            recipient_context: Additional context about recipient
            tone: Desired tone

        Returns:
            Personalized email text
        """
        prompt = f"""Personalize this email template for the recipient.

Template:
{template}

Recipient: {recipient_name}
Context: {recipient_context}
Tone: {tone.value}

Make it feel personal but maintain the {tone.value} tone.
Keep the core message but adjust wording to feel handcrafted.
Do not change the fundamental meaning or requests.
"""

        response = await self.llm.generate(
            prompt=prompt,
            temperature=0.6,
            max_tokens=400
        )

        return response.text.strip()

    async def generate_subject_line(
        self,
        template_type: EmailTemplateType,
        context: Dict
    ) -> str:
        """Generate subject line for email."""
        manuscript_title = context.get('manuscript_title', 'your manuscript')

        subject_templates = {
            EmailTemplateType.REVIEW_INVITATION: f"Invitation to Review: {manuscript_title[:60]}",
            EmailTemplateType.REVIEW_REMINDER: f"Reminder: Review Request for {manuscript_title[:50]}",
            EmailTemplateType.REVIEW_THANK_YOU: f"Thank You for Your Review",
            EmailTemplateType.REVISION_REQUEST: f"Revision Request: {manuscript_title[:50]}",
            EmailTemplateType.MINOR_REVISIONS: f"Minor Revisions Required: {manuscript_title[:50]}",
            EmailTemplateType.MAJOR_REVISIONS: f"Major Revisions Required: {manuscript_title[:50]}",
            EmailTemplateType.ACCEPTANCE: f"Manuscript Accepted: {manuscript_title[:50]}",
            EmailTemplateType.REJECTION: f"Manuscript Decision: {manuscript_title[:50]}",
            EmailTemplateType.DESK_REJECT: f"Manuscript Decision: {manuscript_title[:50]}",
            EmailTemplateType.SUBMISSION_CONFIRMATION: f"Submission Confirmed: {manuscript_title[:50]}",
            EmailTemplateType.COPYEDITING_REQUEST: f"Copyediting Review Request: {manuscript_title[:40]}",
            EmailTemplateType.PRODUCTION_NOTIFICATION: f"Your Article in Production: {manuscript_title[:40]}",
            EmailTemplateType.PUBLICATION_ANNOUNCEMENT: f"Your Article is Published! {manuscript_title[:40]}",
        }

        return subject_templates.get(template_type, f"Regarding: {manuscript_title[:60]}")

    def _get_template_prompt(
        self,
        template_type: EmailTemplateType,
        context: Dict,
        tone: EmailTone,
        custom_instructions: Optional[str]
    ) -> str:
        """Get generation prompt for template type."""
        prompts = {
            EmailTemplateType.REVIEW_INVITATION: self._prompt_review_invitation,
            EmailTemplateType.REVIEW_REMINDER: self._prompt_review_reminder,
            EmailTemplateType.REVIEW_THANK_YOU: self._prompt_review_thank_you,
            EmailTemplateType.REVISION_REQUEST: self._prompt_revision_request,
            EmailTemplateType.ACCEPTANCE: self._prompt_acceptance,
            EmailTemplateType.REJECTION: self._prompt_rejection,
            EmailTemplateType.SUBMISSION_CONFIRMATION: self._prompt_submission_confirmation,
            EmailTemplateType.PUBLICATION_ANNOUNCEMENT: self._prompt_publication_announcement,
        }

        prompt_generator = prompts.get(template_type, self._prompt_generic)
        prompt = prompt_generator(context, tone)

        if custom_instructions:
            prompt += f"\n\nAdditional Instructions:\n{custom_instructions}"

        return prompt

    def _prompt_review_invitation(self, context: Dict, tone: EmailTone) -> str:
        """Generate prompt for review invitation email."""
        return f"""Generate a {tone.value} email inviting a reviewer to review a manuscript.

Context:
- Reviewer: {context.get('reviewer_name', '[Reviewer Name]')}
- Manuscript Title: {context.get('manuscript_title', '[Title]')}
- Manuscript Abstract: {context.get('abstract', '[Abstract]')[:200]}...
- Due Date: {context.get('due_date', '[Date]')}
- Why chosen: {context.get('match_reason', 'Your expertise matches this manuscript well')}

Tone: {tone.value}
Length: 150-200 words

Include:
1. Warm, personalized greeting
2. Brief manuscript overview
3. Why we specifically chose them (use match_reason)
4. Review timeline and due date
5. Clear accept/decline options
6. Thank them for considering

Write the complete email (subject and body). Format:
Subject: [subject line]

[email body]
"""

    def _prompt_review_reminder(self, context: Dict, tone: EmailTone) -> str:
        """Generate prompt for review reminder email."""
        return f"""Generate a gentle {tone.value} reminder email for an overdue review.

Context:
- Reviewer: {context.get('reviewer_name', '[Name]')}
- Manuscript Title: {context.get('manuscript_title', '[Title]')}
- Original Due Date: {context.get('original_due_date', '[Date]')}
- Days Overdue: {context.get('days_overdue', 'X')}

Tone: {tone.value} but understanding
Length: 100-150 words

Include:
1. Friendly greeting
2. Gentle reminder about the review
3. Understanding of their busy schedule
4. Request for update or revised timeline
5. Offer to help or reassign if needed

Write the complete email:
Subject: [subject line]

[email body]
"""

    def _prompt_review_thank_you(self, context: Dict, tone: EmailTone) -> str:
        """Generate prompt for review thank you email."""
        return f"""Generate a {tone.value} thank you email for completing a review.

Context:
- Reviewer: {context.get('reviewer_name', '[Name]')}
- Manuscript Title: {context.get('manuscript_title', '[Title]')}
- Quality Note: {context.get('quality_note', 'Your thorough review was very helpful')}

Tone: {tone.value} and appreciative
Length: 80-120 words

Include:
1. Sincere thanks
2. Acknowledgment of their time and expertise
3. Brief mention of value they provided
4. Invitation to review again in the future

Write the complete email:
Subject: [subject line]

[email body]
"""

    def _prompt_revision_request(self, context: Dict, tone: EmailTone) -> str:
        """Generate prompt for revision request email."""
        return f"""Generate a {tone.value} email requesting manuscript revisions.

Context:
- Author: {context.get('author_name', '[Author]')}
- Manuscript Title: {context.get('manuscript_title', '[Title]')}
- Revision Type: {context.get('revision_type', 'Minor Revisions')}
- Key Concerns: {context.get('concerns', '[List of concerns]')}
- Timeline: {context.get('timeline', '4 weeks')}

Tone: {tone.value} but encouraging
Length: 200-250 words

Include:
1. Clear statement of decision (revisions required)
2. Positive feedback on manuscript strengths
3. Clear summary of required changes
4. Timeline for resubmission
5. Offer to answer questions
6. Encouraging closing

Write the complete email:
Subject: [subject line]

[email body]
"""

    def _prompt_acceptance(self, context: Dict, tone: EmailTone) -> str:
        """Generate prompt for acceptance email."""
        return f"""Generate a {tone.value} congratulatory email for manuscript acceptance.

Context:
- Author: {context.get('author_name', '[Author]')}
- Manuscript Title: {context.get('manuscript_title', '[Title]')}
- Strengths: {context.get('strengths', 'significant contribution to the field')}
- Next Steps: {context.get('next_steps', 'copyediting and production')}
- Estimated Publication: {context.get('publication_timeline', '8-12 weeks')}

Tone: {tone.value} and congratulatory
Length: 150-200 words

Include:
1. Enthusiastic congratulations
2. What impressed us about the work
3. Clear next steps (copyediting, production)
4. Timeline to publication
5. Thank them for choosing our journal

Write the complete email:
Subject: [subject line]

[email body]
"""

    def _prompt_rejection(self, context: Dict, tone: EmailTone) -> str:
        """Generate prompt for rejection email."""
        return f"""Generate a {tone.value} rejection email that is respectful and constructive.

Context:
- Author: {context.get('author_name', '[Author]')}
- Manuscript Title: {context.get('manuscript_title', '[Title]')}
- Reason: {context.get('rejection_reason', 'does not align with journal scope')}
- Positive Aspects: {context.get('positive_aspects', 'well-written and thorough')}

Tone: {tone.value} and respectful
Length: 120-150 words

Include:
1. Clear but gentle statement of decision
2. Brief, constructive reason
3. Acknowledgment of positive aspects
4. Encouragement for future submissions elsewhere
5. Professional closing

Write the complete email:
Subject: [subject line]

[email body]
"""

    def _prompt_submission_confirmation(self, context: Dict, tone: EmailTone) -> str:
        """Generate prompt for submission confirmation email."""
        return f"""Generate a {tone.value} submission confirmation email.

Context:
- Author: {context.get('author_name', '[Author]')}
- Manuscript Title: {context.get('manuscript_title', '[Title]')}
- Manuscript ID: {context.get('manuscript_id', 'MS-XXXX-XXX')}
- Submission Date: {context.get('submission_date', '[Date]')}
- Next Step: {context.get('next_step', 'initial editorial review')}

Tone: {tone.value} and welcoming
Length: 100-120 words

Include:
1. Warm welcome and thanks for submitting
2. Confirmation of receipt
3. Manuscript ID for reference
4. What happens next
5. Timeline expectations
6. Contact information

Write the complete email:
Subject: [subject line]

[email body]
"""

    def _prompt_publication_announcement(self, context: Dict, tone: EmailTone) -> str:
        """Generate prompt for publication announcement email."""
        return f"""Generate an exciting {tone.value} publication announcement email.

Context:
- Author: {context.get('author_name', '[Author]')}
- Article Title: {context.get('article_title', '[Title]')}
- DOI: {context.get('doi', '10.XXXX/XXXXX')}
- Publication URL: {context.get('url', '[URL]')}
- Volume/Issue: {context.get('issue', 'Vol X, Issue Y')}

Tone: {tone.value} and celebratory
Length: 120-150 words

Include:
1. Exciting announcement of publication
2. Article details (title, DOI, URL)
3. Encourage sharing on social media
4. Thank them for publishing with us
5. Invitation to submit future work

Write the complete email:
Subject: [subject line]

[email body]
"""

    def _prompt_generic(self, context: Dict, tone: EmailTone) -> str:
        """Generic prompt for unlisted template types."""
        return f"""Generate a {tone.value} email for journal workflow communication.

Context:
{context}

Tone: {tone.value}
Length: 120-180 words

Write a professional, clear, and appropriate email based on the context provided.

Format:
Subject: [subject line]

[email body]
"""

    def _parse_email(self, email_text: str, template_type: EmailTemplateType, context: Dict) -> tuple[str, str]:
        """Parse subject and body from generated email."""
        lines = email_text.strip().split('\n')

        subject = ""
        body_lines = []
        found_subject = False

        for line in lines:
            line = line.strip()

            if not found_subject and line.lower().startswith('subject:'):
                subject = line[8:].strip()  # Remove "Subject:"
                found_subject = True
            elif found_subject and line:
                body_lines.append(line)

        # Clean up body
        body = '\n'.join(body_lines).strip()

        # Fallback if parsing failed
        if not subject:
            subject = self.generate_subject_line(template_type, context)

        if not body:
            body = email_text.strip()

        return subject, body

    def _get_cache_key(self, template_type: EmailTemplateType, context: Dict, tone: EmailTone) -> str:
        """Generate cache key for email generation."""
        import hashlib
        key_parts = [
            template_type.value,
            tone.value,
            str(context.get('manuscript_title', '')),
            str(context.get('recipient_name', ''))
        ]
        key_str = "|".join(key_parts)
        return hashlib.md5(key_str.encode()).hexdigest()


# Singleton instance
_email_template_service: Optional[AIEmailTemplateService] = None


def get_email_template_service() -> AIEmailTemplateService:
    """Get singleton email template service instance."""
    global _email_template_service
    if _email_template_service is None:
        _email_template_service = AIEmailTemplateService()
    return _email_template_service
