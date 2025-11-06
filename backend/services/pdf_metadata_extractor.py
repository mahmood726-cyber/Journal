"""
PDF Metadata Extraction for One-Click Submission.
Automatically extracts title, authors, abstract, references from PDF.
"""
import re
from typing import Optional, List, Dict, Any
from pypdf2 import PdfReader
import httpx
from pydantic import BaseModel


class Author(BaseModel):
    """Author information."""
    name: str
    affiliation: str = ""
    email: Optional[str] = None
    orcid: Optional[str] = None
    is_corresponding: bool = False


class ExtractedMetadata(BaseModel):
    """Extracted metadata from PDF."""
    title: Optional[str] = None
    authors: List[Author] = []
    abstract: Optional[str] = None
    keywords: List[str] = []
    references: List[str] = []
    email: Optional[str] = None
    orcids: List[str] = []
    confidence_scores: Dict[str, float] = {
        'title': 0.0,
        'authors': 0.0,
        'abstract': 0.0
    }


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
            metadata.authors = self._extract_authors_plos_style(text)
            metadata.abstract = self._extract_abstract(text)
            metadata.keywords = self._extract_keywords(text)
            metadata.references = self._extract_references(text)
            metadata.email = self._extract_email(text)
            metadata.orcids = self._extract_orcids(text)

            # Calculate confidence scores
            metadata.confidence_scores = {
                'title': 0.9 if metadata.title and len(metadata.title) > 10 else 0.3,
                'authors': 0.8 if len(metadata.authors) >= 2 else 0.5 if len(metadata.authors) == 1 else 0.2,
                'abstract': 0.9 if metadata.abstract and len(metadata.abstract) > 100 else 0.4
            }

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

    def _extract_authors_plos_style(self, text: str) -> List[Author]:
        """
        Extract authors in PLOS ONE style format.

        PLOS ONE format:
        - "John M. Smith1*, Jane Doe2, Robert Johnson1"
        - Superscript numbers (1, 2, 3) indicate affiliations
        - Asterisk (*) indicates corresponding author
        - Comma-separated list
        - May include middle initials

        Returns:
            List of Author objects with name, affiliation, and metadata
        """
        authors = []
        affiliations_map = {}

        # Find section between title and abstract
        abstract_match = re.search(r'abstract', text, re.IGNORECASE)
        if abstract_match:
            header_text = text[:abstract_match.start()]
        else:
            header_text = text[:2000]  # First ~2000 chars

        # Step 1: Extract affiliations with their numbers
        # Pattern: "1Department of Biology, University Name"
        # or "1 Department of Biology, University Name"
        affiliation_keywords = ['university', 'institute', 'department', 'school',
                               'college', 'center', 'laboratory', 'hospital', 'faculty']

        for line in header_text.split('\n'):
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in affiliation_keywords):
                # Try to extract leading number
                number_match = re.match(r'^(\d+)\s*(.+)', line.strip())
                if number_match:
                    affil_num = number_match.group(1)
                    affil_text = number_match.group(2)
                    affiliations_map[affil_num] = affil_text.strip()
                else:
                    # No number, use as default affiliation
                    affiliations_map['default'] = line.strip()

        # Step 2: Find author line (usually comma-separated names with numbers/asterisks)
        # Look for pattern: "Name1*, Name2, Name3"
        # Enhanced pattern to match PLOS ONE style:
        # - FirstName [MiddleInitial.] LastName[NumbersAndSymbols]
        author_line_pattern = r'([A-Z][a-z]+(?:\s+[A-Z]\.?\s+|\s+)[A-Z][a-z]+[\d\*\†\‡§¶#]*(?:\s*,\s*|\s+and\s+|$))+'

        potential_author_lines = re.findall(author_line_pattern, header_text)

        if potential_author_lines:
            # Use the longest match as it's likely the complete author list
            author_line = max(potential_author_lines, key=len)

            # Split by commas and 'and'
            author_parts = re.split(r',|\sand\s', author_line)

            for part in author_parts:
                part = part.strip()
                if len(part) < 5:  # Too short to be a name
                    continue

                # Extract name, numbers, and asterisk
                # Pattern: "John M. Smith1*" -> name="John M. Smith", numbers="1", has_asterisk=True
                match = re.match(r'([A-Z][a-z]+(?:\s+[A-Z]\.?\s*)*[A-Z][a-z]+)([\d,\s]*)(\*|\†|\‡)?', part)

                if match:
                    name = match.group(1).strip()
                    affil_numbers = match.group(2).strip() if match.group(2) else ""
                    is_corresponding = match.group(3) is not None

                    # Get affiliation(s) from numbers
                    affiliation = ""
                    if affil_numbers:
                        # Extract individual numbers
                        nums = re.findall(r'\d+', affil_numbers)
                        if nums:
                            # Use first affiliation number
                            affiliation = affiliations_map.get(nums[0], "")

                    # If no affiliation found, use default
                    if not affiliation and 'default' in affiliations_map:
                        affiliation = affiliations_map['default']

                    # Extract email if in parentheses near name
                    email_match = self.email_pattern.search(part)
                    email = email_match.group(0) if email_match else None

                    # Extract ORCID if present
                    orcid_match = self.orcid_pattern.search(part)
                    orcid = orcid_match.group(0) if orcid_match else None

                    authors.append(Author(
                        name=name,
                        affiliation=affiliation,
                        email=email,
                        orcid=orcid,
                        is_corresponding=is_corresponding
                    ))

        # Fallback: If no authors found with PLOS style, use simple pattern
        if not authors:
            author_pattern = r'([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+)'
            potential_authors = re.findall(author_pattern, header_text)

            excluded = ['Abstract', 'Introduction', 'Methods', 'Results', 'Discussion',
                       'Keywords', 'References', 'Figure', 'Table', 'Email', 'Copyright']

            for author_name in potential_authors:
                if author_name not in excluded and len(author_name) > 5:
                    authors.append(Author(
                        name=author_name.strip(),
                        affiliation=affiliations_map.get('default', '')
                    ))

            # Limit to unique names
            seen_names = set()
            unique_authors = []
            for author in authors:
                if author.name not in seen_names:
                    seen_names.add(author.name)
                    unique_authors.append(author)
            authors = unique_authors[:15]  # Max 15 authors

        return authors[:15]  # Limit to 15 authors

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
                                Author(name=f"{a.get('given', '')} {a.get('family', '')}".strip())
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
