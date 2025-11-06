"""
Advanced SEO and Marketing Tools

Optimizes article visibility in search engines and academic databases.
"""
from typing import Dict, List, Optional
import logging
from datetime import datetime
import xml.etree.ElementTree as ET
from urllib.parse import quote
import json

logger = logging.getLogger(__name__)


class SEOOptimizer:
    """
    Comprehensive SEO optimization for journal articles.

    Features:
    - Generate structured data (Schema.org)
    - Create XML sitemaps
    - Generate meta tags
    - Social media optimization (Open Graph, Twitter Cards)
    - Google Scholar metadata
    - Alt metrics integration
    """

    def __init__(self, base_url: str, journal_title: str):
        self.base_url = base_url.rstrip('/')
        self.journal_title = journal_title

    def generate_article_seo(self, manuscript, authors: List) -> Dict:
        """
        Generate comprehensive SEO metadata for an article.

        Args:
            manuscript: Manuscript object
            authors: List of author objects

        Returns:
            Dictionary with all SEO elements
        """
        article_url = f"{self.base_url}/article/{manuscript.manuscript_id}"

        return {
            'meta_tags': self._generate_meta_tags(manuscript, authors, article_url),
            'structured_data': self._generate_structured_data(manuscript, authors, article_url),
            'open_graph': self._generate_open_graph(manuscript, authors, article_url),
            'twitter_card': self._generate_twitter_card(manuscript, article_url),
            'google_scholar': self._generate_google_scholar_tags(manuscript, authors),
            'dublin_core': self._generate_dublin_core(manuscript, authors)
        }

    def _generate_meta_tags(self, manuscript, authors: List, url: str) -> Dict:
        """Generate standard HTML meta tags."""
        author_names = ', '.join([a.full_name for a in authors])

        return {
            'title': f"{manuscript.title} | {self.journal_title}",
            'description': manuscript.abstract[:160] if len(manuscript.abstract) > 160 else manuscript.abstract,
            'keywords': ', '.join(manuscript.keywords) if manuscript.keywords else '',
            'author': author_names,
            'citation_title': manuscript.title,
            'citation_journal_title': self.journal_title,
            'citation_publication_date': manuscript.published_at.strftime('%Y/%m/%d') if manuscript.published_at else '',
            'citation_doi': manuscript.doi if manuscript.doi else '',
            'citation_issn': '',  # Add from settings
            'citation_volume': str(manuscript.volume) if manuscript.volume else '',
            'citation_issue': str(manuscript.issue) if manuscript.issue else '',
            'citation_pdf_url': f"{url}.pdf" if manuscript.pdf_file else '',
            'robots': 'index, follow'
        }

    def _generate_structured_data(self, manuscript, authors: List, url: str) -> str:
        """Generate Schema.org structured data (JSON-LD)."""
        structured_data = {
            '@context': 'https://schema.org',
            '@type': 'ScholarlyArticle',
            'headline': manuscript.title,
            'description': manuscript.abstract,
            'url': url,
            'datePublished': manuscript.published_at.isoformat() if manuscript.published_at else None,
            'author': [
                {
                    '@type': 'Person',
                    'name': author.full_name,
                    'affiliation': {
                        '@type': 'Organization',
                        'name': author.affiliation
                    } if author.affiliation else None,
                    '@id': f"https://orcid.org/{author.orcid}" if author.orcid else None
                }
                for author in authors
            ],
            'publisher': {
                '@type': 'Organization',
                'name': self.journal_title
            },
            'isAccessibleForFree': True,
            'license': 'https://creativecommons.org/licenses/by/4.0/',
            'keywords': manuscript.keywords if manuscript.keywords else [],
            'identifier': [
                {'@type': 'PropertyValue', 'propertyID': 'DOI', 'value': manuscript.doi}
            ] if manuscript.doi else []
        }

        # Remove None values
        structured_data = self._remove_none_values(structured_data)

        return json.dumps(structured_data, indent=2)

    def _generate_open_graph(self, manuscript, authors: List, url: str) -> Dict:
        """Generate Open Graph meta tags for social media."""
        return {
            'og:title': manuscript.title,
            'og:description': manuscript.abstract[:200] if len(manuscript.abstract) > 200 else manuscript.abstract,
            'og:url': url,
            'og:type': 'article',
            'og:site_name': self.journal_title,
            'article:published_time': manuscript.published_at.isoformat() if manuscript.published_at else '',
            'article:author': authors[0].full_name if authors else '',
            'article:tag': manuscript.keywords[0] if manuscript.keywords else ''
        }

    def _generate_twitter_card(self, manuscript, url: str) -> Dict:
        """Generate Twitter Card meta tags."""
        return {
            'twitter:card': 'summary_large_image',
            'twitter:title': manuscript.title,
            'twitter:description': manuscript.abstract[:200] if len(manuscript.abstract) > 200 else manuscript.abstract,
            'twitter:url': url
        }

    def _generate_google_scholar_tags(self, manuscript, authors: List) -> Dict:
        """Generate Google Scholar meta tags for indexing."""
        tags = {
            'citation_title': manuscript.title,
            'citation_journal_title': self.journal_title,
            'citation_publication_date': manuscript.published_at.strftime('%Y/%m/%d') if manuscript.published_at else '',
        }

        # Add authors
        for i, author in enumerate(authors, 1):
            tags[f'citation_author'] = author.full_name
            if author.affiliation:
                tags[f'citation_author_institution'] = author.affiliation

        if manuscript.doi:
            tags['citation_doi'] = manuscript.doi

        if manuscript.pdf_file:
            tags['citation_pdf_url'] = f"{self.base_url}/article/{manuscript.manuscript_id}.pdf"

        return tags

    def _generate_dublin_core(self, manuscript, authors: List) -> Dict:
        """Generate Dublin Core metadata."""
        return {
            'DC.title': manuscript.title,
            'DC.creator': ', '.join([a.full_name for a in authors]),
            'DC.description': manuscript.abstract,
            'DC.date': manuscript.published_at.strftime('%Y-%m-%d') if manuscript.published_at else '',
            'DC.type': 'Text',
            'DC.format': 'text/html',
            'DC.identifier': manuscript.doi if manuscript.doi else '',
            'DC.language': 'en',
            'DC.rights': 'https://creativecommons.org/licenses/by/4.0/'
        }

    def generate_sitemap(self, manuscripts: List, filename: str = 'sitemap.xml') -> str:
        """
        Generate XML sitemap for search engines.

        Args:
            manuscripts: List of published manuscripts
            filename: Output filename

        Returns:
            Path to generated sitemap
        """
        # Create XML structure
        urlset = ET.Element('urlset')
        urlset.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')

        # Add homepage
        url = ET.SubElement(urlset, 'url')
        ET.SubElement(url, 'loc').text = self.base_url
        ET.SubElement(url, 'changefreq').text = 'daily'
        ET.SubElement(url, 'priority').text = '1.0'

        # Add articles
        for manuscript in manuscripts:
            url = ET.SubElement(urlset, 'url')
            loc = f"{self.base_url}/article/{manuscript.manuscript_id}"
            ET.SubElement(url, 'loc').text = loc
            ET.SubElement(url, 'lastmod').text = manuscript.published_at.strftime('%Y-%m-%d')
            ET.SubElement(url, 'changefreq').text = 'monthly'
            ET.SubElement(url, 'priority').text = '0.8'

        # Write to file
        tree = ET.ElementTree(urlset)
        tree.write(filename, encoding='utf-8', xml_declaration=True)

        logger.info(f"Generated sitemap with {len(manuscripts)} articles")

        return filename

    def generate_rss_feed(self, manuscripts: List, filename: str = 'feed.xml') -> str:
        """
        Generate RSS feed for latest articles.

        Args:
            manuscripts: List of recent manuscripts
            filename: Output filename

        Returns:
            Path to generated feed
        """
        rss = ET.Element('rss')
        rss.set('version', '2.0')

        channel = ET.SubElement(rss, 'channel')
        ET.SubElement(channel, 'title').text = self.journal_title
        ET.SubElement(channel, 'link').text = self.base_url
        ET.SubElement(channel, 'description').text = f"Latest articles from {self.journal_title}"
        ET.SubElement(channel, 'language').text = 'en-us'

        for manuscript in manuscripts[:20]:  # Latest 20 articles
            item = ET.SubElement(channel, 'item')
            ET.SubElement(item, 'title').text = manuscript.title
            ET.SubElement(item, 'link').text = f"{self.base_url}/article/{manuscript.manuscript_id}"
            ET.SubElement(item, 'description').text = manuscript.abstract[:500]
            ET.SubElement(item, 'pubDate').text = manuscript.published_at.strftime('%a, %d %b %Y %H:%M:%S +0000')
            ET.SubElement(item, 'guid').text = manuscript.doi if manuscript.doi else f"{self.base_url}/article/{manuscript.manuscript_id}"

        # Write to file
        tree = ET.ElementTree(rss)
        tree.write(filename, encoding='utf-8', xml_declaration=True)

        logger.info(f"Generated RSS feed with {len(manuscripts)} articles")

        return filename

    def generate_robots_txt(self, additional_rules: Optional[List[str]] = None) -> str:
        """Generate robots.txt content."""
        rules = [
            "User-agent: *",
            "Allow: /",
            "Allow: /article/",
            "Disallow: /admin/",
            "Disallow: /api/",
            "",
            f"Sitemap: {self.base_url}/sitemap.xml"
        ]

        if additional_rules:
            rules.extend(additional_rules)

        return '\n'.join(rules)

    def _remove_none_values(self, data):
        """Recursively remove None values from dict."""
        if isinstance(data, dict):
            return {k: self._remove_none_values(v) for k, v in data.items() if v is not None}
        elif isinstance(data, list):
            return [self._remove_none_values(item) for item in data if item is not None]
        else:
            return data


def optimize_article_seo(manuscript_id: int, db_session, base_url: str, journal_title: str) -> Dict:
    """
    Optimize SEO for a published article.

    Args:
        manuscript_id: Manuscript database ID
        db_session: Database session
        base_url: Base URL of journal
        journal_title: Journal title

    Returns:
        SEO metadata
    """
    from db.models import Manuscript, ManuscriptStatus

    manuscript = db_session.query(Manuscript).filter(
        Manuscript.id == manuscript_id,
        Manuscript.status == ManuscriptStatus.PUBLISHED
    ).first()

    if not manuscript:
        return {'error': 'Published manuscript not found'}

    optimizer = SEOOptimizer(base_url, journal_title)

    return optimizer.generate_article_seo(manuscript, manuscript.authors)
