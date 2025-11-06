"""
DOI Registration Service for Crossref and DataCite.

Handles automated DOI registration for published articles.
"""
import requests
from typing import Dict, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class CrossrefDOIRegistrar:
    """Register DOIs with Crossref."""

    def __init__(self, username: str, password: str, doi_prefix: str, test_mode: bool = True):
        """
        Initialize Crossref DOI registrar.

        Args:
            username: Crossref username
            password: Crossref password
            doi_prefix: DOI prefix (e.g., 10.12345)
            test_mode: Use test API endpoint
        """
        self.username = username
        self.password = password
        self.doi_prefix = doi_prefix
        self.base_url = "https://test.crossref.org" if test_mode else "https://api.crossref.org"

    def register_doi(self, article_data: Dict) -> Dict:
        """
        Register a DOI with Crossref.

        Args:
            article_data: Dictionary containing article information
                - manuscript_id: Manuscript ID
                - title: Article title
                - authors: List of author dictionaries
                - published_date: Publication date
                - journal_title: Journal title
                - issn: Journal ISSN
                - volume: Volume number
                - issue: Issue number
                - page_start: Starting page (optional)
                - page_end: Ending page (optional)
                - url: Article URL

        Returns:
            Dictionary with DOI and registration status
        """
        try:
            # Generate DOI
            doi = self._generate_doi(article_data['manuscript_id'])

            # Create Crossref XML
            crossref_xml = self._create_crossref_xml(doi, article_data)

            # Submit to Crossref
            response = requests.post(
                f"{self.base_url}/servlet/deposit",
                auth=(self.username, self.password),
                files={'mdFile': ('crossref.xml', crossref_xml, 'application/xml')},
                params={'operation': 'doMDUpload', 'login_id': self.username, 'login_passwd': self.password}
            )

            if response.status_code == 200:
                logger.info(f"DOI registered successfully: {doi}")
                return {
                    'success': True,
                    'doi': doi,
                    'message': 'DOI registered successfully'
                }
            else:
                logger.error(f"DOI registration failed: {response.text}")
                return {
                    'success': False,
                    'error': response.text
                }

        except Exception as e:
            logger.error(f"Error registering DOI: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def _generate_doi(self, manuscript_id: str) -> str:
        """Generate DOI from manuscript ID."""
        year = datetime.now().year
        return f"{self.doi_prefix}/journal.{year}.{manuscript_id}"

    def _create_crossref_xml(self, doi: str, article_data: Dict) -> str:
        """Create Crossref deposit XML."""
        xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<doi_batch xmlns="http://www.crossref.org/schema/4.4.2"
           xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           version="4.4.2"
           xsi:schemaLocation="http://www.crossref.org/schema/4.4.2
           http://www.crossref.org/schemas/crossref4.4.2.xsd">
  <head>
    <doi_batch_id>{article_data['manuscript_id']}_{ datetime.now().strftime('%Y%m%d%H%M%S')}</doi_batch_id>
    <timestamp>{datetime.now().strftime('%Y%m%d%H%M%S')}</timestamp>
    <depositor>
      <depositor_name>{article_data.get('depositor_name', 'Journal System')}</depositor_name>
      <email_address>{article_data.get('depositor_email', 'admin@journal.com')}</email_address>
    </depositor>
    <registrant>{article_data.get('publisher', 'Publisher Name')}</registrant>
  </head>
  <body>
    <journal>
      <journal_metadata>
        <full_title>{article_data['journal_title']}</full_title>
        <issn media_type="electronic">{article_data['issn']}</issn>
      </journal_metadata>
      <journal_issue>
        <publication_date media_type="online">
          <year>{article_data['published_date'].year}</year>
          <month>{article_data['published_date'].month}</month>
          <day>{article_data['published_date'].day}</day>
        </publication_date>
        <journal_volume>
          <volume>{article_data['volume']}</volume>
        </journal_volume>
        <issue>{article_data.get('issue', '')}</issue>
      </journal_issue>
      <journal_article publication_type="full_text">
        <titles>
          <title>{article_data['title']}</title>
        </titles>
        <contributors>
'''

        # Add authors
        for i, author in enumerate(article_data['authors']):
            sequence = "first" if i == 0 else "additional"
            xml += f'''          <person_name sequence="{sequence}" contributor_role="author">
            <given_name>{author.get('given_names', '')}</given_name>
            <surname>{author.get('surname', '')}</surname>
'''
            if author.get('orcid'):
                xml += f'''            <ORCID>https://orcid.org/{author['orcid']}</ORCID>
'''
            xml += f'''          </person_name>
'''

        xml += f'''        </contributors>
        <publication_date media_type="online">
          <year>{article_data['published_date'].year}</year>
          <month>{article_data['published_date'].month}</month>
          <day>{article_data['published_date'].day}</day>
        </publication_date>
'''

        # Add pages if available
        if article_data.get('page_start'):
            xml += f'''        <pages>
          <first_page>{article_data['page_start']}</first_page>
'''
            if article_data.get('page_end'):
                xml += f'''          <last_page>{article_data['page_end']}</last_page>
'''
            xml += '''        </pages>
'''

        # Add DOI and resource URL
        xml += f'''        <doi_data>
          <doi>{doi}</doi>
          <resource>{article_data['url']}</resource>
        </doi_data>
      </journal_article>
    </journal>
  </body>
</doi_batch>'''

        return xml


class DataCiteDOIRegistrar:
    """Register DOIs with DataCite."""

    def __init__(self, repository_id: str, password: str, doi_prefix: str, test_mode: bool = True):
        """
        Initialize DataCite DOI registrar.

        Args:
            repository_id: DataCite repository ID
            password: DataCite password
            doi_prefix: DOI prefix
            test_mode: Use test API endpoint
        """
        self.repository_id = repository_id
        self.password = password
        self.doi_prefix = doi_prefix
        self.base_url = "https://api.test.datacite.org" if test_mode else "https://api.datacite.org"

    def register_doi(self, article_data: Dict) -> Dict:
        """
        Register a DOI with DataCite.

        Args:
            article_data: Article metadata dictionary

        Returns:
            Dictionary with DOI and registration status
        """
        try:
            # Generate DOI
            doi = self._generate_doi(article_data['manuscript_id'])

            # Create DataCite metadata
            metadata = self._create_datacite_metadata(doi, article_data)

            # Submit to DataCite
            response = requests.post(
                f"{self.base_url}/dois",
                json=metadata,
                auth=(self.repository_id, self.password),
                headers={'Content-Type': 'application/vnd.api+json'}
            )

            if response.status_code in [200, 201]:
                logger.info(f"DOI registered successfully with DataCite: {doi}")
                return {
                    'success': True,
                    'doi': doi,
                    'message': 'DOI registered successfully'
                }
            else:
                logger.error(f"DataCite DOI registration failed: {response.text}")
                return {
                    'success': False,
                    'error': response.text
                }

        except Exception as e:
            logger.error(f"Error registering DOI with DataCite: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def _generate_doi(self, manuscript_id: str) -> str:
        """Generate DOI from manuscript ID."""
        year = datetime.now().year
        return f"{self.doi_prefix}/journal.{year}.{manuscript_id}"

    def _create_datacite_metadata(self, doi: str, article_data: Dict) -> Dict:
        """Create DataCite metadata JSON."""
        creators = []
        for author in article_data['authors']:
            creator = {
                'name': f"{author.get('surname', '')}, {author.get('given_names', '')}",
                'givenName': author.get('given_names', ''),
                'familyName': author.get('surname', '')
            }
            if author.get('orcid'):
                creator['nameIdentifiers'] = [{
                    'nameIdentifier': f"https://orcid.org/{author['orcid']}",
                    'nameIdentifierScheme': 'ORCID'
                }]
            creators.append(creator)

        metadata = {
            'data': {
                'type': 'dois',
                'attributes': {
                    'doi': doi,
                    'url': article_data['url'],
                    'titles': [{
                        'title': article_data['title']
                    }],
                    'creators': creators,
                    'publisher': article_data.get('publisher', 'Publisher Name'),
                    'publicationYear': article_data['published_date'].year,
                    'resourceType': {
                        'resourceTypeGeneral': 'Text',
                        'resourceType': 'Journal Article'
                    },
                    'schemaVersion': 'http://datacite.org/schema/kernel-4'
                }
            }
        }

        return metadata


def register_doi_for_manuscript(manuscript_id: int, db_session, provider: str = "crossref") -> Dict:
    """
    Register DOI for a manuscript.

    Args:
        manuscript_id: Database ID of the manuscript
        db_session: Database session
        provider: DOI provider ('crossref' or 'datacite')

    Returns:
        Dictionary with registration result
    """
    from db.models import Manuscript, User
    from core.config import settings

    # Fetch manuscript
    manuscript = db_session.query(Manuscript).filter(Manuscript.id == manuscript_id).first()

    if not manuscript:
        raise ValueError(f"Manuscript {manuscript_id} not found")

    if not manuscript.published_at:
        raise ValueError("Manuscript must be published before registering DOI")

    # Prepare article data
    authors_data = []
    for author in manuscript.authors:
        author_dict = {
            'surname': author.full_name.split()[-1],
            'given_names': ' '.join(author.full_name.split()[:-1]),
            'orcid': author.orcid
        }
        authors_data.append(author_dict)

    article_data = {
        'manuscript_id': manuscript.manuscript_id,
        'title': manuscript.title,
        'authors': authors_data,
        'published_date': manuscript.published_at,
        'journal_title': settings.JOURNAL_TITLE,
        'issn': settings.JOURNAL_EISSN,
        'volume': manuscript.volume,
        'issue': manuscript.issue,
        'page_start': manuscript.page_start,
        'page_end': manuscript.page_end,
        'url': f"{settings.JOURNAL_URL}/article/{manuscript.manuscript_id}",
        'publisher': settings.JOURNAL_PUBLISHER,
        'depositor_name': settings.JOURNAL_PUBLISHER,
        'depositor_email': settings.JOURNAL_EMAIL
    }

    # Register DOI
    if provider == "crossref":
        registrar = CrossrefDOIRegistrar(
            username=settings.DOI_USERNAME,
            password=settings.DOI_PASSWORD,
            doi_prefix=settings.DOI_PREFIX,
            test_mode=settings.DOI_TEST_MODE
        )
    elif provider == "datacite":
        registrar = DataCiteDOIRegistrar(
            repository_id=settings.DATACITE_REPOSITORY_ID,
            password=settings.DATACITE_PASSWORD,
            doi_prefix=settings.DOI_PREFIX,
            test_mode=settings.DOI_TEST_MODE
        )
    else:
        raise ValueError(f"Unknown DOI provider: {provider}")

    result = registrar.register_doi(article_data)

    # Update manuscript with DOI if successful
    if result['success']:
        manuscript.doi = result['doi']
        db_session.commit()
        logger.info(f"DOI {result['doi']} assigned to manuscript {manuscript.manuscript_id}")

    return result


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python doi_registrar.py <manuscript_id> [provider]")
        sys.exit(1)

    manuscript_id = int(sys.argv[1])
    provider = sys.argv[2] if len(sys.argv) > 2 else "crossref"

    from db.base import SessionLocal

    db = SessionLocal()
    try:
        result = register_doi_for_manuscript(manuscript_id, db, provider)
        print(f"DOI Registration result: {result}")
    finally:
        db.close()
