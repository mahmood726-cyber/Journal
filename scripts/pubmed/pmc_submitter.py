"""
PubMed Central (PMC) Submission System.

Handles automated submission of JATS XML files to PMC via FTP.
Follows PMC submission guidelines and requirements.
"""
import ftplib
import os
from datetime import datetime
from typing import Optional, Dict
import logging
from pathlib import Path


logger = logging.getLogger(__name__)


class PMCSubmitter:
    """Handle submissions to PubMed Central via FTP."""

    def __init__(self, ftp_host: str, username: str, password: str, base_path: str = "/upload"):
        """
        Initialize PMC submitter.

        Args:
            ftp_host: PMC FTP host (usually ftp.ncbi.nlm.nih.gov)
            username: PMC FTP username
            password: PMC FTP password
            base_path: Base path on FTP server for uploads
        """
        self.ftp_host = ftp_host
        self.username = username
        self.password = password
        self.base_path = base_path

    def submit_article(
        self,
        jats_xml_path: str,
        pdf_path: Optional[str] = None,
        supplementary_files: Optional[list] = None,
        article_id: str = None
    ) -> Dict[str, any]:
        """
        Submit an article to PubMed Central.

        PMC Submission Requirements:
        1. JATS XML file (required) - must validate against JATS DTD
        2. PDF file (recommended)
        3. Figures/images referenced in XML
        4. Supplementary files (optional)

        Args:
            jats_xml_path: Path to JATS XML file
            pdf_path: Path to PDF file (optional but recommended)
            supplementary_files: List of paths to supplementary files
            article_id: Article identifier for tracking

        Returns:
            Dictionary with submission results
        """
        if not os.path.exists(jats_xml_path):
            raise FileNotFoundError(f"JATS XML file not found: {jats_xml_path}")

        # Validate JATS XML before submission
        if not self._validate_jats_xml(jats_xml_path):
            raise ValueError("JATS XML validation failed")

        submission_result = {
            'article_id': article_id,
            'submitted_at': datetime.utcnow(),
            'files_submitted': [],
            'success': False,
            'error': None
        }

        try:
            # Connect to PMC FTP server
            ftp = ftplib.FTP(self.ftp_host)
            ftp.login(self.username, self.password)
            logger.info(f"Connected to PMC FTP server: {self.ftp_host}")

            # Create submission directory if needed
            submission_dir = f"{self.base_path}/{article_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            try:
                ftp.mkd(submission_dir)
                ftp.cwd(submission_dir)
                logger.info(f"Created submission directory: {submission_dir}")
            except ftplib.error_perm:
                ftp.cwd(submission_dir)

            # Upload JATS XML file
            xml_filename = os.path.basename(jats_xml_path)
            with open(jats_xml_path, 'rb') as f:
                ftp.storbinary(f'STOR {xml_filename}', f)
            submission_result['files_submitted'].append(xml_filename)
            logger.info(f"Uploaded JATS XML: {xml_filename}")

            # Upload PDF if provided
            if pdf_path and os.path.exists(pdf_path):
                pdf_filename = os.path.basename(pdf_path)
                with open(pdf_path, 'rb') as f:
                    ftp.storbinary(f'STOR {pdf_filename}', f)
                submission_result['files_submitted'].append(pdf_filename)
                logger.info(f"Uploaded PDF: {pdf_filename}")

            # Upload supplementary files
            if supplementary_files:
                for supp_file in supplementary_files:
                    if os.path.exists(supp_file):
                        supp_filename = os.path.basename(supp_file)
                        with open(supp_file, 'rb') as f:
                            ftp.storbinary(f'STOR {supp_filename}', f)
                        submission_result['files_submitted'].append(supp_filename)
                        logger.info(f"Uploaded supplementary file: {supp_filename}")

            # Close FTP connection
            ftp.quit()
            logger.info("FTP connection closed")

            submission_result['success'] = True
            submission_result['submission_dir'] = submission_dir

        except Exception as e:
            logger.error(f"Error submitting to PMC: {str(e)}")
            submission_result['error'] = str(e)

        return submission_result

    def _validate_jats_xml(self, xml_path: str) -> bool:
        """
        Validate JATS XML against DTD.

        Args:
            xml_path: Path to XML file

        Returns:
            True if valid, False otherwise
        """
        try:
            from lxml import etree

            # Parse XML
            with open(xml_path, 'rb') as f:
                doc = etree.parse(f)

            # Basic validation - check for required elements
            root = doc.getroot()
            required_elements = [
                './/front/journal-meta',
                './/front/article-meta',
                './/front/article-meta/title-group/article-title',
                './/front/article-meta/contrib-group',
            ]

            for element_path in required_elements:
                if root.find(element_path, namespaces=root.nsmap) is None:
                    logger.error(f"Missing required element: {element_path}")
                    return False

            logger.info("JATS XML validation passed")
            return True

        except Exception as e:
            logger.error(f"XML validation error: {str(e)}")
            return False

    def check_submission_status(self, submission_dir: str) -> Dict[str, any]:
        """
        Check status of a submission (if PMC provides status files).

        Note: PMC typically sends status updates via email.
        This method checks for any status files in the submission directory.

        Args:
            submission_dir: Submission directory path on FTP server

        Returns:
            Status information
        """
        try:
            ftp = ftplib.FTP(self.ftp_host)
            ftp.login(self.username, self.password)
            ftp.cwd(submission_dir)

            files = []
            ftp.retrlines('LIST', files.append)
            ftp.quit()

            return {
                'submission_dir': submission_dir,
                'files': files,
                'checked_at': datetime.utcnow()
            }

        except Exception as e:
            logger.error(f"Error checking submission status: {str(e)}")
            return {'error': str(e)}


def submit_article_to_pmc(manuscript_id: int, db_session) -> Dict[str, any]:
    """
    Submit a manuscript to PubMed Central.

    Args:
        manuscript_id: Database ID of the manuscript
        db_session: Database session

    Returns:
        Submission result dictionary
    """
    from db.models import Manuscript
    from core.config import settings
    from scripts.jats.jats_generator import generate_jats_for_article

    # Fetch manuscript
    manuscript = db_session.query(Manuscript).filter(Manuscript.id == manuscript_id).first()

    if not manuscript:
        raise ValueError(f"Manuscript {manuscript_id} not found")

    if not manuscript.published_at:
        raise ValueError("Manuscript must be published before submitting to PMC")

    # Generate JATS XML if not already generated
    if not manuscript.jats_xml_file or not os.path.exists(manuscript.jats_xml_file):
        jats_path = generate_jats_for_article(manuscript_id, db_session)
        manuscript.jats_xml_file = jats_path
        db_session.commit()
    else:
        jats_path = manuscript.jats_xml_file

    # Prepare supplementary files
    supplementary_files = []
    if manuscript.supplementary_files:
        supplementary_files = manuscript.supplementary_files

    # Initialize PMC submitter
    submitter = PMCSubmitter(
        ftp_host=settings.PMC_FTP_HOST,
        username=settings.PMC_FTP_USER,
        password=settings.PMC_FTP_PASSWORD,
        base_path=settings.PMC_FTP_PATH
    )

    # Submit to PMC
    result = submitter.submit_article(
        jats_xml_path=jats_path,
        pdf_path=manuscript.pdf_file,
        supplementary_files=supplementary_files,
        article_id=manuscript.manuscript_id
    )

    # Update manuscript record
    if result['success']:
        manuscript.submitted_to_pmc = True
        manuscript.pmc_submission_date = datetime.utcnow()
        db_session.commit()
        logger.info(f"Manuscript {manuscript.manuscript_id} submitted to PMC successfully")
    else:
        logger.error(f"Failed to submit manuscript {manuscript.manuscript_id} to PMC: {result.get('error')}")

    return result


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) < 2:
        print("Usage: python pmc_submitter.py <manuscript_id>")
        sys.exit(1)

    manuscript_id = int(sys.argv[1])

    from db.base import SessionLocal

    db = SessionLocal()
    try:
        result = submit_article_to_pmc(manuscript_id, db)
        print(f"Submission result: {result}")
    finally:
        db.close()
