"""
JATS XML Generator for PubMed Central Submission.

Generates JATS (Journal Article Tag Suite) XML format required for PubMed Central.
Based on NLM JATS Version 1.2 specification.
"""
from lxml import etree
from datetime import datetime
from typing import List, Dict, Optional
import os


class JATSGenerator:
    """Generate JATS XML for journal articles."""

    def __init__(self, journal_meta: Dict):
        """
        Initialize JATS generator with journal metadata.

        Args:
            journal_meta: Dictionary containing journal information
                - title: Journal title
                - issn: Print ISSN
                - eissn: Electronic ISSN
                - publisher_name: Publisher name
                - journal_id: Journal ID
        """
        self.journal_meta = journal_meta

    def generate_jats_xml(self, article_data: Dict, output_path: str) -> str:
        """
        Generate JATS XML for an article.

        Args:
            article_data: Dictionary containing article information
                - article_id: Manuscript ID
                - doi: DOI
                - title: Article title
                - abstract: Article abstract
                - authors: List of author dictionaries
                - keywords: List of keywords
                - received_date: Date received
                - accepted_date: Date accepted
                - published_date: Date published
                - volume: Volume number
                - issue: Issue number
                - page_start: Starting page (optional)
                - page_end: Ending page (optional)
                - article_type: Type of article
                - body: Article body content (optional)
                - references: List of references (optional)

            output_path: Path to save the XML file

        Returns:
            Path to the generated XML file
        """
        # Create root element with JATS namespace
        root = etree.Element('article', nsmap={
            None: 'http://jats.nlm.nih.gov',
            'xlink': 'http://www.w3.org/1999/xlink',
            'mml': 'http://www.w3.org/1998/Math/MathML'
        })

        root.set('article-type', article_data.get('article_type', 'research-article'))
        root.set('{http://www.w3.org/XML/1998/namespace}lang', 'en')

        # Front matter
        front = etree.SubElement(root, 'front')

        # Journal metadata
        self._add_journal_meta(front)

        # Article metadata
        self._add_article_meta(front, article_data)

        # Body
        if article_data.get('body'):
            body = etree.SubElement(root, 'body')
            self._add_body_content(body, article_data['body'])

        # Back matter (references)
        if article_data.get('references'):
            back = etree.SubElement(root, 'back')
            self._add_references(back, article_data['references'])

        # Write to file with pretty formatting
        tree = etree.ElementTree(root)
        tree.write(
            output_path,
            pretty_print=True,
            xml_declaration=True,
            encoding='UTF-8',
            doctype='<!DOCTYPE article PUBLIC "-//NLM//DTD JATS (Z39.96) Journal Archiving and Interchange DTD v1.2 20190208//EN" "JATS-archivearticle1.dtd">'
        )

        return output_path

    def _add_journal_meta(self, front: etree.Element) -> None:
        """Add journal metadata section."""
        journal_meta = etree.SubElement(front, 'journal-meta')

        # Journal ID
        journal_id = etree.SubElement(journal_meta, 'journal-id')
        journal_id.set('journal-id-type', 'publisher-id')
        journal_id.text = self.journal_meta.get('journal_id', '')

        # Journal title
        journal_title_group = etree.SubElement(journal_meta, 'journal-title-group')
        journal_title = etree.SubElement(journal_title_group, 'journal-title')
        journal_title.text = self.journal_meta['title']

        # ISSN
        if self.journal_meta.get('issn'):
            issn = etree.SubElement(journal_meta, 'issn')
            issn.set('pub-type', 'ppub')
            issn.text = self.journal_meta['issn']

        if self.journal_meta.get('eissn'):
            eissn = etree.SubElement(journal_meta, 'issn')
            eissn.set('pub-type', 'epub')
            eissn.text = self.journal_meta['eissn']

        # Publisher
        publisher = etree.SubElement(journal_meta, 'publisher')
        publisher_name = etree.SubElement(publisher, 'publisher-name')
        publisher_name.text = self.journal_meta['publisher_name']

    def _add_article_meta(self, front: etree.Element, article_data: Dict) -> None:
        """Add article metadata section."""
        article_meta = etree.SubElement(front, 'article-meta')

        # Article ID
        article_id = etree.SubElement(article_meta, 'article-id')
        article_id.set('pub-id-type', 'publisher-id')
        article_id.text = article_data['article_id']

        # DOI
        if article_data.get('doi'):
            doi = etree.SubElement(article_meta, 'article-id')
            doi.set('pub-id-type', 'doi')
            doi.text = article_data['doi']

        # Article categories (optional)
        if article_data.get('categories'):
            article_categories = etree.SubElement(article_meta, 'article-categories')
            subj_group = etree.SubElement(article_categories, 'subj-group')
            subj_group.set('subj-group-type', 'heading')
            for category in article_data['categories']:
                subject = etree.SubElement(subj_group, 'subject')
                subject.text = category

        # Title
        title_group = etree.SubElement(article_meta, 'title-group')
        article_title = etree.SubElement(title_group, 'article-title')
        article_title.text = article_data['title']

        # Authors
        if article_data.get('authors'):
            contrib_group = etree.SubElement(article_meta, 'contrib-group')
            for author in article_data['authors']:
                self._add_author(contrib_group, author)

        # Affiliations
        if article_data.get('affiliations'):
            for idx, affiliation in enumerate(article_data['affiliations'], 1):
                aff = etree.SubElement(article_meta, 'aff')
                aff.set('id', f'aff{idx}')
                aff.text = affiliation

        # Publication dates
        if article_data.get('received_date'):
            self._add_date(article_meta, 'received', article_data['received_date'])
        if article_data.get('accepted_date'):
            self._add_date(article_meta, 'accepted', article_data['accepted_date'])
        if article_data.get('published_date'):
            self._add_date(article_meta, 'epub', article_data['published_date'])

        # Volume and Issue
        if article_data.get('volume'):
            volume = etree.SubElement(article_meta, 'volume')
            volume.text = str(article_data['volume'])

        if article_data.get('issue'):
            issue = etree.SubElement(article_meta, 'issue')
            issue.text = str(article_data['issue'])

        # Page numbers (if applicable)
        if article_data.get('page_start'):
            fpage = etree.SubElement(article_meta, 'fpage')
            fpage.text = str(article_data['page_start'])

        if article_data.get('page_end'):
            lpage = etree.SubElement(article_meta, 'lpage')
            lpage.text = str(article_data['page_end'])

        # Permissions (Open Access)
        permissions = etree.SubElement(article_meta, 'permissions')
        copyright_statement = etree.SubElement(permissions, 'copyright-statement')
        copyright_statement.text = f"© {datetime.now().year} {article_data['authors'][0]['surname']} et al."

        copyright_year = etree.SubElement(permissions, 'copyright-year')
        copyright_year.text = str(datetime.now().year)

        license_elem = etree.SubElement(permissions, 'license')
        license_elem.set('license-type', 'open-access')
        license_elem.set('{http://www.w3.org/1999/xlink}href', 'http://creativecommons.org/licenses/by/4.0/')

        license_p = etree.SubElement(license_elem, 'license-p')
        license_p.text = "This is an open access article distributed under the terms of the Creative Commons Attribution License (CC BY 4.0)."

        # Abstract
        if article_data.get('abstract'):
            abstract = etree.SubElement(article_meta, 'abstract')
            abstract_p = etree.SubElement(abstract, 'p')
            abstract_p.text = article_data['abstract']

        # Keywords
        if article_data.get('keywords'):
            kwd_group = etree.SubElement(article_meta, 'kwd-group')
            kwd_group.set('kwd-group-type', 'author')
            for keyword in article_data['keywords']:
                kwd = etree.SubElement(kwd_group, 'kwd')
                kwd.text = keyword

    def _add_author(self, contrib_group: etree.Element, author_data: Dict) -> None:
        """Add a single author to the contributor group."""
        contrib = etree.SubElement(contrib_group, 'contrib')
        contrib.set('contrib-type', 'author')

        if author_data.get('is_corresponding'):
            contrib.set('corresp', 'yes')

        name = etree.SubElement(contrib, 'name')

        surname = etree.SubElement(name, 'surname')
        surname.text = author_data['surname']

        given_names = etree.SubElement(name, 'given-names')
        given_names.text = author_data['given_names']

        # ORCID
        if author_data.get('orcid'):
            contrib_id = etree.SubElement(contrib, 'contrib-id')
            contrib_id.set('contrib-id-type', 'orcid')
            contrib_id.text = author_data['orcid']

        # Email (for corresponding author)
        if author_data.get('email') and author_data.get('is_corresponding'):
            email = etree.SubElement(contrib, 'email')
            email.text = author_data['email']

        # Affiliation reference
        if author_data.get('aff_id'):
            xref = etree.SubElement(contrib, 'xref')
            xref.set('ref-type', 'aff')
            xref.set('rid', author_data['aff_id'])

    def _add_date(self, parent: etree.Element, date_type: str, date_value: datetime) -> None:
        """Add a date element."""
        date_elem = etree.SubElement(parent, 'date')
        date_elem.set('date-type', date_type)

        day = etree.SubElement(date_elem, 'day')
        day.text = str(date_value.day)

        month = etree.SubElement(date_elem, 'month')
        month.text = str(date_value.month)

        year = etree.SubElement(date_elem, 'year')
        year.text = str(date_value.year)

    def _add_body_content(self, body: etree.Element, content: str) -> None:
        """Add body content (simplified version)."""
        sec = etree.SubElement(body, 'sec')
        p = etree.SubElement(sec, 'p')
        p.text = content

    def _add_references(self, back: etree.Element, references: List[Dict]) -> None:
        """Add references section."""
        ref_list = etree.SubElement(back, 'ref-list')

        for idx, ref in enumerate(references, 1):
            ref_elem = etree.SubElement(ref_list, 'ref')
            ref_elem.set('id', f'ref{idx}')

            element_citation = etree.SubElement(ref_elem, 'element-citation')
            element_citation.set('publication-type', ref.get('type', 'journal'))

            # Add reference details based on type
            if ref.get('authors'):
                person_group = etree.SubElement(element_citation, 'person-group')
                person_group.set('person-group-type', 'author')
                for author in ref['authors']:
                    name = etree.SubElement(person_group, 'name')
                    surname = etree.SubElement(name, 'surname')
                    surname.text = author.get('surname', '')
                    given_names = etree.SubElement(name, 'given-names')
                    given_names.text = author.get('given_names', '')

            if ref.get('title'):
                article_title = etree.SubElement(element_citation, 'article-title')
                article_title.text = ref['title']

            if ref.get('journal'):
                source = etree.SubElement(element_citation, 'source')
                source.text = ref['journal']

            if ref.get('year'):
                year = etree.SubElement(element_citation, 'year')
                year.text = str(ref['year'])

            if ref.get('doi'):
                pub_id = etree.SubElement(element_citation, 'pub-id')
                pub_id.set('pub-id-type', 'doi')
                pub_id.text = ref['doi']


def generate_jats_for_article(manuscript_id: int, db_session) -> str:
    """
    Generate JATS XML for a manuscript from the database.

    Args:
        manuscript_id: ID of the manuscript
        db_session: Database session

    Returns:
        Path to generated JATS XML file
    """
    from db.models import Manuscript, User
    from core.config import settings

    # Fetch manuscript from database
    manuscript = db_session.query(Manuscript).filter(Manuscript.id == manuscript_id).first()

    if not manuscript:
        raise ValueError(f"Manuscript {manuscript_id} not found")

    # Prepare journal metadata
    journal_meta = {
        'title': settings.JOURNAL_TITLE,
        'issn': settings.JOURNAL_ISSN,
        'eissn': settings.JOURNAL_EISSN,
        'publisher_name': settings.JOURNAL_PUBLISHER,
        'journal_id': settings.JOURNAL_SHORT_TITLE or settings.JOURNAL_TITLE
    }

    # Prepare article data
    authors_data = []
    for idx, author in enumerate(manuscript.authors, 1):
        author_dict = {
            'surname': author.full_name.split()[-1],
            'given_names': ' '.join(author.full_name.split()[:-1]),
            'email': author.email if idx == 1 else None,  # First author is corresponding
            'is_corresponding': idx == 1,
            'orcid': author.orcid,
            'aff_id': f'aff{idx}'
        }
        authors_data.append(author_dict)

    affiliations = [author.affiliation for author in manuscript.authors if author.affiliation]

    article_data = {
        'article_id': manuscript.manuscript_id,
        'doi': manuscript.doi,
        'title': manuscript.title,
        'abstract': manuscript.abstract,
        'authors': authors_data,
        'affiliations': affiliations,
        'keywords': manuscript.keywords,
        'received_date': manuscript.created_at,
        'accepted_date': manuscript.published_at,  # Assuming acceptance = publication for now
        'published_date': manuscript.published_at,
        'volume': manuscript.volume,
        'issue': manuscript.issue,
        'page_start': manuscript.page_start,
        'page_end': manuscript.page_end,
        'article_type': manuscript.article_type or 'research-article'
    }

    # Generate JATS XML
    generator = JATSGenerator(journal_meta)
    output_path = f"./uploads/jats/{manuscript.manuscript_id}.xml"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    return generator.generate_jats_xml(article_data, output_path)
