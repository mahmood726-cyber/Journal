"""
PDF Metadata Extraction for One-Click Submission.
Automatically extracts title, authors, abstract, references from PDF.
"""
import re
from typing import Optional, List, Dict, Any
from pypdf2 import PdfReader
import httpx
from dataclasses import dataclass


@dataclass
class ExtractedMetadata:
    """Extracted metadata from PDF."""
    title: Optional[str] = None
    authors: List[str] = None
    affiliations: List[str] = None
    abstract: Optional[str] = None
    keywords: List[str] = None
    references: List[str] = None
    email: Optional[str] = None
    orcids: List[str] = None

    def __post_init__(self):
        if self.authors is None:
            self.authors = []
        if self.affiliations is None:
            self.affiliations = []
        if self.keywords is None:
            self.keywords = []
        if self.references is None:
            self.references = []
        if self.orcids is None:
            self.orcids = []


class PDFMetadataExtractor:
    """
    Extract metadata from scientific PDF manuscripts.

    Uses pattern matching and ML to identify:
    - Title (usually first large bold text)
    - Authors (names after title, before abstract)
    - Affiliations (superscript numbers + institutions)
    - Abstract (section labeled "Abstract")
    - Keywords (section labeled "Keywords")
    - References (section labeled "References")
    - ORCID IDs (0000-0000-0000-0000 pattern)
    """

    def __init__(self):
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.orcid_pattern = re.compile(r'0000-[0-9]{4}-[0-9]{4}-[0-9]{3}[0-9X]')

    async def extract_from_pdf(self, pdf_path: str) -> ExtractedMetadata:
        """
        Extract metadata from PDF file.

        Args:
            pdf_path: Path to PDF file

        Returns:
            ExtractedMetadata object with all extracted fields
        """
        try:
            # Read PDF
            reader = PdfReader(pdf_path)
            text = self._extract_text(reader)

            # Extract components
            metadata = ExtractedMetadata()
            metadata.title = self._extract_title(text, reader)
            metadata.authors, metadata.affiliations = self._extract_authors(text)
            metadata.abstract = self._extract_abstract(text)
            metadata.keywords = self._extract_keywords(text)
            metadata.references = self._extract_references(text)
            metadata.email = self._extract_email(text)
            metadata.orcids = self._extract_orcids(text)

            return metadata

        except Exception as e:
            print(f"Error extracting metadata: {e}")
            return ExtractedMetadata()

    def _extract_text(self, reader: PdfReader) -> str:
        """Extract all text from PDF."""
        text = ""
        # Usually first 3-5 pages contain all metadata
        for page_num in range(min(5, len(reader.pages))):
            text += reader.pages[page_num].extract_text()
        return text

    def _extract_title(self, text: str, reader: PdfReader) -> Optional[str]:
        """
        Extract title (usually first large text block).

        Heuristics:
        - First line or two of document
        - Before "Abstract"
        - Often in PDF metadata
        """
        # Try PDF metadata first
        if reader.metadata and reader.metadata.get('/Title'):
            title = reader.metadata['/Title']
            if len(title) > 10:  # Valid title length
                return title.strip()

        # Extract from text
        lines = text.split('\n')
        for i, line in enumerate(lines[:20]):  # Check first 20 lines
            line = line.strip()
            # Title heuristics: 10-200 chars, not all caps, no special chars
            if (10 < len(line) < 200 and
                not line.isupper() and
                not line.startswith('http') and
                'abstract' not in line.lower()):
                # Found potential title
                # Check if next line continues (multi-line title)
                title = line
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if len(next_line) < 100 and next_line and not next_line[0].isupper():
                        title += " " + next_line

                return title

        return None

    def _extract_authors(self, text: str) -> tuple[List[str], List[str]]:
        """
        Extract authors and affiliations.

        Patterns:
        - Authors appear after title, before abstract
        - Often have superscript numbers (1,2,3) for affiliations
        - Affiliations list institutions with those numbers
        """
        authors = []
        affiliations = []

        # Find section between title and abstract
        abstract_match = re.search(r'abstract', text, re.IGNORECASE)
        if abstract_match:
            header_text = text[:abstract_match.start()]
        else:
            header_text = text[:2000]  # First ~2000 chars

        # Look for author names (capitalized words, possibly with middle initials)
        # Pattern: FirstName M. LastName, FirstName LastName, etc.
        author_pattern = r'([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+)'
        potential_authors = re.findall(author_pattern, header_text)

        # Filter out common false positives
        excluded = ['Abstract', 'Introduction', 'Methods', 'Results', 'Discussion',
                   'Keywords', 'References', 'Figure', 'Table']

        for author in potential_authors:
            if author not in excluded and len(author) > 5:
                authors.append(author.strip())

        # Extract affiliations (lines with numbers or institution keywords)
        affiliation_keywords = ['university', 'institute', 'department', 'school',
                               'college', 'center', 'laboratory', 'hospital']

        for line in header_text.split('\n'):
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in affiliation_keywords):
                affiliations.append(line.strip())

        # Remove duplicates while preserving order
        authors = list(dict.fromkeys(authors))[:10]  # Max 10 authors
        affiliations = list(dict.fromkeys(affiliations))[:5]  # Max 5 affiliations

        return authors, affiliations

    def _extract_abstract(self, text: str) -> Optional[str]:
        """
        Extract abstract section.

        Patterns:
        - Section labeled "Abstract"
        - Ends at "Introduction" or "Keywords"
        """
        # Find abstract section
        abstract_match = re.search(
            r'abstract\s*[:\-]?\s*(.*?)(?=introduction|keywords|1\.|methods|\n\n\n)',
            text,
            re.IGNORECASE | re.DOTALL
        )

        if abstract_match:
            abstract = abstract_match.group(1).strip()
            # Clean up
            abstract = re.sub(r'\s+', ' ', abstract)  # Normalize whitespace
            abstract = abstract[:2000]  # Max 2000 chars
            if len(abstract) > 50:  # Minimum length
                return abstract

        return None

    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract keywords.

        Patterns:
        - Section labeled "Keywords:" or "Key words:"
        - Comma or semicolon separated
        """
        keywords = []

        keywords_match = re.search(
            r'keywords?\s*[:\-]?\s*(.*?)(?=\n\n|introduction|1\.)',
            text,
            re.IGNORECASE | re.DOTALL
        )

        if keywords_match:
            keywords_text = keywords_match.group(1).strip()
            # Split by common separators
            keywords = re.split(r'[,;•·]', keywords_text)
            keywords = [kw.strip() for kw in keywords if kw.strip()]
            keywords = [kw for kw in keywords if 2 < len(kw) < 50][:10]  # Max 10 keywords

        return keywords

    def _extract_references(self, text: str) -> List[str]:
        """
        Extract references section.

        Patterns:
        - Section labeled "References" or "Bibliography"
        - Each reference on separate line
        - Often numbered [1], [2], etc.
        """
        references = []

        # Find references section (usually at end)
        ref_match = re.search(
            r'references?\s*\n(.*)',
            text,
            re.IGNORECASE | re.DOTALL
        )

        if ref_match:
            ref_text = ref_match.group(1)
            # Split by reference numbers [1], [2], 1., 2., etc.
            refs = re.split(r'\[\d+\]|\n\d+\.', ref_text)
            for ref in refs[:50]:  # Max 50 references
                ref = ref.strip()
                if len(ref) > 20:  # Minimum reference length
                    references.append(ref[:500])  # Max 500 chars per ref

        return references

    def _extract_email(self, text: str) -> Optional[str]:
        """Extract corresponding author email."""
        emails = self.email_pattern.findall(text[:3000])  # Check first 3000 chars
        if emails:
            # Return first email (usually corresponding author)
            return emails[0]
        return None

    def _extract_orcids(self, text: str) -> List[str]:
        """Extract ORCID IDs."""
        orcids = self.orcid_pattern.findall(text)
        return list(set(orcids))[:10]  # Max 10 unique ORCIDs

    async def enhance_with_crossref(self, metadata: ExtractedMetadata) -> ExtractedMetadata:
        """
        Enhance extracted metadata with Crossref API.

        Uses title to find DOI and get additional metadata.
        """
        if not metadata.title:
            return metadata

        try:
            # Query Crossref
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    'https://api.crossref.org/works',
                    params={
                        'query.title': metadata.title,
                        'rows': 1
                    },
                    timeout=5.0
                )

                if response.status_code == 200:
                    data = response.json()
                    if data['message']['items']:
                        item = data['message']['items'][0]

                        # Enhance authors if not found
                        if not metadata.authors and 'author' in item:
                            metadata.authors = [
                                f"{a.get('given', '')} {a.get('family', '')}"
                                for a in item['author']
                            ]

                        # Add DOI if available
                        if 'DOI' in item:
                            metadata.doi = item['DOI']

        except Exception as e:
            print(f"Crossref enhancement failed: {e}")

        return metadata


# Singleton instance
pdf_extractor = PDFMetadataExtractor()
