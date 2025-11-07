"""
Personalization API Endpoints

Provides REST API for personalization:
- User profile management
- Interest tracking
- Recommendation generation
- Reading history
- Search tracking
- Similar users
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import json

from database import get_db
from models import User, UserProfile, ReadingHistory, UserInterest, Article
from api.auth import get_current_user, get_current_user_optional

router = APIRouter()


# ==================== Request/Response Models ====================

class InterestModel(BaseModel):
    topic: str
    weight: float = Field(ge=0.0, le=1.0)
    source: str  # 'explicit' or 'implicit'
    updated_at: datetime


class ReadingHistoryItemModel(BaseModel):
    article_id: str
    article_title: str
    topics: List[str]
    viewed_at: datetime
    time_spent: int  # seconds
    scroll_depth: int  # 0-100
    completed: bool
    saved: bool = False
    shared: bool = False


class UserPreferencesModel(BaseModel):
    email_frequency: str = 'weekly'
    notification_topics: List[str] = []
    ui_theme: str = 'auto'
    language: str = 'en'
    article_view: str = 'list'
    autoplay: bool = False


class UserBehaviorModel(BaseModel):
    average_reading_time: int = 0
    preferred_reading_time: str = 'afternoon'
    device_preference: str = 'desktop'
    engagement_level: str = 'low'
    last_visit: datetime
    visit_frequency: float = 0.0
    search_queries: List[str] = []


class DemographicsModel(BaseModel):
    role: str = 'reader'
    institution: Optional[str] = None
    country: Optional[str] = None
    research_area: List[str] = []


class UserProfileModel(BaseModel):
    user_id: str
    interests: List[InterestModel] = []
    reading_history: List[ReadingHistoryItemModel] = []
    preferences: UserPreferencesModel
    behavior: UserBehaviorModel
    demographics: DemographicsModel
    last_updated: datetime


class RecommendationModel(BaseModel):
    id: str
    type: str  # 'article', 'issue', 'topic', 'author', 'event'
    title: str
    description: str
    relevance_score: float
    reasons: List[str]
    metadata: dict


class PersonalizedContentModel(BaseModel):
    recommendations: List[RecommendationModel]
    trending_for_you: List[RecommendationModel]
    continue_reading: List[ReadingHistoryItemModel]
    suggested_authors: List[str]
    suggested_topics: List[str]


class ArticleViewRequest(BaseModel):
    article_id: str
    article_title: str
    topics: List[str]
    time_spent: int
    scroll_depth: int


class UpdatePreferencesRequest(BaseModel):
    preferences: dict


class AddInterestRequest(BaseModel):
    topic: str


# ==================== Endpoints ====================

@router.get("/profile/{user_id}", response_model=UserProfileModel)
async def get_user_profile(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get user profile."""
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

    if not profile:
        # Create default profile
        profile = UserProfile(
            user_id=user_id,
            preferences=json.dumps({
                'email_frequency': 'weekly',
                'notification_topics': [],
                'ui_theme': 'auto',
                'language': 'en',
                'article_view': 'list',
                'autoplay': False
            }),
            behavior=json.dumps({
                'average_reading_time': 0,
                'preferred_reading_time': 'afternoon',
                'device_preference': 'desktop',
                'engagement_level': 'low',
                'last_visit': datetime.utcnow().isoformat(),
                'visit_frequency': 0.0,
                'search_queries': []
            }),
            demographics=json.dumps({
                'role': 'reader'
            })
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

    # Get interests
    interests = db.query(UserInterest).filter(
        UserInterest.user_id == user_id
    ).order_by(UserInterest.weight.desc()).all()

    # Get reading history
    history = db.query(ReadingHistory).filter(
        ReadingHistory.user_id == user_id
    ).order_by(ReadingHistory.viewed_at.desc()).limit(100).all()

    return {
        "user_id": profile.user_id,
        "interests": [
            {
                "topic": i.topic,
                "weight": i.weight,
                "source": i.source,
                "updated_at": i.updated_at
            }
            for i in interests
        ],
        "reading_history": [
            {
                "article_id": h.article_id,
                "article_title": h.article_title,
                "topics": json.loads(h.topics) if h.topics else [],
                "viewed_at": h.viewed_at,
                "time_spent": h.time_spent,
                "scroll_depth": h.scroll_depth,
                "completed": h.completed,
                "saved": h.saved,
                "shared": h.shared
            }
            for h in history
        ],
        "preferences": json.loads(profile.preferences) if profile.preferences else {},
        "behavior": json.loads(profile.behavior) if profile.behavior else {},
        "demographics": json.loads(profile.demographics) if profile.demographics else {},
        "last_updated": profile.last_updated
    }


@router.put("/profile")
async def update_profile(
    profile: UserProfileModel,
    db: Session = Depends(get_db)
):
    """Update user profile."""
    db_profile = db.query(UserProfile).filter(
        UserProfile.user_id == profile.user_id
    ).first()

    if not db_profile:
        db_profile = UserProfile(user_id=profile.user_id)
        db.add(db_profile)

    db_profile.preferences = json.dumps(profile.preferences.dict())
    db_profile.behavior = json.dumps(profile.behavior.dict())
    db_profile.demographics = json.dumps(profile.demographics.dict())
    db_profile.last_updated = datetime.utcnow()

    # Update interests
    db.query(UserInterest).filter(UserInterest.user_id == profile.user_id).delete()
    for interest in profile.interests:
        db_interest = UserInterest(
            user_id=profile.user_id,
            topic=interest.topic,
            weight=interest.weight,
            source=interest.source,
            updated_at=interest.updated_at
        )
        db.add(db_interest)

    db.commit()

    return {"message": "Profile updated successfully"}


@router.post("/recommendations")
async def get_recommendations(
    request: dict,
    db: Session = Depends(get_db)
):
    """Get personalized recommendations."""
    user_id = request.get("userId")
    interests = request.get("interests", [])
    reading_history = request.get("readingHistory", [])
    limit = request.get("limit", 10)

    # Extract topics from interests
    interest_topics = set(i["topic"] for i in interests if i.get("weight", 0) > 0.3)

    # Extract topics from reading history
    history_topics = set()
    for item in reading_history[-20:]:  # Last 20
        history_topics.update(item.get("topics", []))

    # Combine topics
    all_topics = interest_topics | history_topics

    if not all_topics:
        # Return trending articles if no personalization data
        recent_articles = db.query(Article).filter(
            Article.status == "published"
        ).order_by(Article.published_date.desc()).limit(limit).all()

        return [
            {
                "id": article.id,
                "type": "article",
                "title": article.title,
                "description": article.abstract[:200] if article.abstract else "",
                "relevance_score": 0.5,
                "reasons": ["Trending article"],
                "metadata": {
                    "authors": article.authors,
                    "published_date": article.published_date.isoformat()
                }
            }
            for article in recent_articles
        ]

    # Find articles matching user interests
    recommendations = []

    # Get articles with matching keywords
    for article in db.query(Article).filter(
        Article.status == "published"
    ).order_by(Article.published_date.desc()).limit(100).all():

        article_keywords = set(json.loads(article.keywords)) if article.keywords else set()
        topic_match = len(article_keywords & all_topics)

        if topic_match > 0:
            relevance_score = min(topic_match * 0.2, 1.0)
            reasons = [f"Matches your interest in {', '.join(list(article_keywords & all_topics)[:3])}"]

            recommendations.append({
                "id": article.id,
                "type": "article",
                "title": article.title,
                "description": article.abstract[:200] if article.abstract else "",
                "relevance_score": relevance_score,
                "reasons": reasons,
                "metadata": {
                    "authors": article.authors,
                    "published_date": article.published_date.isoformat(),
                    "keywords": list(article_keywords)
                }
            })

    # Sort by relevance and return top N
    recommendations.sort(key=lambda x: x["relevance_score"], reverse=True)
    return recommendations[:limit]


@router.post("/homepage")
async def get_personalized_homepage(
    request: dict,
    db: Session = Depends(get_db)
):
    """Get personalized homepage content."""
    user_id = request.get("userId")
    profile = request.get("profile", {})

    # Get recommendations
    recommendations = await get_recommendations(request, db)

    # Get continue reading (incomplete articles)
    continue_reading = []
    for item in profile.get("readingHistory", [])[-10:]:
        if not item.get("completed") and item.get("scrollDepth", 0) > 20:
            continue_reading.append(item)

    # Get suggested topics (top interests)
    suggested_topics = [
        i["topic"] for i in profile.get("interests", [])
        if i.get("weight", 0) > 0.4
    ][:5]

    # Get suggested authors (from reading history)
    author_counts = {}
    for item in profile.get("readingHistory", []):
        article = db.query(Article).filter(Article.id == item.get("article_id")).first()
        if article and article.authors:
            authors = json.loads(article.authors) if isinstance(article.authors, str) else article.authors
            for author in authors:
                author_name = author if isinstance(author, str) else author.get("name", "")
                author_counts[author_name] = author_counts.get(author_name, 0) + 1

    suggested_authors = sorted(author_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        "recommendations": recommendations,
        "trendingForYou": recommendations[:5],  # Top 5 as trending
        "continueReading": continue_reading,
        "suggestedAuthors": [author for author, _ in suggested_authors],
        "suggestedTopics": suggested_topics
    }


@router.post("/track/article-view")
async def track_article_view(
    view: ArticleViewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Track article view."""
    user_id = current_user.id if current_user else "anonymous"

    # Add to reading history
    history_item = ReadingHistory(
        user_id=user_id,
        article_id=view.article_id,
        article_title=view.article_title,
        topics=json.dumps(view.topics),
        viewed_at=datetime.utcnow(),
        time_spent=view.time_spent,
        scroll_depth=view.scroll_depth,
        completed=view.scroll_depth > 80,
        saved=False,
        shared=False
    )
    db.add(history_item)

    # Update interests based on topics
    engagement_score = (min(view.time_spent / 300, 1) * 0.5 + view.scroll_depth / 100 * 0.5)

    for topic in view.topics:
        existing_interest = db.query(UserInterest).filter(
            UserInterest.user_id == user_id,
            UserInterest.topic == topic
        ).first()

        if existing_interest:
            # Update with exponential moving average
            existing_interest.weight = existing_interest.weight * 0.8 + engagement_score * 0.2
            existing_interest.weight = min(existing_interest.weight, 1.0)
            existing_interest.updated_at = datetime.utcnow()
        else:
            # Add new interest
            new_interest = UserInterest(
                user_id=user_id,
                topic=topic,
                weight=engagement_score * 0.5,
                source='implicit',
                updated_at=datetime.utcnow()
            )
            db.add(new_interest)

    db.commit()

    return {"message": "Article view tracked successfully"}


@router.post("/track/search")
async def track_search(
    request: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Track search query."""
    user_id = current_user.id if current_user else "anonymous"
    query = request.get("query", "")

    # Update user profile with search query
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

    if profile:
        behavior = json.loads(profile.behavior) if profile.behavior else {}
        search_queries = behavior.get("search_queries", [])
        search_queries.append(query)

        # Keep only last 50
        if len(search_queries) > 50:
            search_queries = search_queries[-50:]

        behavior["search_queries"] = search_queries
        profile.behavior = json.dumps(behavior)
        profile.last_updated = datetime.utcnow()
        db.commit()

    # Extract topics from query (simple word extraction)
    common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was'}
    topics = [word for word in query.lower().split() if len(word) > 3 and word not in common_words]

    # Update interests from topics
    for topic in topics:
        existing_interest = db.query(UserInterest).filter(
            UserInterest.user_id == user_id,
            UserInterest.topic == topic
        ).first()

        if existing_interest:
            existing_interest.weight = min(existing_interest.weight + 0.1, 1.0)
            existing_interest.updated_at = datetime.utcnow()
        else:
            new_interest = UserInterest(
                user_id=user_id,
                topic=topic,
                weight=0.3,
                source='implicit',
                updated_at=datetime.utcnow()
            )
            db.add(new_interest)

    db.commit()

    return {"message": "Search tracked successfully"}


@router.put("/preferences")
async def update_preferences(
    request: UpdatePreferencesRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user preferences."""
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()

    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)

    profile.preferences = json.dumps(request.preferences)
    profile.last_updated = datetime.utcnow()
    db.commit()

    return {"message": "Preferences updated successfully"}


@router.post("/interests")
async def add_interest(
    request: AddInterestRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add explicit interest."""
    existing = db.query(UserInterest).filter(
        UserInterest.user_id == current_user.id,
        UserInterest.topic == request.topic
    ).first()

    if existing:
        existing.weight = min(existing.weight + 0.2, 1.0)
        existing.source = 'explicit'
        existing.updated_at = datetime.utcnow()
    else:
        interest = UserInterest(
            user_id=current_user.id,
            topic=request.topic,
            weight=0.8,
            source='explicit',
            updated_at=datetime.utcnow()
        )
        db.add(interest)

    db.commit()

    return {"message": "Interest added successfully"}


@router.delete("/interests/{topic}")
async def remove_interest(
    topic: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove interest."""
    db.query(UserInterest).filter(
        UserInterest.user_id == current_user.id,
        UserInterest.topic == topic
    ).delete()
    db.commit()

    return {"message": "Interest removed successfully"}


@router.post("/similar-users")
async def get_similar_users(
    request: dict,
    db: Session = Depends(get_db)
):
    """Get similar users based on interests (collaborative filtering)."""
    user_id = request.get("userId")
    interests = request.get("interests", [])
    limit = request.get("limit", 10)

    # Get user's topics with high weight
    user_topics = set(i["topic"] for i in interests if i.get("weight", 0) > 0.5)

    if not user_topics:
        return []

    # Find users with similar interests
    similar_users = []

    # Get all users with interests
    all_user_interests = db.query(UserInterest.user_id).distinct().all()

    for (other_user_id,) in all_user_interests:
        if other_user_id == user_id:
            continue

        # Get other user's interests
        other_interests = db.query(UserInterest).filter(
            UserInterest.user_id == other_user_id,
            UserInterest.weight > 0.5
        ).all()

        other_topics = set(i.topic for i in other_interests)

        # Calculate similarity (Jaccard coefficient)
        intersection = len(user_topics & other_topics)
        union = len(user_topics | other_topics)

        if union > 0:
            similarity = intersection / union
            if similarity > 0.3:  # 30% similarity threshold
                similar_users.append((other_user_id, similarity))

    # Sort by similarity and return top N
    similar_users.sort(key=lambda x: x[1], reverse=True)
    return [user_id for user_id, _ in similar_users[:limit]]
