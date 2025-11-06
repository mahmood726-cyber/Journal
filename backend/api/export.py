"""
Export API Endpoints

Handles various export formats for manuscripts including:
- PubMed XML
- JATS XML (future)
- Crossref XML (future)
- BibTeX (future)
- RIS (future)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from db.base import get_db
from db.models import Manuscript, User, UserRole, ManuscriptStatus
from api.auth import get_current_user
from services.pubmed_xml_service import generate_pubmed_xml_for_manuscript
from services.jats_xml_service import generate_jats_xml_for_manuscript
from core.config import settings

router = APIRouter()


@router.get("/manuscripts/{manuscript_id}/pubmed-xml")
async def export_manuscript_pubmed_xml(
    manuscript_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Export manuscript metadata in PubMed XML format for MEDLINE indexing.

    Only published manuscripts can be exported.
    Requires editor/admin role or manuscript authorship.

    Returns:
        XML response with PubMed-compliant bibliographic data
    """
    # Fetch manuscript
    manuscript = db.query(Manuscript).filter(Manuscript.id == manuscript_id).first()

    if not manuscript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manuscript not found"
        )

    # Check if manuscript is published
    if manuscript.status != ManuscriptStatus.PUBLISHED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only published manuscripts can be exported to PubMed XML"
        )

    # Check permissions
    is_editor = current_user.role in [UserRole.EDITOR, UserRole.EDITOR_IN_CHIEF, UserRole.ADMIN]
    is_author = any(author.id == current_user.id for author in manuscript.authors)

    if not is_editor and not is_author:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to export this manuscript"
        )

    # Prepare manuscript data
    manuscript_data = {
        'manuscript_id': manuscript.manuscript_id,
        'title': manuscript.title,
        'abstract': manuscript.abstract,
        'authors': [
            {
                'first_name': author.first_name or author.full_name.split()[0],
                'last_name': author.last_name or author.full_name.split()[-1],
                'affiliation': author.affiliation,
                'orcid': author.orcid,
            }
            for author in manuscript.authors
        ],
        'doi': manuscript.doi,
        'published_at': manuscript.published_at.isoformat() if manuscript.published_at else None,
        'volume': manuscript.volume,
        'issue': manuscript.issue,
        'page_start': manuscript.page_start,
        'page_end': manuscript.page_end,
        'language': 'eng',  # Default to English
        'article_type': manuscript.article_type or 'Journal Article',
    }

    # Generate PubMed XML
    try:
        xml_content = generate_pubmed_xml_for_manuscript(
            manuscript=manuscript_data,
            journal_title=getattr(settings, 'JOURNAL_TITLE', 'Diamond Open Access Journal'),
            journal_abbrev=getattr(settings, 'JOURNAL_ABBREV', 'Diamond OA J'),
            issn=getattr(settings, 'JOURNAL_ISSN', '2XXX-XXXX'),
            publisher=getattr(settings, 'PUBLISHER_NAME', 'Diamond Open Access Publisher')
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate PubMed XML: {str(e)}"
        )

    # Return XML response
    return Response(
        content=xml_content,
        media_type="application/xml",
        headers={
            "Content-Disposition": f"attachment; filename={manuscript.manuscript_id}_pubmed.xml"
        }
    )


@router.get("/manuscripts/pubmed-xml/batch")
async def export_batch_pubmed_xml(
    manuscript_ids: Optional[str] = None,  # Comma-separated IDs
    issue_id: Optional[int] = None,
    volume: Optional[int] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Export multiple manuscripts in a single PubMed XML file.

    Can filter by:
    - Specific manuscript IDs (comma-separated)
    - Issue ID
    - Volume number

    Requires editor/admin role.
    """
    # Check permissions
    if current_user.role not in [UserRole.EDITOR, UserRole.EDITOR_IN_CHIEF, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only editors can perform batch export"
        )

    # Build query
    query = db.query(Manuscript).filter(Manuscript.status == ManuscriptStatus.PUBLISHED)

    if manuscript_ids:
        ids = [int(id.strip()) for id in manuscript_ids.split(',')]
        query = query.filter(Manuscript.id.in_(ids))
    elif issue_id:
        query = query.filter(Manuscript.issue_id == issue_id)
    elif volume:
        query = query.filter(Manuscript.volume == volume)

    manuscripts = query.limit(limit).all()

    if not manuscripts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No published manuscripts found matching criteria"
        )

    # Prepare manuscripts data
    manuscripts_data = []
    for manuscript in manuscripts:
        manuscripts_data.append({
            'manuscript_id': manuscript.manuscript_id,
            'title': manuscript.title,
            'abstract': manuscript.abstract,
            'authors': [
                {
                    'first_name': author.first_name or author.full_name.split()[0],
                    'last_name': author.last_name or author.full_name.split()[-1],
                    'affiliation': author.affiliation,
                    'orcid': author.orcid,
                }
                for author in manuscript.authors
            ],
            'doi': manuscript.doi,
            'published_at': manuscript.published_at.isoformat() if manuscript.published_at else None,
            'volume': manuscript.volume,
            'issue': manuscript.issue,
            'page_start': manuscript.page_start,
            'page_end': manuscript.page_end,
            'language': 'eng',
            'article_type': manuscript.article_type or 'Journal Article',
        })

    # Generate PubMed XML for all manuscripts
    from services.pubmed_xml_service import PubMedXMLService
    service = PubMedXMLService()

    try:
        xml_content = service.generate_pubmed_xml(
            manuscripts=manuscripts_data,
            journal_title=getattr(settings, 'JOURNAL_TITLE', 'Diamond Open Access Journal'),
            journal_abbrev=getattr(settings, 'JOURNAL_ABBREV', 'Diamond OA J'),
            issn=getattr(settings, 'JOURNAL_ISSN', '2XXX-XXXX'),
            publisher=getattr(settings, 'PUBLISHER_NAME', 'Diamond Open Access Publisher')
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate batch PubMed XML: {str(e)}"
        )

    # Generate filename
    if issue_id:
        filename = f"issue_{issue_id}_pubmed.xml"
    elif volume:
        filename = f"volume_{volume}_pubmed.xml"
    else:
        filename = f"batch_{len(manuscripts)}_pubmed.xml"

    # Return XML response
    return Response(
        content=xml_content,
        media_type="application/xml",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/manuscripts/{manuscript_id}/jats-xml")
async def export_manuscript_jats_xml(
    manuscript_id: int,
    include_body: bool = False,
    include_references: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Export manuscript in JATS XML 1.3 format for PMC, Europe PMC, and Crossref.

    JATS (Journal Article Tag Suite) is the NISO standard for scholarly articles.

    Query Parameters:
        include_body: Include article body text (default: False)
        include_references: Include references section (default: True)

    Only published manuscripts can be exported.
    Requires editor/admin role or manuscript authorship.

    Returns:
        XML response with JATS 1.3 compliant article XML
    """
    # Fetch manuscript
    manuscript = db.query(Manuscript).filter(Manuscript.id == manuscript_id).first()

    if not manuscript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manuscript not found"
        )

    # Check if manuscript is published
    if manuscript.status != ManuscriptStatus.PUBLISHED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only published manuscripts can be exported to JATS XML"
        )

    # Check permissions
    is_editor = current_user.role in [UserRole.EDITOR, UserRole.EDITOR_IN_CHIEF, UserRole.ADMIN]
    is_author = any(author.id == current_user.id for author in manuscript.authors)

    if not is_editor and not is_author:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to export this manuscript"
        )

    # Prepare manuscript data
    manuscript_data = {
        'manuscript_id': manuscript.manuscript_id,
        'title': manuscript.title,
        'abstract': manuscript.abstract,
        'keywords': manuscript.keywords if hasattr(manuscript, 'keywords') else [],
        'authors': [
            {
                'first_name': author.first_name or author.full_name.split()[0],
                'last_name': author.last_name or author.full_name.split()[-1],
                'full_name': author.full_name,
                'affiliation': author.affiliation,
                'orcid': author.orcid,
                'email': author.email,
            }
            for author in manuscript.authors
        ],
        'doi': manuscript.doi,
        'published_at': manuscript.published_at.isoformat() if manuscript.published_at else None,
        'volume': manuscript.volume,
        'issue': manuscript.issue,
        'page_start': manuscript.page_start,
        'page_end': manuscript.page_end,
        'language': 'eng',
        'article_type': manuscript.article_type or 'research-article',
        'copyright_year': manuscript.published_at.year if manuscript.published_at else None,
        'copyright_holder': 'The Authors',
    }

    # Add optional fields
    if hasattr(manuscript, 'body_content') and include_body:
        manuscript_data['body_content'] = manuscript.body_content

    if hasattr(manuscript, 'acknowledgments'):
        manuscript_data['acknowledgments'] = manuscript.acknowledgments

    if hasattr(manuscript, 'references') and include_references:
        manuscript_data['references'] = manuscript.references

    # Journal metadata
    journal_meta = {
        'title': getattr(settings, 'JOURNAL_TITLE', 'Diamond Open Access Journal'),
        'abbrev': getattr(settings, 'JOURNAL_ABBREV', 'Diamond OA J'),
        'issn': getattr(settings, 'JOURNAL_ISSN', '2XXX-XXXX'),
        'publisher': getattr(settings, 'PUBLISHER_NAME', 'Diamond Open Access Publisher'),
    }

    # Generate JATS XML
    try:
        xml_content = generate_jats_xml_for_manuscript(
            manuscript=manuscript_data,
            journal_meta=journal_meta,
            include_body=include_body,
            include_references=include_references
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate JATS XML: {str(e)}"
        )

    # Return XML response
    return Response(
        content=xml_content,
        media_type="application/xml",
        headers={
            "Content-Disposition": f"attachment; filename={manuscript.manuscript_id}_jats.xml"
        }
    )


@router.get("/manuscripts/{manuscript_id}/citation/{format}")
async def export_citation(
    manuscript_id: int,
    format: str,  # bibtex, ris, endnote, apa, mla, chicago
    db: Session = Depends(get_db)
):
    """
    Export citation in various formats.

    Supported formats:
    - bibtex: BibTeX format
    - ris: RIS format (EndNote, Zotero, Mendeley)
    - apa: APA style
    - mla: MLA style
    - chicago: Chicago style

    Public endpoint - no authentication required.
    """
    # Fetch manuscript
    manuscript = db.query(Manuscript).filter(Manuscript.id == manuscript_id).first()

    if not manuscript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manuscript not found"
        )

    if manuscript.status != ManuscriptStatus.PUBLISHED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only published manuscripts have citations"
        )

    # TODO: Implement citation generation for different formats
    # For now, return a placeholder
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=f"Citation format '{format}' not yet implemented"
    )
