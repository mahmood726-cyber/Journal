"""
PubMed XML Export Service

Generates bibliographic information in PubMed standard publisher data format XML
for indexing in NLM PubMed/MEDLINE.

Reference: https://www.ncbi.nlm.nih.gov/books/NBK3828/
PubMed DTD: https://dtd.nlm.nih.gov/ncbi/pubmed/out/pubmed_190101.dtd
"""

from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
from typing import List, Optional
from datetime import datetime


class PubMedXMLService:
    """Service for generating PubMed-compliant XML for manuscript metadata."""

    def __init__(self):
        self.version = "1.0"
        self.encoding = "UTF-8"

    def generate_pubmed_xml(
        self,
        manuscripts: List[dict],
        journal_title: str,
        journal_abbrev: str,
        issn: str,
        publisher: str = "Diamond Open Access Journal"
    ) -> str:
        """
        Generate PubMed XML for one or more manuscripts.

        Args:
            manuscripts: List of manuscript dictionaries with metadata
            journal_title: Full journal title
            journal_abbrev: Journal title abbreviation
            issn: Journal ISSN
            publisher: Publisher name

        Returns:
            Formatted XML string
        """
        # Create root element
        root = Element('ArticleSet')

        for manuscript in manuscripts:
            article = self._create_article_element(
                manuscript,
                journal_title,
                journal_abbrev,
                issn,
                publisher
            )
            root.append(article)

        # Pretty print XML
        return self._prettify_xml(root)

    def _create_article_element(
        self,
        manuscript: dict,
        journal_title: str,
        journal_abbrev: str,
        issn: str,
        publisher: str
    ) -> Element:
        """Create Article element for a single manuscript."""
        article = Element('Article')

        # Journal metadata
        journal = SubElement(article, 'Journal')

        publisher_elem = SubElement(journal, 'PublisherName')
        publisher_elem.text = publisher

        journal_title_elem = SubElement(journal, 'JournalTitle')
        journal_title_elem.text = journal_title

        issn_elem = SubElement(journal, 'Issn')
        issn_elem.text = issn

        # Volume and issue
        if manuscript.get('volume'):
            volume = SubElement(journal, 'Volume')
            volume.text = str(manuscript['volume'])

        if manuscript.get('issue'):
            issue = SubElement(journal, 'Issue')
            issue.text = str(manuscript['issue'])

        # Publication date
        if manuscript.get('published_at'):
            pub_date = self._create_pubdate_element(manuscript['published_at'])
            journal.append(pub_date)

        # Article title
        article_title = SubElement(article, 'ArticleTitle')
        article_title.text = manuscript['title']

        # Pagination
        if manuscript.get('page_start') and manuscript.get('page_end'):
            pagination = SubElement(article, 'Pagination')
            medline_pgn = SubElement(pagination, 'MedlinePgn')
            medline_pgn.text = f"{manuscript['page_start']}-{manuscript['page_end']}"
        elif manuscript.get('page_start'):
            pagination = SubElement(article, 'Pagination')
            start_page = SubElement(pagination, 'StartPage')
            start_page.text = str(manuscript['page_start'])

        # Abstract
        if manuscript.get('abstract'):
            abstract = SubElement(article, 'Abstract')
            abstract_text = SubElement(abstract, 'AbstractText')
            abstract_text.text = manuscript['abstract']

        # Authors
        if manuscript.get('authors'):
            author_list = SubElement(article, 'AuthorList')
            for author_data in manuscript['authors']:
                author = self._create_author_element(author_data)
                author_list.append(author)

        # Language
        language = SubElement(article, 'Language')
        language.text = manuscript.get('language', 'eng')

        # Publication type
        pub_type_list = SubElement(article, 'PublicationTypeList')
        pub_type = SubElement(pub_type_list, 'PublicationType')
        pub_type.text = manuscript.get('article_type', 'Journal Article')

        # Article IDs (DOI, PII, etc.)
        if manuscript.get('doi') or manuscript.get('manuscript_id'):
            article_id_list = SubElement(article, 'ArticleIdList')

            if manuscript.get('doi'):
                doi_elem = SubElement(article_id_list, 'ArticleId', IdType='doi')
                doi_elem.text = manuscript['doi']

            if manuscript.get('manuscript_id'):
                pii_elem = SubElement(article_id_list, 'ArticleId', IdType='pii')
                pii_elem.text = manuscript['manuscript_id']

        return article

    def _create_author_element(self, author_data: dict) -> Element:
        """Create Author element."""
        author = Element('Author')

        # Last name (required)
        if author_data.get('last_name'):
            last_name = SubElement(author, 'LastName')
            last_name.text = author_data['last_name']

        # First name
        if author_data.get('first_name'):
            fore_name = SubElement(author, 'ForeName')
            fore_name.text = author_data['first_name']

        # Initials
        if author_data.get('first_name'):
            initials = SubElement(author, 'Initials')
            initials.text = author_data['first_name'][0]

        # Affiliation
        if author_data.get('affiliation'):
            affiliation = SubElement(author, 'Affiliation')
            affiliation.text = author_data['affiliation']

        # ORCID
        if author_data.get('orcid'):
            identifier = SubElement(author, 'Identifier', Source='ORCID')
            identifier.text = author_data['orcid']

        return author

    def _create_pubdate_element(self, pub_date_str: str) -> Element:
        """Create PubDate element from date string."""
        pub_date = Element('PubDate')

        # Parse date
        if isinstance(pub_date_str, str):
            dt = datetime.fromisoformat(pub_date_str.replace('Z', '+00:00'))
        else:
            dt = pub_date_str

        # Year (required)
        year = SubElement(pub_date, 'Year')
        year.text = str(dt.year)

        # Month
        month = SubElement(pub_date, 'Month')
        month.text = dt.strftime('%b')  # Jan, Feb, Mar, etc.

        # Day
        day = SubElement(pub_date, 'Day')
        day.text = str(dt.day)

        return pub_date

    def _prettify_xml(self, elem: Element) -> str:
        """Return a pretty-printed XML string."""
        rough_string = tostring(elem, encoding='utf-8', method='xml')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ", encoding='UTF-8').decode('utf-8')


def generate_pubmed_xml_for_manuscript(
    manuscript: dict,
    journal_title: str = "Diamond Open Access Journal",
    journal_abbrev: str = "Diamond OA J",
    issn: str = "2XXX-XXXX",
    publisher: str = "Diamond Open Access Publisher"
) -> str:
    """
    Convenience function to generate PubMed XML for a single manuscript.

    Args:
        manuscript: Manuscript dictionary with metadata
        journal_title: Full journal title
        journal_abbrev: Journal abbreviation
        issn: Journal ISSN
        publisher: Publisher name

    Returns:
        PubMed-compliant XML string
    """
    service = PubMedXMLService()
    return service.generate_pubmed_xml(
        manuscripts=[manuscript],
        journal_title=journal_title,
        journal_abbrev=journal_abbrev,
        issn=issn,
        publisher=publisher
    )
