"""
Theme Marketplace API
Handles theme upload, download, rating, and management
"""

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import json
import hashlib

from ..db.database import get_db
from ..db import models
from ..schemas import themes as theme_schemas
from ..core.auth import get_current_user, require_role

router = APIRouter(prefix="/themes", tags=["themes"])


@router.get("/", response_model=List[theme_schemas.ThemeResponse])
async def list_themes(
    category: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = "downloads",  # downloads, rating, recent
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """
    List all available themes from marketplace

    Parameters:
    - category: Filter by category (academic, modern, medical, etc.)
    - search: Search by name or description
    - sort_by: Sort by downloads, rating, or recent
    - limit: Number of results per page
    - offset: Pagination offset
    """
    query = db.query(models.Theme).filter(models.Theme.is_approved == True)

    if category:
        query = query.filter(models.Theme.category == category)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (models.Theme.name.ilike(search_term)) |
            (models.Theme.description.ilike(search_term)) |
            (models.Theme.author.ilike(search_term))
        )

    # Sort
    if sort_by == "downloads":
        query = query.order_by(models.Theme.download_count.desc())
    elif sort_by == "rating":
        query = query.order_by(models.Theme.average_rating.desc())
    elif sort_by == "recent":
        query = query.order_by(models.Theme.created_at.desc())

    themes = query.limit(limit).offset(offset).all()
    return themes


@router.get("/{theme_id}", response_model=theme_schemas.ThemeDetailResponse)
async def get_theme(theme_id: int, db: Session = Depends(get_db)):
    """Get detailed information about a specific theme"""
    theme = db.query(models.Theme).filter(models.Theme.id == theme_id).first()
    if not theme:
        raise HTTPException(status_code=404, detail="Theme not found")

    return theme


@router.get("/{theme_id}/download")
async def download_theme(theme_id: int, db: Session = Depends(get_db)):
    """
    Download theme configuration JSON
    Increments download counter
    """
    theme = db.query(models.Theme).filter(models.Theme.id == theme_id).first()
    if not theme:
        raise HTTPException(status_code=404, detail="Theme not found")

    # Increment download counter
    theme.download_count += 1
    db.commit()

    # Return theme configuration
    return {
        "id": theme.theme_id,
        "name": theme.name,
        "description": theme.description,
        "category": theme.category,
        "colors": json.loads(theme.colors_json),
        "typography": json.loads(theme.typography_json),
        "borderRadius": theme.border_radius,
        "author": theme.author,
        "version": theme.version,
    }


@router.post("/", response_model=theme_schemas.ThemeResponse)
async def create_theme(
    theme: theme_schemas.ThemeCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Upload a new theme to the marketplace
    Requires authentication
    """
    # Validate theme structure
    if not _validate_theme_structure(theme.colors, theme.typography):
        raise HTTPException(
            status_code=400,
            detail="Invalid theme structure. Check colors and typography."
        )

    # Generate unique theme ID
    theme_id = _generate_theme_id(theme.name, current_user.email)

    # Check if theme ID already exists
    existing = db.query(models.Theme).filter(models.Theme.theme_id == theme_id).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Theme with this name already exists. Please choose a different name."
        )

    # Create theme record
    db_theme = models.Theme(
        theme_id=theme_id,
        name=theme.name,
        description=theme.description,
        category=theme.category,
        colors_json=json.dumps(theme.colors),
        typography_json=json.dumps(theme.typography),
        border_radius=theme.border_radius,
        author=theme.author or current_user.full_name,
        author_email=current_user.email,
        version=theme.version or "1.0.0",
        preview_image_url=theme.preview_image_url,
        is_approved=False,  # Requires admin approval
        created_by_id=current_user.id,
    )

    db.add(db_theme)
    db.commit()
    db.refresh(db_theme)

    return db_theme


@router.put("/{theme_id}", response_model=theme_schemas.ThemeResponse)
async def update_theme(
    theme_id: int,
    theme_update: theme_schemas.ThemeUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update a theme
    Only the theme author or admins can update
    """
    db_theme = db.query(models.Theme).filter(models.Theme.id == theme_id).first()
    if not db_theme:
        raise HTTPException(status_code=404, detail="Theme not found")

    # Check permissions
    if db_theme.created_by_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to update this theme")

    # Update fields
    update_data = theme_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field in ["colors", "typography"]:
            setattr(db_theme, f"{field}_json", json.dumps(value))
        else:
            setattr(db_theme, field, value)

    # Increment version
    if any(field in update_data for field in ["colors", "typography", "borderRadius"]):
        db_theme.version = _increment_version(db_theme.version)

    db.commit()
    db.refresh(db_theme)

    return db_theme


@router.delete("/{theme_id}")
async def delete_theme(
    theme_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a theme
    Only the theme author or admins can delete
    """
    db_theme = db.query(models.Theme).filter(models.Theme.id == theme_id).first()
    if not db_theme:
        raise HTTPException(status_code=404, detail="Theme not found")

    # Check permissions
    if db_theme.created_by_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete this theme")

    db.delete(db_theme)
    db.commit()

    return {"message": "Theme deleted successfully"}


@router.post("/{theme_id}/rate")
async def rate_theme(
    theme_id: int,
    rating: theme_schemas.ThemeRating,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Rate a theme (1-5 stars)
    Users can only rate each theme once
    """
    db_theme = db.query(models.Theme).filter(models.Theme.id == theme_id).first()
    if not db_theme:
        raise HTTPException(status_code=404, detail="Theme not found")

    # Check if user already rated this theme
    existing_rating = db.query(models.ThemeRating).filter(
        models.ThemeRating.theme_id == theme_id,
        models.ThemeRating.user_id == current_user.id
    ).first()

    if existing_rating:
        # Update existing rating
        existing_rating.rating = rating.rating
        existing_rating.review = rating.review
        existing_rating.updated_at = datetime.utcnow()
    else:
        # Create new rating
        new_rating = models.ThemeRating(
            theme_id=theme_id,
            user_id=current_user.id,
            rating=rating.rating,
            review=rating.review,
        )
        db.add(new_rating)

    db.commit()

    # Recalculate average rating
    _update_theme_average_rating(theme_id, db)

    return {"message": "Rating submitted successfully"}


@router.get("/{theme_id}/ratings", response_model=List[theme_schemas.ThemeRatingResponse])
async def get_theme_ratings(
    theme_id: int,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """Get ratings and reviews for a theme"""
    ratings = db.query(models.ThemeRating).filter(
        models.ThemeRating.theme_id == theme_id
    ).order_by(
        models.ThemeRating.created_at.desc()
    ).limit(limit).offset(offset).all()

    return ratings


@router.post("/{theme_id}/approve")
@require_role("admin")
async def approve_theme(
    theme_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Approve a theme for marketplace (admin only)
    """
    db_theme = db.query(models.Theme).filter(models.Theme.id == theme_id).first()
    if not db_theme:
        raise HTTPException(status_code=404, detail="Theme not found")

    db_theme.is_approved = True
    db_theme.approved_by_id = current_user.id
    db_theme.approved_at = datetime.utcnow()

    db.commit()

    return {"message": "Theme approved successfully"}


@router.post("/import")
async def import_theme(
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Import a theme from JSON file
    """
    if not file.filename.endswith('.json'):
        raise HTTPException(status_code=400, detail="File must be JSON format")

    try:
        content = await file.read()
        theme_data = json.loads(content)

        # Validate theme structure
        required_fields = ["id", "name", "description", "category", "colors", "typography"]
        if not all(field in theme_data for field in required_fields):
            raise HTTPException(
                status_code=400,
                detail=f"Missing required fields. Need: {', '.join(required_fields)}"
            )

        # Create theme from imported data
        theme_create = theme_schemas.ThemeCreate(
            name=theme_data["name"],
            description=theme_data["description"],
            category=theme_data["category"],
            colors=theme_data["colors"],
            typography=theme_data["typography"],
            border_radius=theme_data.get("borderRadius", "0.5rem"),
            author=theme_data.get("author", current_user.full_name),
            version=theme_data.get("version", "1.0.0"),
        )

        return await create_theme(theme_create, current_user, db)

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Import failed: {str(e)}")


@router.get("/export/{theme_id}")
async def export_theme(
    theme_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Export a theme to JSON file
    """
    db_theme = db.query(models.Theme).filter(models.Theme.id == theme_id).first()
    if not db_theme:
        raise HTTPException(status_code=404, detail="Theme not found")

    # Check if user owns the theme or is admin
    if db_theme.created_by_id != current_user.id and current_user.role != "admin":
        # Allow export for public approved themes
        if not db_theme.is_approved:
            raise HTTPException(status_code=403, detail="Not authorized to export this theme")

    theme_export = {
        "id": db_theme.theme_id,
        "name": db_theme.name,
        "description": db_theme.description,
        "category": db_theme.category,
        "colors": json.loads(db_theme.colors_json),
        "typography": json.loads(db_theme.typography_json),
        "borderRadius": db_theme.border_radius,
        "author": db_theme.author,
        "version": db_theme.version,
        "metadata": {
            "downloads": db_theme.download_count,
            "rating": db_theme.average_rating,
            "created_at": db_theme.created_at.isoformat(),
        }
    }

    return theme_export


# Helper functions

def _validate_theme_structure(colors: dict, typography: dict) -> bool:
    """Validate theme has required color and typography fields"""
    required_color_fields = ["primary", "gray", "success", "warning", "error", "info", "background", "surface", "text"]
    required_typography_fields = ["fontFamily", "fontSize", "lineHeight"]

    if not all(field in colors for field in required_color_fields):
        return False

    if not all(field in typography for field in required_typography_fields):
        return False

    # Validate primary colors have all shades
    required_shades = ["50", "100", "200", "300", "400", "500", "600", "700", "800", "900"]
    if not all(shade in colors["primary"] for shade in required_shades):
        return False

    if not all(shade in colors["gray"] for shade in required_shades):
        return False

    return True


def _generate_theme_id(name: str, author_email: str) -> str:
    """Generate unique theme ID from name and author"""
    # Slugify name
    slug = name.lower().replace(" ", "-").replace("&", "and")
    # Remove special characters
    slug = "".join(c for c in slug if c.isalnum() or c == "-")

    # Add hash of author email for uniqueness
    email_hash = hashlib.md5(author_email.encode()).hexdigest()[:8]

    return f"{slug}-{email_hash}"


def _increment_version(version: str) -> str:
    """Increment semantic version (e.g., 1.0.0 -> 1.0.1)"""
    try:
        parts = version.split(".")
        parts[-1] = str(int(parts[-1]) + 1)
        return ".".join(parts)
    except:
        return "1.0.0"


def _update_theme_average_rating(theme_id: int, db: Session):
    """Recalculate average rating for a theme"""
    ratings = db.query(models.ThemeRating).filter(
        models.ThemeRating.theme_id == theme_id
    ).all()

    if ratings:
        avg_rating = sum(r.rating for r in ratings) / len(ratings)
        db_theme = db.query(models.Theme).filter(models.Theme.id == theme_id).first()
        if db_theme:
            db_theme.average_rating = round(avg_rating, 2)
            db_theme.rating_count = len(ratings)
            db.commit()
