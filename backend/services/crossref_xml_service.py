"""
Crossref XML Service

Generates Crossref XML for DOI registration and metadata deposit.
Follows Crossref schema 5.3.1 specifications.

Required for:
- DOI registration with Crossref
- Metadata updates
- Citation linking
- Content discovery

Reference: https://www.crossref.org/documentation/schema-library/
Schema: https://data.crossref.org/schemas/crossref5.3.1.xsd
"""

from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
from typing import List, Optional, Dict
from datetime import datetime
import secrets


class CrossrefXMLService:
    """Service for generating Crossref XML for DOI registration."""

    def __init__(self):
        self.schema_version = "5.3.1"
        self.xmlns = "http://www.crossref.org/schema/5.3.1"
        self.xmlns_xsi = "http://www.w3.org/2001/XMLSchema-instance"
        self.xsi_schema_location = f"{self.xmlns} http://www.crossref.org/schemas/crossref5.3.1.xsd"

    def generate_crossref_xml(
        self,
        manuscripts: List[dict],
        depositor_info: dict,
        journal_metadata: dict,
        batch_id: Optional[str] = None
    ) -> str:
        """
        Generate Crossref XML for DOI registration.

        Args:
            manuscripts: List of manuscript dictionaries
            depositor_info: Depositor contact information
            journal_metadata: Journal metadata (title, ISSN, etc.)
            batch_id: Optional batch ID (auto-generated if not provided)

        Returns:
            Crossref-compliant XML string
        """
        # Generate batch ID if not provided
        if not batch_id:
            batch_id = self._generate_batch_id()

        # Create root element with namespaces
        root = Element('doi_batch', {
            'xmlns': self.xmlns,
            'xmlns:xsi': self.xmlns_xsi,
            'xsi:schemaLocation': self.xsi_schema_location,
            'version': self.schema_version
        })

        # Head section
        head = self._create_head(batch_id, depositor_info)
        root.append(head)

        # Body section
        body = self._create_body(manuscripts, journal_metadata)
        root.append(body)

        return self._prettify_xml(root)

    def _generate_batch_id(self) -> str:
        """Generate unique batch ID."""
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        random_suffix = secrets.token_hex(4)
        return f"batch_{timestamp}_{random_suffix}"

    def _create_head(self, batch_id: str, depositor_info: dict) -> Element:
        """Create <head> element with batch and depositor info."""
        head = Element('head')

        # Batch ID
        doi_batch_id = SubElement(head, 'doi_batch_id')
        doi_batch_id.text = batch_id

        # Timestamp
        timestamp = SubElement(head, 'timestamp')
        timestamp.text = datetime.utcnow().strftime('%Y%m%d%H%M%S')

        # Depositor
        depositor = SubElement(head, 'depositor')

        depositor_name = SubElement(depositor, 'depositor_name')
        depositor_name.text = depositor_info.get('name', 'Journal Depositor')

        email_address = SubElement(depositor, 'email_address')
        email_address.text = depositor_info.get('email', 'deposits@journal.com')

        # Registrant (who owns the DOI prefix)
        registrant = SubElement(head, 'registrant')
        registrant.text = depositor_info.get('registrant', 'Diamond Open Access Journal')

        return head

    def _create_body(self, manuscripts: List[dict], journal_metadata: dict) -> Element:
        """Create <body> element with journal and article data."""
        body = Element('body')

        # Journal metadata
        journal = self._create_journal(journal_metadata, manuscripts)
        body.append(journal)

        return body

    def _create_journal(self, journal_metadata: dict, manuscripts: List[dict]) -> Element:
        """Create <journal> element."""
        journal = Element('journal')

        # Journal metadata
        journal_meta = SubElement(journal, 'journal_metadata', {'language': 'en'})

        # Full title
        full_title = SubElement(journal_meta, 'full_title')
        full_title.text = journal_metadata.get('title', 'Diamond Open Access Journal')

        # Abbreviated title
        if journal_metadata.get('abbrev'):
            abbrev_title = SubElement(journal_meta, 'abbrev_title')
            abbrev_title.text = journal_metadata['abbrev']

        # ISSN
        if journal_metadata.get('issn'):
            issn = SubElement(journal_meta, 'issn', {'media_type': 'electronic'})
            issn.text = journal_metadata['issn']

        # DOI data for journal (optional)
        if journal_metadata.get('journal_doi'):
            doi_data = SubElement(journal_meta, 'doi_data')
            doi = SubElement(doi_data, 'doi')
            doi.text = journal_metadata['journal_doi']
            resource = SubElement(doi_data, 'resource')
            resource.text = journal_metadata.get('journal_url', 'https://journal.example.com')

        # Journal issue (group manuscripts by issue)
        issues = self._group_manuscripts_by_issue(manuscripts)

        for issue_key, issue_manuscripts in issues.items():
            journal_issue = self._create_journal_issue(
                issue_manuscripts,
                journal_metadata
            )
            journal.append(journal_issue)

        return journal

    def _group_manuscripts_by_issue(self, manuscripts: List[dict]) -> Dict[str, List[dict]]:
        """Group manuscripts by volume and issue."""
        issues = {}

        for manuscript in manuscripts:
            volume = manuscript.get('volume', 0)
            issue = manuscript.get('issue', 0)
            key = f"v{volume}_i{issue}"

            if key not in issues:
                issues[key] = []
            issues[key].append(manuscript)

        return issues

    def _create_journal_issue(self, manuscripts: List[dict], journal_metadata: dict) -> Element:
        """Create <journal_issue> element."""
        journal_issue = Element('journal_issue')

        # Get volume and issue from first manuscript
        first_manuscript = manuscripts[0]

        # Publication date
        if first_manuscript.get('published_at'):
            pub_date = self._create_publication_date(first_manuscript['published_at'])
            journal_issue.append(pub_date)

        # Journal volume
        if first_manuscript.get('volume'):
            journal_volume = SubElement(journal_issue, 'journal_volume')
            volume = SubElement(journal_volume, 'volume')
            volume.text = str(first_manuscript['volume'])

        # Issue
        if first_manuscript.get('issue'):
            issue = SubElement(journal_issue, 'issue')
            issue.text = str(first_manuscript['issue'])

        # Articles in this issue
        for manuscript in manuscripts:
            article = self._create_journal_article(manuscript)
            journal_issue.append(article)

        return journal_issue

    def _create_publication_date(self, pub_date_str: str) -> Element:
        """Create <publication_date> element."""
        publication_date = Element('publication_date', {'media_type': 'online'})

        # Parse date
        if isinstance(pub_date_str, str):
            dt = datetime.fromisoformat(pub_date_str.replace('Z', '+00:00'))
        else:
            dt = pub_date_str

        month = SubElement(publication_date, 'month')
        month.text = f"{dt.month:02d}"

        day = SubElement(publication_date, 'day')
        day.text = f"{dt.day:02d}"

        year = SubElement(publication_date, 'year')
        year.text = str(dt.year)

        return publication_date

    def _create_journal_article(self, manuscript: dict) -> Element:
        """Create <journal_article> element."""
        journal_article = Element('journal_article', {
            'publication_type': 'full_text',
            'language': 'en'
        })

        # Titles
        titles = SubElement(journal_article, 'titles')
        title = SubElement(titles, 'title')
        title.text = manuscript['title']

        # Contributors (authors)
        if manuscript.get('authors'):
            contributors = self._create_contributors(manuscript['authors'])
            journal_article.append(contributors)

        # Abstract (optional)
        if manuscript.get('abstract'):
            jats_abstract = SubElement(journal_article, 'jats:abstract', {
                'xmlns:jats': 'http://www.ncbi.nlm.nih.gov/JATS1'
            })
            jats_p = SubElement(jats_abstract, 'jats:p')
            jats_p.text = manuscript['abstract']

        # Publication date
        if manuscript.get('published_at'):
            pub_date = self._create_publication_date(manuscript['published_at'])
            journal_article.append(pub_date)

        # Pages
        if manuscript.get('page_start'):
            pages = SubElement(journal_article, 'pages')
            first_page = SubElement(pages, 'first_page')
            first_page.text = str(manuscript['page_start'])

            if manuscript.get('page_end'):
                last_page = SubElement(pages, 'last_page')
                last_page.text = str(manuscript['page_end'])

        # Publisher item (manuscript ID)
        if manuscript.get('manuscript_id'):
            publisher_item = SubElement(journal_article, 'publisher_item')
            identifier = SubElement(publisher_item, 'identifier', {'id_type': 'pii'})
            identifier.text = manuscript['manuscript_id']

        # DOI data (required)
        if manuscript.get('doi'):
            doi_data = self._create_doi_data(manuscript)
            journal_article.append(doi_data)

        # Citation list (optional)
        if manuscript.get('references'):
            citation_list = self._create_citation_list(manuscript['references'])
            journal_article.append(citation_list)

        return journal_article

    def _create_contributors(self, authors: List[dict]) -> Element:
        """Create <contributors> element with authors."""
        contributors = Element('contributors')

        for idx, author in enumerate(authors):
            person_name = SubElement(contributors, 'person_name', {
                'sequence': 'first' if idx == 0 else 'additional',
                'contributor_role': 'author'
            })

            # Given name
            if author.get('first_name'):
                given_name = SubElement(person_name, 'given_name')
                given_name.text = author['first_name']
            elif author.get('full_name'):
                given_name = SubElement(person_name, 'given_name')
                parts = author['full_name'].split()
                given_name.text = ' '.join(parts[:-1]) if len(parts) > 1 else ''

            # Surname
            if author.get('last_name'):
                surname = SubElement(person_name, 'surname')
                surname.text = author['last_name']
            elif author.get('full_name'):
                surname = SubElement(person_name, 'surname')
                surname.text = author['full_name'].split()[-1]

            # ORCID
            if author.get('orcid'):
                orcid = SubElement(person_name, 'ORCID')
                orcid.text = f"https://orcid.org/{author['orcid']}"

            # Affiliation
            if author.get('affiliation'):
                affiliations = SubElement(person_name, 'affiliations')
                institution = SubElement(affiliations, 'institution')
                institution_name = SubElement(institution, 'institution_name')
                institution_name.text = author['affiliation']

        return contributors

    def _create_doi_data(self, manuscript: dict) -> Element:
        """Create <doi_data> element."""
        doi_data = Element('doi_data')

        # DOI
        doi = SubElement(doi_data, 'doi')
        doi.text = manuscript['doi']

        # Resource URL (where the article can be accessed)
        resource = SubElement(doi_data, 'resource')
        if manuscript.get('url'):
            resource.text = manuscript['url']
        else:
            # Construct URL from manuscript ID
            resource.text = f"https://journal.example.com/article/{manuscript.get('manuscript_id', manuscript['doi'])}"

        # Collection (for text mining)
        collection = SubElement(doi_data, 'collection', {'property': 'text-mining'})
        item = SubElement(collection, 'item')
        item_resource = SubElement(item, 'resource', {'mime_type': 'application/pdf'})
        if manuscript.get('pdf_url'):
            item_resource.text = manuscript['pdf_url']
        else:
            item_resource.text = f"{resource.text}/pdf"

        return doi_data

    def _create_citation_list(self, references: List[dict]) -> Element:
        """Create <citation_list> element."""
        citation_list = Element('citation_list')

        for idx, ref in enumerate(references, 1):
            citation = SubElement(citation_list, 'citation', {'key': f"ref{idx}"})

            # Unstructured citation (simplest approach)
            unstructured_citation = SubElement(citation, 'unstructured_citation')
            unstructured_citation.text = ref.get('citation', str(ref))

            # DOI if available
            if ref.get('doi'):
                doi = SubElement(citation, 'doi')
                doi.text = ref['doi']

        return citation_list

    def _prettify_xml(self, elem: Element) -> str:
        """Return a pretty-printed XML string."""
        rough_string = tostring(elem, encoding='utf-8', method='xml')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ", encoding='UTF-8').decode('utf-8')


def generate_crossref_xml_for_manuscript(
    manuscript: dict,
    depositor_info: dict,
    journal_metadata: dict,
    batch_id: Optional[str] = None
) -> str:
    """
    Convenience function to generate Crossref XML for a single manuscript.

    Args:
        manuscript: Manuscript dictionary with metadata
        depositor_info: Depositor contact information
        journal_metadata: Journal metadata
        batch_id: Optional batch ID

    Returns:
        Crossref-compliant XML string
    """
    service = CrossrefXMLService()
    return service.generate_crossref_xml(
        manuscripts=[manuscript],
        depositor_info=depositor_info,
        journal_metadata=journal_metadata,
        batch_id=batch_id
    )
