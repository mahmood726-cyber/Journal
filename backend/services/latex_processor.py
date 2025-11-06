"""
LaTeX Manuscript Processing

Handles LaTeX manuscript compilation, conversion to other formats,
and extraction of metadata and figures.
"""
from typing import Dict, List, Optional, Tuple
import subprocess
import os
import re
import shutil
from pathlib import Path
import logging
import tempfile

logger = logging.getLogger(__name__)


class LaTeXProcessor:
    """
    Process LaTeX manuscripts for journal publication.

    Features:
    - Compile LaTeX to PDF
    - Convert LaTeX to JATS XML
    - Extract figures and tables
    - Parse bibliography
    - Extract metadata (title, authors, abstract)
    """

    def __init__(self, work_dir: Optional[str] = None):
        """
        Initialize LaTeX processor.

        Args:
            work_dir: Working directory for compilation (temp dir if None)
        """
        self.work_dir = work_dir or tempfile.mkdtemp(prefix='latex_')
        self.required_packages = ['pdflatex', 'bibtex', 'pandoc']

    def process_manuscript(
        self,
        latex_file_path: str,
        extract_figures: bool = True,
        convert_to_jats: bool = True
    ) -> Dict:
        """
        Process a LaTeX manuscript.

        Args:
            latex_file_path: Path to main .tex file
            extract_figures: Whether to extract figures
            convert_to_jats: Whether to convert to JATS XML

        Returns:
            Dictionary with processing results
        """
        latex_file = Path(latex_file_path)

        if not latex_file.exists():
            raise FileNotFoundError(f"LaTeX file not found: {latex_file_path}")

        # Copy latex file and dependencies to work directory
        work_latex_file = self._prepare_working_directory(latex_file)

        results = {
            'source_file': str(latex_file),
            'success': False,
            'pdf_path': None,
            'jats_xml_path': None,
            'figures': [],
            'metadata': {},
            'errors': []
        }

        try:
            # Extract metadata
            logger.info("Extracting metadata from LaTeX...")
            results['metadata'] = self._extract_metadata(work_latex_file)

            # Compile to PDF
            logger.info("Compiling LaTeX to PDF...")
            pdf_path, compile_errors = self._compile_to_pdf(work_latex_file)

            if pdf_path:
                results['pdf_path'] = pdf_path
                results['success'] = True
            else:
                results['errors'].extend(compile_errors)

            # Extract figures
            if extract_figures and results['success']:
                logger.info("Extracting figures...")
                results['figures'] = self._extract_figures(work_latex_file)

            # Convert to JATS XML
            if convert_to_jats and results['success']:
                logger.info("Converting to JATS XML...")
                jats_path, jats_errors = self._convert_to_jats(work_latex_file)

                if jats_path:
                    results['jats_xml_path'] = jats_path
                else:
                    results['errors'].extend(jats_errors)

        except Exception as e:
            logger.error(f"LaTeX processing failed: {str(e)}")
            results['errors'].append(str(e))

        return results

    def _prepare_working_directory(self, latex_file: Path) -> Path:
        """Copy LaTeX file and dependencies to working directory."""
        # Copy main file
        work_file = Path(self.work_dir) / latex_file.name
        shutil.copy2(latex_file, work_file)

        # Copy supporting files (figures, .bib, .cls, .sty, etc.)
        source_dir = latex_file.parent

        for pattern in ['*.eps', '*.pdf', '*.png', '*.jpg', '*.jpeg', '*.bib', '*.cls', '*.sty', '*.bst']:
            for file in source_dir.glob(pattern):
                dest = Path(self.work_dir) / file.name
                if not dest.exists():
                    shutil.copy2(file, dest)

        # Copy subdirectories (like figures/)
        for subdir in ['figures', 'images', 'graphics']:
            src_subdir = source_dir / subdir
            if src_subdir.exists() and src_subdir.is_dir():
                dest_subdir = Path(self.work_dir) / subdir
                if not dest_subdir.exists():
                    shutil.copytree(src_subdir, dest_subdir)

        return work_file

    def _extract_metadata(self, latex_file: Path) -> Dict:
        """
        Extract metadata from LaTeX document.
        Parses \title, \author, \abstract, \keywords, etc.
        """
        with open(latex_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        metadata = {}

        # Extract title
        title_match = re.search(r'\\title\{([^}]+)\}', content)
        if title_match:
            metadata['title'] = self._clean_latex_text(title_match.group(1))

        # Extract authors
        authors = []
        author_matches = re.findall(r'\\author\{([^}]+)\}', content)
        for author_text in author_matches:
            # Parse author info (simplified)
            authors.append(self._clean_latex_text(author_text))
        metadata['authors'] = authors

        # Extract abstract
        abstract_match = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', content, re.DOTALL)
        if abstract_match:
            metadata['abstract'] = self._clean_latex_text(abstract_match.group(1))

        # Extract keywords
        keywords_match = re.search(r'\\keywords?\{([^}]+)\}', content, re.IGNORECASE)
        if keywords_match:
            keywords_text = keywords_match.group(1)
            metadata['keywords'] = [k.strip() for k in keywords_text.split(',')]

        # Extract document class
        docclass_match = re.search(r'\\documentclass(?:\[[^\]]*\])?\{([^}]+)\}', content)
        if docclass_match:
            metadata['document_class'] = docclass_match.group(1)

        return metadata

    def _compile_to_pdf(self, latex_file: Path) -> Tuple[Optional[str], List[str]]:
        """
        Compile LaTeX to PDF using pdflatex.

        Returns:
            Tuple of (pdf_path or None, list of errors)
        """
        errors = []
        pdf_path = None

        try:
            # Change to working directory
            original_dir = os.getcwd()
            os.chdir(self.work_dir)

            # Run pdflatex (may need multiple passes)
            for pass_num in range(2):  # Two passes for references
                result = subprocess.run(
                    ['pdflatex', '-interaction=nonstopmode', '-halt-on-error', latex_file.name],
                    capture_output=True,
                    text=True,
                    timeout=60
                )

                if result.returncode != 0:
                    errors.append(f"pdflatex pass {pass_num + 1} failed")
                    errors.append(result.stdout)
                    break

            # Check if PDF was created
            pdf_file = latex_file.with_suffix('.pdf')
            if pdf_file.exists():
                pdf_path = str(pdf_file)
            else:
                errors.append("PDF file was not created")

            # Check for .bib file and run bibtex if present
            bib_file = latex_file.with_suffix('.bib')
            aux_file = latex_file.with_suffix('.aux')

            if bib_file.exists() and aux_file.exists():
                subprocess.run(
                    ['bibtex', latex_file.stem],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                # Re-run pdflatex after bibtex
                subprocess.run(
                    ['pdflatex', '-interaction=nonstopmode', latex_file.name],
                    capture_output=True,
                    text=True,
                    timeout=60
                )

            os.chdir(original_dir)

        except subprocess.TimeoutExpired:
            errors.append("Compilation timeout")
        except Exception as e:
            errors.append(f"Compilation error: {str(e)}")

        return pdf_path, errors

    def _extract_figures(self, latex_file: Path) -> List[Dict]:
        """
        Extract figures from LaTeX document.
        Identifies figure files and captions.
        """
        with open(latex_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        figures = []

        # Find figure environments
        figure_pattern = r'\\begin\{figure\}(.*?)\\end\{figure\}'
        figure_matches = re.findall(figure_pattern, content, re.DOTALL)

        for i, fig_content in enumerate(figure_matches, 1):
            figure_info = {'number': i}

            # Extract graphics file
            graphics_match = re.search(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}', fig_content)
            if graphics_match:
                graphics_file = graphics_match.group(1)

                # Add common extensions if not present
                if not any(graphics_file.endswith(ext) for ext in ['.eps', '.pdf', '.png', '.jpg', '.jpeg']):
                    for ext in ['.pdf', '.png', '.eps', '.jpg']:
                        test_file = Path(self.work_dir) / f"{graphics_file}{ext}"
                        if test_file.exists():
                            graphics_file = f"{graphics_file}{ext}"
                            break

                figure_info['file'] = graphics_file

                # Check if file exists
                fig_path = Path(self.work_dir) / graphics_file
                figure_info['exists'] = fig_path.exists()

                if fig_path.exists():
                    figure_info['full_path'] = str(fig_path)

            # Extract caption
            caption_match = re.search(r'\\caption\{([^}]+)\}', fig_content)
            if caption_match:
                figure_info['caption'] = self._clean_latex_text(caption_match.group(1))

            # Extract label
            label_match = re.search(r'\\label\{([^}]+)\}', fig_content)
            if label_match:
                figure_info['label'] = label_match.group(1)

            figures.append(figure_info)

        return figures

    def _convert_to_jats(self, latex_file: Path) -> Tuple[Optional[str], List[str]]:
        """
        Convert LaTeX to JATS XML using Pandoc.

        Returns:
            Tuple of (jats_xml_path or None, list of errors)
        """
        errors = []
        jats_path = None

        try:
            output_file = latex_file.with_suffix('.xml')

            # Use pandoc to convert LaTeX to JATS
            result = subprocess.run(
                [
                    'pandoc',
                    str(latex_file),
                    '-f', 'latex',
                    '-t', 'jats',
                    '-o', str(output_file),
                    '--standalone'
                ],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0 and output_file.exists():
                jats_path = str(output_file)
            else:
                errors.append("Pandoc conversion failed")
                if result.stderr:
                    errors.append(result.stderr)

        except FileNotFoundError:
            errors.append("Pandoc not found. Install pandoc for JATS conversion.")
        except subprocess.TimeoutExpired:
            errors.append("Pandoc conversion timeout")
        except Exception as e:
            errors.append(f"Conversion error: {str(e)}")

        return jats_path, errors

    def _clean_latex_text(self, text: str) -> str:
        """
        Clean LaTeX commands from text.
        Removes common LaTeX formatting commands.
        """
        # Remove common commands
        text = re.sub(r'\\textbf\{([^}]+)\}', r'\1', text)
        text = re.sub(r'\\textit\{([^}]+)\}', r'\1', text)
        text = re.sub(r'\\emph\{([^}]+)\}', r'\1', text)
        text = re.sub(r'\\textsuperscript\{([^}]+)\}', r'^{\1}', text)
        text = re.sub(r'\\textsubscript\{([^}]+)\}', r'_{\1}', text)

        # Remove line breaks
        text = text.replace('\\\\', ' ')
        text = text.replace('\n', ' ')

        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text)

        return text.strip()

    def cleanup(self):
        """Clean up working directory."""
        if self.work_dir and Path(self.work_dir).exists():
            shutil.rmtree(self.work_dir)

    def __del__(self):
        """Cleanup on deletion."""
        self.cleanup()


def process_latex_manuscript(manuscript_id: int, db_session) -> Dict:
    """
    Convenience function to process a LaTeX manuscript from database.

    Args:
        manuscript_id: Manuscript database ID
        db_session: Database session

    Returns:
        Processing results
    """
    from db.models import Manuscript

    manuscript = db_session.query(Manuscript).filter(Manuscript.id == manuscript_id).first()

    if not manuscript:
        raise ValueError(f"Manuscript {manuscript_id} not found")

    if not manuscript.manuscript_file:
        raise ValueError("No manuscript file uploaded")

    if not manuscript.manuscript_file.endswith('.tex'):
        raise ValueError("Manuscript file is not a LaTeX file")

    processor = LaTeXProcessor()

    try:
        results = processor.process_manuscript(
            latex_file_path=manuscript.manuscript_file,
            extract_figures=True,
            convert_to_jats=True
        )

        # Update manuscript record with results
        if results['pdf_path']:
            manuscript.pdf_file = results['pdf_path']

        if results['jats_xml_path']:
            manuscript.jats_xml_file = results['jats_xml_path']

        if results['figures']:
            manuscript.figures = [fig['full_path'] for fig in results['figures'] if fig.get('full_path')]

        # Update metadata if extracted
        if results['metadata']:
            if 'title' in results['metadata'] and not manuscript.title:
                manuscript.title = results['metadata']['title']

            if 'abstract' in results['metadata'] and not manuscript.abstract:
                manuscript.abstract = results['metadata']['abstract']

            if 'keywords' in results['metadata'] and not manuscript.keywords:
                manuscript.keywords = results['metadata']['keywords']

        db_session.commit()

        logger.info(f"Successfully processed LaTeX manuscript {manuscript.manuscript_id}")

        return results

    finally:
        processor.cleanup()
