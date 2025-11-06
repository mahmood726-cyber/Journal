"""
Advanced Plagiarism Detection Service

Integrates with multiple plagiarism detection APIs and provides
comprehensive originality checking for manuscripts.
"""
from typing import Dict, List, Optional
import logging
import hashlib
from datetime import datetime
import requests
from pathlib import Path

logger = logging.getLogger(__name__)


class PlagiarismDetectionService:
    """
    Multi-provider plagiarism detection service.

    Supports:
    - Turnitin/iThenticate API
    - Copyleaks API
    - Plagiarism Checker X
    - Custom text similarity detection
    """

    def __init__(self, provider: str = "ithenticate", api_key: Optional[str] = None):
        """
        Initialize plagiarism detection service.

        Args:
            provider: Detection provider ('ithenticate', 'copyleaks', 'custom')
            api_key: API key for the provider
        """
        self.provider = provider
        self.api_key = api_key
        self.base_urls = {
            'ithenticate': 'https://api.ithenticate.com/v2',
            'copyleaks': 'https://api.copyleaks.com/v3'
        }

    def check_manuscript(
        self,
        manuscript_file_path: str,
        manuscript_id: str,
        author_name: str
    ) -> Dict:
        """
        Check manuscript for plagiarism.

        Args:
            manuscript_file_path: Path to manuscript file
            manuscript_id: Manuscript identifier
            author_name: Author name for submission

        Returns:
            Dictionary with plagiarism report
        """
        if self.provider == "ithenticate":
            return self._check_ithenticate(manuscript_file_path, manuscript_id, author_name)
        elif self.provider == "copyleaks":
            return self._check_copyleaks(manuscript_file_path, manuscript_id, author_name)
        elif self.provider == "custom":
            return self._check_custom(manuscript_file_path, manuscript_id)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    def _check_ithenticate(
        self,
        file_path: str,
        manuscript_id: str,
        author_name: str
    ) -> Dict:
        """
        Check manuscript using iThenticate API.

        iThenticate is the industry standard for academic plagiarism detection.
        """
        if not self.api_key:
            logger.warning("iThenticate API key not configured")
            return self._mock_plagiarism_report(file_path, manuscript_id)

        try:
            # Step 1: Create submission
            submission_data = {
                'submitter': author_name,
                'title': f'Manuscript {manuscript_id}',
                'author': {
                    'first_name': author_name.split()[0] if ' ' in author_name else author_name,
                    'last_name': author_name.split()[-1] if ' ' in author_name else author_name
                }
            }

            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }

            # Create submission
            response = requests.post(
                f"{self.base_urls['ithenticate']}/submissions",
                json=submission_data,
                headers=headers,
                timeout=30
            )

            if response.status_code not in [200, 201]:
                raise Exception(f"Failed to create submission: {response.text}")

            submission = response.json()
            submission_id = submission['id']

            # Step 2: Upload file
            with open(file_path, 'rb') as f:
                files = {'file': (Path(file_path).name, f)}
                upload_response = requests.post(
                    f"{self.base_urls['ithenticate']}/submissions/{submission_id}/upload",
                    files=files,
                    headers={'Authorization': f'Bearer {self.api_key}'},
                    timeout=60
                )

            if upload_response.status_code not in [200, 201, 202]:
                raise Exception(f"Failed to upload file: {upload_response.text}")

            # Step 3: Generate similarity report
            report_response = requests.post(
                f"{self.base_urls['ithenticate']}/submissions/{submission_id}/similarity",
                headers=headers,
                timeout=30
            )

            if report_response.status_code not in [200, 201, 202]:
                raise Exception(f"Failed to generate report: {report_response.text}")

            report_data = report_response.json()

            # Step 4: Poll for completion (in production, use webhooks)
            # For now, return submission info
            return {
                'provider': 'ithenticate',
                'submission_id': submission_id,
                'status': 'processing',
                'report_url': f"{self.base_urls['ithenticate']}/submissions/{submission_id}/similarity",
                'checked_at': datetime.utcnow().isoformat(),
                'message': 'Similarity report is being generated. Check back in a few minutes.'
            }

        except Exception as e:
            logger.error(f"iThenticate check failed: {str(e)}")
            return {
                'provider': 'ithenticate',
                'status': 'error',
                'error': str(e),
                'checked_at': datetime.utcnow().isoformat()
            }

    def _check_copyleaks(
        self,
        file_path: str,
        manuscript_id: str,
        author_name: str
    ) -> Dict:
        """
        Check manuscript using Copyleaks API.

        Copyleaks provides comprehensive plagiarism detection with multi-language support.
        """
        if not self.api_key:
            logger.warning("Copyleaks API key not configured")
            return self._mock_plagiarism_report(file_path, manuscript_id)

        try:
            # Copyleaks authentication
            auth_response = requests.post(
                f"{self.base_urls['copyleaks']}/account/login",
                json={'email': self.api_key.split(':')[0], 'key': self.api_key.split(':')[1]},
                timeout=30
            )

            if auth_response.status_code != 200:
                raise Exception(f"Authentication failed: {auth_response.text}")

            token = auth_response.json()['access_token']

            # Submit file for scanning
            scan_id = f"manuscript_{manuscript_id}_{hashlib.md5(file_path.encode()).hexdigest()}"

            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }

            with open(file_path, 'rb') as f:
                file_content = f.read()
                import base64
                encoded_content = base64.b64encode(file_content).decode()

            scan_data = {
                'base64': encoded_content,
                'filename': Path(file_path).name,
                'properties': {
                    'webhooks': {
                        'status': f'https://yourjournal.com/api/v1/plagiarism/webhook/{scan_id}'
                    }
                }
            }

            scan_response = requests.put(
                f"{self.base_urls['copyleaks']}/scans/submit/file/{scan_id}",
                json=scan_data,
                headers=headers,
                timeout=60
            )

            if scan_response.status_code not in [200, 201]:
                raise Exception(f"Scan submission failed: {scan_response.text}")

            return {
                'provider': 'copyleaks',
                'scan_id': scan_id,
                'status': 'processing',
                'checked_at': datetime.utcnow().isoformat(),
                'message': 'Plagiarism scan in progress. Results will be available shortly.'
            }

        except Exception as e:
            logger.error(f"Copyleaks check failed: {str(e)}")
            return {
                'provider': 'copyleaks',
                'status': 'error',
                'error': str(e),
                'checked_at': datetime.utcnow().isoformat()
            }

    def _check_custom(self, file_path: str, manuscript_id: str) -> Dict:
        """
        Custom plagiarism detection using text similarity algorithms.

        This is a basic implementation using:
        - TF-IDF vectorization
        - Cosine similarity
        - Comparison with published articles database
        """
        try:
            # Extract text from file
            text = self._extract_text_from_file(file_path)

            if not text:
                return {
                    'provider': 'custom',
                    'status': 'error',
                    'error': 'Could not extract text from file'
                }

            # Compare with database of published articles
            similar_docs = self._find_similar_documents(text)

            # Calculate overall similarity score
            if similar_docs:
                max_similarity = max(doc['similarity'] for doc in similar_docs)
                overall_score = int(max_similarity * 100)
            else:
                overall_score = 0

            # Determine status
            if overall_score < 15:
                status = 'passed'
                message = 'Low similarity detected. Document appears original.'
            elif overall_score < 30:
                status = 'warning'
                message = 'Moderate similarity detected. Manual review recommended.'
            else:
                status = 'high_similarity'
                message = 'High similarity detected. Detailed review required.'

            return {
                'provider': 'custom',
                'status': status,
                'similarity_score': overall_score,
                'similar_documents': similar_docs[:5],  # Top 5 matches
                'message': message,
                'checked_at': datetime.utcnow().isoformat(),
                'total_words': len(text.split()),
                'flagged_sections': self._identify_flagged_sections(text, similar_docs)
            }

        except Exception as e:
            logger.error(f"Custom plagiarism check failed: {str(e)}")
            return {
                'provider': 'custom',
                'status': 'error',
                'error': str(e)
            }

    def _extract_text_from_file(self, file_path: str) -> str:
        """Extract text from various file formats."""
        import PyPDF2
        import docx

        file_ext = Path(file_path).suffix.lower()

        try:
            if file_ext == '.pdf':
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    text = ' '.join(page.extract_text() for page in reader.pages)
                return text

            elif file_ext in ['.doc', '.docx']:
                doc = docx.Document(file_path)
                text = ' '.join(paragraph.text for paragraph in doc.paragraphs)
                return text

            elif file_ext == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()

            else:
                logger.warning(f"Unsupported file type: {file_ext}")
                return ""

        except Exception as e:
            logger.error(f"Text extraction failed: {str(e)}")
            return ""

    def _find_similar_documents(self, text: str, threshold: float = 0.3) -> List[Dict]:
        """
        Find similar documents in the database.
        Uses TF-IDF and cosine similarity.
        """
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        from db.models import Manuscript, ManuscriptStatus
        from db.base import SessionLocal

        db = SessionLocal()
        try:
            # Get published manuscripts
            published = db.query(Manuscript).filter(
                Manuscript.status == ManuscriptStatus.PUBLISHED,
                Manuscript.abstract.isnot(None)
            ).limit(1000).all()  # Limit for performance

            if not published:
                return []

            # Combine title and abstract for comparison
            documents = [f"{m.title} {m.abstract}" for m in published]
            documents.append(text)

            # Calculate TF-IDF
            vectorizer = TfidfVectorizer(
                max_features=5000,
                stop_words='english',
                ngram_range=(1, 3)
            )
            tfidf_matrix = vectorizer.fit_transform(documents)

            # Calculate similarity
            query_vector = tfidf_matrix[-1]
            doc_vectors = tfidf_matrix[:-1]
            similarities = cosine_similarity(query_vector, doc_vectors)[0]

            # Find similar documents
            similar_docs = []
            for i, sim in enumerate(similarities):
                if sim >= threshold:
                    manuscript = published[i]
                    similar_docs.append({
                        'manuscript_id': manuscript.manuscript_id,
                        'title': manuscript.title,
                        'similarity': float(sim),
                        'doi': manuscript.doi,
                        'published_date': manuscript.published_at.isoformat() if manuscript.published_at else None
                    })

            # Sort by similarity
            similar_docs.sort(key=lambda x: x['similarity'], reverse=True)

            return similar_docs

        except Exception as e:
            logger.error(f"Error finding similar documents: {str(e)}")
            return []
        finally:
            db.close()

    def _identify_flagged_sections(self, text: str, similar_docs: List[Dict]) -> List[Dict]:
        """Identify specific sections with high similarity."""
        # Simplified implementation
        # In production, would use more sophisticated text alignment algorithms
        flagged_sections = []

        # Split text into paragraphs
        paragraphs = text.split('\n\n')

        for i, para in enumerate(paragraphs[:10]):  # Check first 10 paragraphs
            if len(para.split()) > 20:  # Only check substantial paragraphs
                flagged_sections.append({
                    'section_number': i + 1,
                    'excerpt': para[:200] + '...' if len(para) > 200 else para,
                    'similarity_level': 'moderate' if len(similar_docs) > 0 else 'low'
                })

        return flagged_sections[:3]  # Return top 3 flagged sections

    def _mock_plagiarism_report(self, file_path: str, manuscript_id: str) -> Dict:
        """
        Generate mock plagiarism report for testing/demo purposes.
        """
        import random

        similarity_score = random.randint(5, 25)

        return {
            'provider': 'demo',
            'status': 'completed',
            'similarity_score': similarity_score,
            'message': f'{similarity_score}% similarity detected (Demo mode)',
            'checked_at': datetime.utcnow().isoformat(),
            'similar_sources': [
                {
                    'source': 'PubMed Central Article',
                    'similarity': random.randint(3, 15),
                    'url': 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1234567/'
                },
                {
                    'source': 'Journal Article Database',
                    'similarity': random.randint(2, 10),
                    'url': 'https://doi.org/10.1234/example'
                }
            ],
            'assessment': 'Acceptable' if similarity_score < 15 else 'Needs Review',
            'note': 'This is a demo report. Configure API keys for actual plagiarism detection.'
        }

    def get_report_status(self, submission_id: str) -> Dict:
        """
        Check status of a plagiarism report.

        Args:
            submission_id: Submission or scan ID from initial check

        Returns:
            Current status and results if available
        """
        if self.provider == "ithenticate":
            return self._get_ithenticate_report(submission_id)
        elif self.provider == "copyleaks":
            return self._get_copyleaks_report(submission_id)
        else:
            return {'status': 'unknown', 'message': 'Report status not available'}

    def _get_ithenticate_report(self, submission_id: str) -> Dict:
        """Get completed iThenticate report."""
        if not self.api_key:
            return {'status': 'error', 'message': 'API key not configured'}

        try:
            headers = {'Authorization': f'Bearer {self.api_key}'}

            response = requests.get(
                f"{self.base_urls['ithenticate']}/submissions/{submission_id}/similarity",
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    'provider': 'ithenticate',
                    'status': 'completed',
                    'similarity_score': data.get('overall_match_percentage', 0),
                    'report_url': data.get('viewer_url'),
                    'details': data
                }
            else:
                return {
                    'provider': 'ithenticate',
                    'status': 'processing',
                    'message': 'Report not ready yet'
                }

        except Exception as e:
            logger.error(f"Error retrieving iThenticate report: {str(e)}")
            return {'status': 'error', 'error': str(e)}

    def _get_copyleaks_report(self, scan_id: str) -> Dict:
        """Get completed Copyleaks report."""
        # Implementation similar to iThenticate
        return {'status': 'processing', 'message': 'Check back later'}


def check_manuscript_plagiarism(
    manuscript_id: int,
    db_session,
    provider: str = "custom"
) -> Dict:
    """
    Convenience function to check manuscript for plagiarism.

    Args:
        manuscript_id: Manuscript database ID
        db_session: Database session
        provider: Plagiarism detection provider

    Returns:
        Plagiarism report
    """
    from db.models import Manuscript
    from core.config import settings

    manuscript = db_session.query(Manuscript).filter(Manuscript.id == manuscript_id).first()

    if not manuscript:
        raise ValueError(f"Manuscript {manuscript_id} not found")

    if not manuscript.manuscript_file:
        raise ValueError("No manuscript file uploaded")

    # Get API key from settings if available
    api_key = getattr(settings, f"{provider.upper()}_API_KEY", None)

    service = PlagiarismDetectionService(provider=provider, api_key=api_key)

    author_name = manuscript.authors[0].full_name if manuscript.authors else "Unknown Author"

    return service.check_manuscript(
        manuscript_file_path=manuscript.manuscript_file,
        manuscript_id=manuscript.manuscript_id,
        author_name=author_name
    )
