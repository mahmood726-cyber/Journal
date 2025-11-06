"""
JATS XML Service

Generates Journal Article Tag Suite (JATS) XML 1.3 for scholarly articles.
JATS is the NISO standard format for journal article metadata and full text.

Required for:
- PubMed Central (PMC)
- Europe PMC
- Crossref full-text deposits
- Professional publishing workflows

Reference: https://jats.nlm.nih.gov/
JATS DTD: https://jats.nlm.nih.gov/publishing/1.3/
"""

from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
from typing import List, Optional, Dict
from datetime import datetime
import html


class JATSXMLService:
    """Service for generating JATS 1.3 compliant XML for manuscripts."""

    def __init__(self, jats_version: str = "1.3"):
        self.jats_version = jats_version
        self.dtd_public_id = f"-//NLM//DTD JATS (Z39.96) Journal Publishing DTD v{jats_version} 20210830//EN"
        self.dtd_system_id = f"https://jats.nlm.nih.gov/publishing/{jats_version}/JATS-journalpublishing1.dtd"

    def generate_jats_xml(
        self,
        manuscript: dict,
        journal_meta: dict,
        include_body: bool = False,
        include_references: bool = True
    ) -> str:
        """
        Generate complete JATS XML for a manuscript.

        Args:
            manuscript: Manuscript data dictionary
            journal_meta: Journal metadata dictionary
            include_body: Include article body text (if available)
            include_references: Include references section

        Returns:
            JATS-compliant XML string
        """
        # Create root element with namespaces
        root = Element('article', {
            'xmlns:xlink': 'http://www.w3.org/1999/xlink',
            'xmlns:mml': 'http://www.w3.org/1998/Math/MathML',
            'dtd-version': self.jats_version,
            'article-type': self._map_article_type(manuscript.get('article_type', 'research-article'))
        })

        # Front matter
        front = self._create_front_matter(manuscript, journal_meta)
        root.append(front)

        # Body (optional)
        if include_body and manuscript.get('body_content'):
            body = self._create_body(manuscript['body_content'])
            root.append(body)

        # Back matter
        if include_references or manuscript.get('acknowledgments'):
            back = self._create_back_matter(manuscript, include_references)
            root.append(back)

        # Pretty print with DOCTYPE
        return self._prettify_with_doctype(root)

    def _create_front_matter(self, manuscript: dict, journal_meta: dict) -> Element:
        """Create <front> element with journal and article metadata."""
        front = Element('front')

        # Journal metadata
        journal_meta_elem = self._create_journal_meta(journal_meta)
        front.append(journal_meta_elem)

        # Article metadata
        article_meta = self._create_article_meta(manuscript)
        front.append(article_meta)

        return front

    def _create_journal_meta(self, journal_meta: dict) -> Element:
        """Create <journal-meta> element."""
        j_meta = Element('journal-meta')

        # Journal ID
        if journal_meta.get('journal_id'):
            journal_id = SubElement(j_meta, 'journal-id', {'journal-id-type': 'publisher-id'})
            journal_id.text = journal_meta['journal_id']

        # Journal title
        journal_title_group = SubElement(j_meta, 'journal-title-group')
        journal_title = SubElement(journal_title_group, 'journal-title')
        journal_title.text = journal_meta.get('title', 'Diamond Open Access Journal')

        if journal_meta.get('abbrev'):
            abbrev_journal_title = SubElement(journal_title_group, 'abbrev-journal-title')
            abbrev_journal_title.text = journal_meta['abbrev']

        # ISSN
        if journal_meta.get('issn'):
            issn = SubElement(j_meta, 'issn', {'pub-type': 'epub'})
            issn.text = journal_meta['issn']

        # Publisher
        publisher = SubElement(j_meta, 'publisher')
        publisher_name = SubElement(publisher, 'publisher-name')
        publisher_name.text = journal_meta.get('publisher', 'Diamond Open Access Publisher')

        return j_meta

    def _create_article_meta(self, manuscript: dict) -> Element:
        """Create <article-meta> element."""
        a_meta = Element('article-meta')

        # Article IDs
        if manuscript.get('doi'):
            article_id_doi = SubElement(a_meta, 'article-id', {'pub-id-type': 'doi'})
            article_id_doi.text = manuscript['doi']

        if manuscript.get('manuscript_id'):
            article_id_publisher = SubElement(a_meta, 'article-id', {'pub-id-type': 'publisher-id'})
            article_id_publisher.text = manuscript['manuscript_id']

        # Article categories (optional)
        if manuscript.get('article_type') or manuscript.get('subject'):
            article_categories = SubElement(a_meta, 'article-categories')
            subj_group = SubElement(article_categories, 'subj-group', {'subj-group-type': 'heading'})
            subject = SubElement(subj_group, 'subject')
            subject.text = manuscript.get('subject', 'Research Article')

        # Title group
        title_group = SubElement(a_meta, 'title-group')
        article_title = SubElement(title_group, 'article-title')
        article_title.text = manuscript['title']

        # Subtitle (if exists)
        if manuscript.get('subtitle'):
            subtitle = SubElement(title_group, 'subtitle')
            subtitle.text = manuscript['subtitle']

        # Contributors (authors)
        if manuscript.get('authors'):
            contrib_group = self._create_contrib_group(manuscript['authors'])
            a_meta.append(contrib_group)

        # Affiliations
        if manuscript.get('authors'):
            affiliations = self._extract_affiliations(manuscript['authors'])
            for idx, aff_text in enumerate(affiliations, 1):
                aff = SubElement(a_meta, 'aff', {'id': f'aff{idx}'})
                aff.text = aff_text

        # Publication date
        if manuscript.get('published_at'):
            pub_date = self._create_pub_date(manuscript['published_at'])
            a_meta.append(pub_date)

        # Volume, issue, pages
        if manuscript.get('volume'):
            volume = SubElement(a_meta, 'volume')
            volume.text = str(manuscript['volume'])

        if manuscript.get('issue'):
            issue = SubElement(a_meta, 'issue')
            issue.text = str(manuscript['issue'])

        # Electronic location identifier (e-pages for online-only journals)
        if manuscript.get('page_start'):
            if manuscript.get('page_end'):
                fpage = SubElement(a_meta, 'fpage')
                fpage.text = str(manuscript['page_start'])
                lpage = SubElement(a_meta, 'lpage')
                lpage.text = str(manuscript['page_end'])
            else:
                elocation_id = SubElement(a_meta, 'elocation-id')
                elocation_id.text = str(manuscript['page_start'])

        # Permissions (license)
        permissions = self._create_permissions(manuscript)
        a_meta.append(permissions)

        # Abstract
        if manuscript.get('abstract'):
            abstract = self._create_abstract(manuscript['abstract'])
            a_meta.append(abstract)

        # Keywords
        if manuscript.get('keywords'):
            kwd_group = self._create_keyword_group(manuscript['keywords'])
            a_meta.append(kwd_group)

        # Funding (if available)
        if manuscript.get('funding'):
            funding_group = self._create_funding_group(manuscript['funding'])
            a_meta.append(funding_group)

        return a_meta

    def _create_contrib_group(self, authors: List[dict]) -> Element:
        """Create <contrib-group> element with authors."""
        contrib_group = Element('contrib-group')

        for idx, author in enumerate(authors, 1):
            contrib = SubElement(contrib_group, 'contrib', {'contrib-type': 'author'})

            # Name
            name = SubElement(contrib, 'name')

            if author.get('last_name'):
                surname = SubElement(name, 'surname')
                surname.text = author['last_name']
            elif author.get('full_name'):
                # Split full name
                parts = author['full_name'].split()
                surname = SubElement(name, 'surname')
                surname.text = parts[-1] if len(parts) > 1 else parts[0]

            if author.get('first_name'):
                given_names = SubElement(name, 'given-names')
                given_names.text = author['first_name']
            elif author.get('full_name') and len(author['full_name'].split()) > 1:
                given_names = SubElement(name, 'given-names')
                given_names.text = ' '.join(author['full_name'].split()[:-1])

            # ORCID
            if author.get('orcid'):
                contrib_id = SubElement(contrib, 'contrib-id', {
                    'contrib-id-type': 'orcid',
                    'authenticated': 'true'
                })
                contrib_id.text = f"https://orcid.org/{author['orcid']}"

            # Email
            if author.get('email'):
                email = SubElement(contrib, 'email')
                email.text = author['email']

            # Affiliation reference
            if author.get('affiliation'):
                xref = SubElement(contrib, 'xref', {
                    'ref-type': 'aff',
                    'rid': f'aff{idx}'
                })

        return contrib_group

    def _extract_affiliations(self, authors: List[dict]) -> List[str]:
        """Extract unique affiliations from authors."""
        affiliations = []
        seen = set()

        for author in authors:
            aff = author.get('affiliation', '')
            if aff and aff not in seen:
                affiliations.append(aff)
                seen.add(aff)

        return affiliations

    def _create_pub_date(self, pub_date_str: str) -> Element:
        """Create <pub-date> element."""
        pub_date = Element('pub-date', {'pub-type': 'epub'})

        # Parse date
        if isinstance(pub_date_str, str):
            dt = datetime.fromisoformat(pub_date_str.replace('Z', '+00:00'))
        else:
            dt = pub_date_str

        day = SubElement(pub_date, 'day')
        day.text = str(dt.day)

        month = SubElement(pub_date, 'month')
        month.text = str(dt.month)

        year = SubElement(pub_date, 'year')
        year.text = str(dt.year)

        return pub_date

    def _create_permissions(self, manuscript: dict) -> Element:
        """Create <permissions> element with licensing information."""
        permissions = Element('permissions')

        # Copyright statement
        if manuscript.get('copyright_year') or manuscript.get('published_at'):
            copyright_year_elem = SubElement(permissions, 'copyright-year')
            if manuscript.get('copyright_year'):
                copyright_year_elem.text = str(manuscript['copyright_year'])
            elif manuscript.get('published_at'):
                dt = datetime.fromisoformat(manuscript['published_at'].replace('Z', '+00:00'))
                copyright_year_elem.text = str(dt.year)

        # Copyright holder
        if manuscript.get('copyright_holder'):
            copyright_holder = SubElement(permissions, 'copyright-holder')
            copyright_holder.text = manuscript['copyright_holder']

        # License (default to CC BY 4.0 for Diamond OA)
        license_elem = SubElement(permissions, 'license', {
            'license-type': 'open-access',
            'xlink:href': 'https://creativecommons.org/licenses/by/4.0/'
        })
        license_p = SubElement(license_elem, 'license-p')
        license_p.text = ('This is an open access article distributed under the terms of the '
                         'Creative Commons Attribution License (CC BY 4.0), which permits '
                         'unrestricted use, distribution, and reproduction in any medium, '
                         'provided the original author and source are credited.')

        return permissions

    def _create_abstract(self, abstract_text: str) -> Element:
        """Create <abstract> element."""
        abstract = Element('abstract')
        p = SubElement(abstract, 'p')
        p.text = abstract_text
        return abstract

    def _create_keyword_group(self, keywords: List[str]) -> Element:
        """Create <kwd-group> element."""
        kwd_group = Element('kwd-group', {'kwd-group-type': 'author'})

        for keyword in keywords:
            kwd = SubElement(kwd_group, 'kwd')
            kwd.text = keyword

        return kwd_group

    def _create_funding_group(self, funding: List[dict]) -> Element:
        """Create <funding-group> element."""
        funding_group = Element('funding-group')

        for fund in funding:
            award_group = SubElement(funding_group, 'award-group')

            if fund.get('funder_name'):
                funding_source = SubElement(award_group, 'funding-source')
                funding_source.text = fund['funder_name']

            if fund.get('award_id'):
                award_id = SubElement(award_group, 'award-id')
                award_id.text = fund['award_id']

        return funding_group

    def _create_body(self, body_content: str) -> Element:
        """Create <body> element with article text."""
        body = Element('body')

        # For now, wrap entire body in a single section
        # In production, you'd want to parse structured content
        sec = SubElement(body, 'sec')
        p = SubElement(sec, 'p')
        p.text = body_content

        return body

    def _create_back_matter(self, manuscript: dict, include_references: bool) -> Element:
        """Create <back> element with references and acknowledgments."""
        back = Element('back')

        # Acknowledgments
        if manuscript.get('acknowledgments'):
            ack = SubElement(back, 'ack')
            p = SubElement(ack, 'p')
            p.text = manuscript['acknowledgments']

        # References
        if include_references and manuscript.get('references'):
            ref_list = self._create_ref_list(manuscript['references'])
            back.append(ref_list)

        return back

    def _create_ref_list(self, references: List[dict]) -> Element:
        """Create <ref-list> element."""
        ref_list = Element('ref-list')
        title = SubElement(ref_list, 'title')
        title.text = 'References'

        for idx, ref in enumerate(references, 1):
            ref_elem = SubElement(ref_list, 'ref', {'id': f'ref{idx}'})

            # Mixed citation (simplest approach)
            mixed_citation = SubElement(ref_elem, 'mixed-citation', {'publication-type': 'journal'})
            mixed_citation.text = ref.get('citation', str(ref))

        return ref_list

    def _map_article_type(self, article_type: str) -> str:
        """Map internal article type to JATS article-type attribute."""
        mapping = {
            'research-article': 'research-article',
            'review-article': 'review-article',
            'case-report': 'case-report',
            'brief-report': 'brief-report',
            'editorial': 'editorial',
            'letter': 'letter',
            'correction': 'correction',
            'retraction': 'retraction',
        }
        return mapping.get(article_type.lower(), 'research-article')

    def _prettify_with_doctype(self, elem: Element) -> str:
        """Return pretty-printed XML with DOCTYPE declaration."""
        rough_string = tostring(elem, encoding='utf-8', method='xml')
        reparsed = minidom.parseString(rough_string)

        # Get pretty XML
        pretty_xml = reparsed.toprettyxml(indent="  ", encoding='UTF-8').decode('utf-8')

        # Remove XML declaration (we'll add our own with DOCTYPE)
        lines = pretty_xml.split('\n')
        if lines[0].startswith('<?xml'):
            lines = lines[1:]

        # Add XML declaration with DOCTYPE
        xml_with_doctype = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE article PUBLIC "{self.dtd_public_id}" "{self.dtd_system_id}">
{''.join(lines)}'''

        return xml_with_doctype


def generate_jats_xml_for_manuscript(
    manuscript: dict,
    journal_meta: dict = None,
    include_body: bool = False,
    include_references: bool = True
) -> str:
    """
    Convenience function to generate JATS XML for a single manuscript.

    Args:
        manuscript: Manuscript dictionary with metadata
        journal_meta: Journal metadata (title, ISSN, publisher)
        include_body: Include article body text
        include_references: Include references section

    Returns:
        JATS 1.3 compliant XML string
    """
    if journal_meta is None:
        journal_meta = {
            'title': 'Diamond Open Access Journal',
            'abbrev': 'Diamond OA J',
            'issn': '2XXX-XXXX',
            'publisher': 'Diamond Open Access Publisher',
        }

    service = JATSXMLService()
    return service.generate_jats_xml(
        manuscript=manuscript,
        journal_meta=journal_meta,
        include_body=include_body,
        include_references=include_references
    )
