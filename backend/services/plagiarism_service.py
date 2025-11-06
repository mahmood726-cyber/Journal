"""
Local LLM-based plagiarism detection service.
Replaces paid services like iThenticate/Turnitin with zero-cost local AI.
"""
from typing import List, Dict, Optional, Tuple
from pydantic import BaseModel
from datetime import datetime
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import re
import asyncio
from sqlalchemy.orm import Session

from .llm_service import get_llm_service, LocalLLMService
from ..db.models import Manuscript
from ..core.config import settings


class PlagiarismMatch(BaseModel):
    """A potential plagiarism match."""
    manuscript_id: int
    manuscript_title: str
    similarity_score: float
    matched_sections: List[Tuple[str, str]]  # (source_section, matched_section)
    is_self_plagiarism: bool = False
    confidence: float
    match_type: str  # "direct_copy", "paraphrase", "idea_theft", "coincidence"
    explanation: str


class PlagiarismReport(BaseModel):
    """Complete plagiarism detection report."""
    manuscript_id: int
    overall_similarity: float
    highest_match_score: float
    matches: List[PlagiarismMatch]
    suspicious_sections: int
    recommendation: str  # "accept", "review", "reject"
    checked_at: datetime
    total_checks: int


class PlagiarismSection(BaseModel):
    """A section of text with its embedding."""
    text: str
    embedding: np.ndarray
    start_pos: int
    end_pos: int


class LocalPlagiarismService:
    """
    Local LLM-based plagiarism detection service.

    Features:
    - Semantic similarity detection using embeddings
    - Internal corpus checking (previous submissions)
    - Self-plagiarism detection (same author)
    - AI-powered match analysis
    - Detailed reporting
    """

    def __init__(
        self,
        llm_service: Optional[LocalLLMService] = None,
        similarity_threshold: float = None,
        min_match_length: int = None
    ):
        """Initialize plagiarism detection service."""
        self.llm = llm_service or get_llm_service()
        self.similarity_threshold = similarity_threshold or settings.PLAGIARISM_SIMILARITY_THRESHOLD
        self.min_match_length = min_match_length or settings.PLAGIARISM_MIN_MATCH_LENGTH

    async def check_plagiarism(
        self,
        manuscript_id: int,
        manuscript_text: str,
        title: str,
        author_ids: List[int],
        db: Session
    ) -> PlagiarismReport:
        """
        Check manuscript for potential plagiarism.

        Args:
            manuscript_id: ID of manuscript being checked
            manuscript_text: Full text of manuscript
            title: Manuscript title
            author_ids: List of author IDs (for self-plagiarism check)
            db: Database session

        Returns:
            PlagiarismReport with all findings
        """
        # 1. Split text into sections and generate embeddings
        sections = await self._create_sections(manuscript_text)

        # 2. Check against internal corpus
        internal_matches = await self._check_internal_corpus(
            sections,
            manuscript_id,
            author_ids,
            db
        )

        # 3. Analyze matches with LLM
        analyzed_matches = await self._analyze_matches(sections, internal_matches)

        # 4. Calculate overall metrics
        overall_similarity = max([m.similarity_score for m in analyzed_matches], default=0.0)
        suspicious_sections = sum(1 for m in analyzed_matches if m.confidence > 0.7)

        # 5. Generate recommendation
        recommendation = self._get_recommendation(overall_similarity, suspicious_sections)

        return PlagiarismReport(
            manuscript_id=manuscript_id,
            overall_similarity=overall_similarity,
            highest_match_score=overall_similarity,
            matches=analyzed_matches,
            suspicious_sections=suspicious_sections,
            recommendation=recommendation,
            checked_at=datetime.utcnow(),
            total_checks=len(analyzed_matches)
        )

    async def _create_sections(
        self,
        text: str,
        section_size: int = 500
    ) -> List[PlagiarismSection]:
        """
        Split text into overlapping sections and generate embeddings.

        Args:
            text: Input text
            section_size: Size of each section in words

        Returns:
            List of PlagiarismSection with embeddings
        """
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        sections = []
        current_section = []
        current_word_count = 0
        start_pos = 0

        for i, sentence in enumerate(sentences):
            words = sentence.split()
            current_section.append(sentence)
            current_word_count += len(words)

            # Create section when we reach section_size or end of text
            if current_word_count >= section_size or i == len(sentences) - 1:
                if current_word_count >= self.min_match_length:
                    section_text = '. '.join(current_section) + '.'

                    # Generate embedding
                    embedding_response = await self.llm.embed(
                        text=section_text,
                        cache_key=self._get_cache_key(section_text)
                    )

                    sections.append(PlagiarismSection(
                        text=section_text,
                        embedding=np.array(embedding_response.embedding),
                        start_pos=start_pos,
                        end_pos=start_pos + len(section_text)
                    ))

                # Overlap: keep last 20% of current section
                overlap_size = max(1, len(current_section) // 5)
                current_section = current_section[-overlap_size:]
                current_word_count = sum(len(s.split()) for s in current_section)
                start_pos += len(section_text)

        return sections

    async def _check_internal_corpus(
        self,
        sections: List[PlagiarismSection],
        current_manuscript_id: int,
        author_ids: List[int],
        db: Session
    ) -> List[Dict]:
        """
        Check sections against internal manuscript corpus.

        Args:
            sections: List of sections to check
            current_manuscript_id: ID of current manuscript (to exclude)
            author_ids: Author IDs for self-plagiarism detection
            db: Database session

        Returns:
            List of potential matches with metadata
        """
        # Get all published/submitted manuscripts (excluding current one)
        manuscripts = db.query(Manuscript).filter(
            Manuscript.id != current_manuscript_id,
            Manuscript.status.in_(['submitted', 'published', 'under_review'])
        ).all()

        matches = []

        # For each existing manuscript, check similarity
        for manuscript in manuscripts:
            # Skip if no text content
            if not manuscript.abstract:
                continue

            # Check if same author (for self-plagiarism flag)
            manuscript_author_ids = [author.id for author in manuscript.authors]
            is_self_plagiarism = any(aid in manuscript_author_ids for aid in author_ids)

            # Generate embeddings for this manuscript
            manuscript_text = f"{manuscript.title}\n\n{manuscript.abstract}"
            comparison_sections = await self._create_sections(manuscript_text)

            # Compare each section
            for section in sections:
                for comp_section in comparison_sections:
                    # Calculate cosine similarity
                    similarity = float(cosine_similarity(
                        section.embedding.reshape(1, -1),
                        comp_section.embedding.reshape(1, -1)
                    )[0][0])

                    # If similarity above threshold, record match
                    if similarity >= self.similarity_threshold:
                        matches.append({
                            'manuscript_id': manuscript.id,
                            'manuscript_title': manuscript.title,
                            'similarity_score': similarity,
                            'source_section': section.text,
                            'matched_section': comp_section.text,
                            'is_self_plagiarism': is_self_plagiarism
                        })

        # Sort by similarity (highest first)
        matches.sort(key=lambda x: x['similarity_score'], reverse=True)

        # Group by manuscript and keep top matches
        grouped_matches = {}
        for match in matches:
            mid = match['manuscript_id']
            if mid not in grouped_matches:
                grouped_matches[mid] = []
            grouped_matches[mid].append(match)

        # Flatten back to list, keeping top 3 sections per manuscript
        final_matches = []
        for manuscript_matches in grouped_matches.values():
            final_matches.extend(manuscript_matches[:3])

        return final_matches[:20]  # Return top 20 overall matches

    async def _analyze_matches(
        self,
        sections: List[PlagiarismSection],
        matches: List[Dict]
    ) -> List[PlagiarismMatch]:
        """
        Use LLM to analyze potential matches for actual plagiarism.

        Args:
            sections: Original sections
            matches: Potential matches from similarity search

        Returns:
            List of analyzed PlagiarismMatch objects
        """
        analyzed = []

        # Group matches by manuscript
        manuscript_matches = {}
        for match in matches:
            mid = match['manuscript_id']
            if mid not in manuscript_matches:
                manuscript_matches[mid] = []
            manuscript_matches[mid].append(match)

        # Analyze each manuscript's matches
        for manuscript_id, m_matches in manuscript_matches.items():
            # Combine all matched sections for this manuscript
            matched_sections = [
                (m['source_section'], m['matched_section'])
                for m in m_matches
            ]

            # Analyze with LLM
            analysis = await self._llm_analyze_match(
                matched_sections[0][0],  # First source section
                matched_sections[0][1],  # First matched section
            )

            analyzed.append(PlagiarismMatch(
                manuscript_id=manuscript_id,
                manuscript_title=m_matches[0]['manuscript_title'],
                similarity_score=m_matches[0]['similarity_score'],
                matched_sections=matched_sections,
                is_self_plagiarism=m_matches[0]['is_self_plagiarism'],
                confidence=analysis['confidence'],
                match_type=analysis['type'],
                explanation=analysis['explanation']
            ))

        return analyzed

    async def _llm_analyze_match(
        self,
        source_section: str,
        matched_section: str
    ) -> Dict:
        """
        Use LLM to determine if match is actual plagiarism.

        Args:
            source_section: Section from manuscript being checked
            matched_section: Similar section from existing manuscript

        Returns:
            Dict with is_plagiarism, confidence, type, explanation
        """
        prompt = f"""Analyze these two text sections for plagiarism.

Section A (New Submission):
{source_section[:500]}

Section B (Existing Manuscript):
{matched_section[:500]}

Determine if Section A plagiarizes Section B.

Consider:
1. Direct copying (word-for-word)
2. Paraphrasing (same ideas, different words)
3. Idea theft (same concepts/approach)
4. Coincidence (similar but independent work)
5. Common knowledge (acceptable similarity)

Respond in JSON format:
{{
    "is_plagiarism": true/false,
    "confidence": 0.0-1.0,
    "type": "direct_copy|paraphrase|idea_theft|coincidence",
    "explanation": "One sentence explanation"
}}"""

        try:
            response = await self.llm.generate(
                prompt=prompt,
                format="json",
                temperature=0.3,  # Lower temperature for more consistent analysis
                cache_key=self._get_cache_key(source_section, matched_section)
            )

            import json
            result = json.loads(response.text)

            return {
                'confidence': result.get('confidence', 0.5),
                'type': result.get('type', 'unknown'),
                'explanation': result.get('explanation', 'Unable to determine')
            }

        except Exception as e:
            # Fallback if LLM fails
            return {
                'confidence': 0.5,
                'type': 'unknown',
                'explanation': f'Analysis error: {str(e)}'
            }

    def _get_recommendation(
        self,
        overall_similarity: float,
        suspicious_sections: int
    ) -> str:
        """
        Generate recommendation based on plagiarism findings.

        Args:
            overall_similarity: Highest similarity score
            suspicious_sections: Number of suspicious sections

        Returns:
            Recommendation string
        """
        if overall_similarity >= 0.95 and suspicious_sections >= 3:
            return "reject"  # Very high similarity, likely plagiarism
        elif overall_similarity >= 0.85 or suspicious_sections >= 2:
            return "review"  # Moderate similarity, manual review needed
        else:
            return "accept"  # Low similarity, likely original

    def _get_cache_key(self, *args) -> str:
        """Generate cache key from text sections."""
        import hashlib
        key_str = "|".join(str(arg)[:100] for arg in args)
        return hashlib.md5(key_str.encode()).hexdigest()


# Singleton instance
_plagiarism_service: Optional[LocalPlagiarismService] = None


def get_plagiarism_service() -> LocalPlagiarismService:
    """Get singleton plagiarism service instance."""
    global _plagiarism_service
    if _plagiarism_service is None:
        _plagiarism_service = LocalPlagiarismService()
    return _plagiarism_service
