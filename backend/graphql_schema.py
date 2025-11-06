"""
GraphQL API Schema

Provides a modern GraphQL API alongside the REST API for more flexible queries.
"""
import strawberry
from typing import List, Optional
from datetime import datetime
from strawberry.fastapi import GraphQLRouter


# GraphQL Types

@strawberry.type
class User:
    id: int
    email: str
    full_name: str
    affiliation: Optional[str]
    country: Optional[str]
    orcid: Optional[str]
    role: str
    created_at: datetime


@strawberry.type
class Author:
    id: int
    full_name: str
    email: str
    affiliation: Optional[str]
    orcid: Optional[str]
    is_corresponding: bool


@strawberry.type
class Manuscript:
    id: int
    manuscript_id: str
    title: str
    abstract: str
    keywords: List[str]
    status: str
    article_type: Optional[str]
    submitted_at: Optional[datetime]
    published_at: Optional[datetime]
    doi: Optional[str]
    views: int
    downloads: int


@strawberry.type
class ManuscriptDetail:
    id: int
    manuscript_id: str
    title: str
    abstract: str
    keywords: List[str]
    status: str
    article_type: Optional[str]
    authors: List[Author]
    submitted_at: Optional[datetime]
    published_at: Optional[datetime]
    doi: Optional[str]
    volume: Optional[int]
    issue: Optional[int]
    views: int
    downloads: int
    reviews_count: int


@strawberry.type
class Review:
    id: int
    manuscript_id: int
    status: str
    invited_at: datetime
    due_date: Optional[datetime]
    completed_at: Optional[datetime]
    recommendation: Optional[str]


@strawberry.type
class JournalStats:
    total_manuscripts: int
    published_articles: int
    under_review: int
    acceptance_rate: float
    average_review_time_days: Optional[float]


@strawberry.type
class SearchResult:
    manuscripts: List[Manuscript]
    total_count: int
    page: int
    page_size: int


# Input Types

@strawberry.input
class ManuscriptFilter:
    status: Optional[str] = None
    article_type: Optional[str] = None
    keywords: Optional[List[str]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


@strawberry.input
class SearchInput:
    query: str
    filters: Optional[ManuscriptFilter] = None
    page: int = 1
    page_size: int = 20


# Query Resolvers

@strawberry.type
class Query:
    @strawberry.field
    def manuscript(self, id: int, info: strawberry.Info) -> Optional[ManuscriptDetail]:
        """Get a single manuscript by ID."""
        from db.models import Manuscript as ManuscriptModel
        from db.base import SessionLocal

        db = SessionLocal()
        try:
            manuscript = db.query(ManuscriptModel).filter(ManuscriptModel.id == id).first()

            if not manuscript:
                return None

            # Convert to GraphQL type
            authors = [
                Author(
                    id=author.id,
                    full_name=author.full_name,
                    email=author.email,
                    affiliation=author.affiliation,
                    orcid=author.orcid,
                    is_corresponding=(i == 0)  # First author is corresponding
                )
                for i, author in enumerate(manuscript.authors)
            ]

            return ManuscriptDetail(
                id=manuscript.id,
                manuscript_id=manuscript.manuscript_id,
                title=manuscript.title,
                abstract=manuscript.abstract,
                keywords=manuscript.keywords or [],
                status=manuscript.status.value,
                article_type=manuscript.article_type,
                authors=authors,
                submitted_at=manuscript.submitted_at,
                published_at=manuscript.published_at,
                doi=manuscript.doi,
                volume=manuscript.volume,
                issue=manuscript.issue,
                views=manuscript.views,
                downloads=manuscript.downloads,
                reviews_count=len(manuscript.reviews)
            )
        finally:
            db.close()

    @strawberry.field
    def manuscripts(
        self,
        info: strawberry.Info,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None
    ) -> List[Manuscript]:
        """List manuscripts with optional filtering."""
        from db.models import Manuscript as ManuscriptModel, ManuscriptStatus
        from db.base import SessionLocal

        db = SessionLocal()
        try:
            query = db.query(ManuscriptModel)

            if status:
                query = query.filter(ManuscriptModel.status == ManuscriptStatus[status.upper()])

            manuscripts = query.offset(skip).limit(limit).all()

            return [
                Manuscript(
                    id=m.id,
                    manuscript_id=m.manuscript_id,
                    title=m.title,
                    abstract=m.abstract,
                    keywords=m.keywords or [],
                    status=m.status.value,
                    article_type=m.article_type,
                    submitted_at=m.submitted_at,
                    published_at=m.published_at,
                    doi=m.doi,
                    views=m.views,
                    downloads=m.downloads
                )
                for m in manuscripts
            ]
        finally:
            db.close()

    @strawberry.field
    def search_manuscripts(self, input: SearchInput, info: strawberry.Info) -> SearchResult:
        """Full-text search for manuscripts."""
        from db.models import Manuscript as ManuscriptModel
        from db.base import SessionLocal
        from sqlalchemy import or_

        db = SessionLocal()
        try:
            query = db.query(ManuscriptModel)

            # Apply text search
            search_term = f"%{input.query}%"
            query = query.filter(
                or_(
                    ManuscriptModel.title.ilike(search_term),
                    ManuscriptModel.abstract.ilike(search_term)
                )
            )

            # Apply filters
            if input.filters:
                if input.filters.status:
                    from db.models import ManuscriptStatus
                    query = query.filter(
                        ManuscriptModel.status == ManuscriptStatus[input.filters.status.upper()]
                    )

                if input.filters.article_type:
                    query = query.filter(ManuscriptModel.article_type == input.filters.article_type)

                if input.filters.date_from:
                    query = query.filter(ManuscriptModel.submitted_at >= input.filters.date_from)

                if input.filters.date_to:
                    query = query.filter(ManuscriptModel.submitted_at <= input.filters.date_to)

            total_count = query.count()

            # Pagination
            skip = (input.page - 1) * input.page_size
            manuscripts = query.offset(skip).limit(input.page_size).all()

            results = [
                Manuscript(
                    id=m.id,
                    manuscript_id=m.manuscript_id,
                    title=m.title,
                    abstract=m.abstract,
                    keywords=m.keywords or [],
                    status=m.status.value,
                    article_type=m.article_type,
                    submitted_at=m.submitted_at,
                    published_at=m.published_at,
                    doi=m.doi,
                    views=m.views,
                    downloads=m.downloads
                )
                for m in manuscripts
            ]

            return SearchResult(
                manuscripts=results,
                total_count=total_count,
                page=input.page,
                page_size=input.page_size
            )
        finally:
            db.close()

    @strawberry.field
    def journal_statistics(self, info: strawberry.Info) -> JournalStats:
        """Get overall journal statistics."""
        from db.models import Manuscript, Review, ReviewStatus, ManuscriptStatus
        from db.base import SessionLocal

        db = SessionLocal()
        try:
            total_manuscripts = db.query(Manuscript).count()

            published = db.query(Manuscript).filter(
                Manuscript.status == ManuscriptStatus.PUBLISHED
            ).count()

            under_review = db.query(Manuscript).filter(
                Manuscript.status == ManuscriptStatus.UNDER_REVIEW
            ).count()

            # Calculate acceptance rate
            total_decided = db.query(Manuscript).filter(
                Manuscript.status.in_([
                    ManuscriptStatus.ACCEPTED,
                    ManuscriptStatus.REJECTED,
                    ManuscriptStatus.PUBLISHED
                ])
            ).count()

            accepted = db.query(Manuscript).filter(
                Manuscript.status.in_([
                    ManuscriptStatus.ACCEPTED,
                    ManuscriptStatus.PUBLISHED
                ])
            ).count()

            acceptance_rate = accepted / total_decided if total_decided > 0 else 0.0

            # Average review time
            completed_reviews = db.query(Review).filter(
                Review.status == ReviewStatus.COMPLETED,
                Review.accepted_at.isnot(None),
                Review.completed_at.isnot(None)
            ).all()

            if completed_reviews:
                review_times = [(r.completed_at - r.accepted_at).days for r in completed_reviews]
                avg_review_time = sum(review_times) / len(review_times)
            else:
                avg_review_time = None

            return JournalStats(
                total_manuscripts=total_manuscripts,
                published_articles=published,
                under_review=under_review,
                acceptance_rate=acceptance_rate,
                average_review_time_days=avg_review_time
            )
        finally:
            db.close()

    @strawberry.field
    def user(self, id: int, info: strawberry.Info) -> Optional[User]:
        """Get user by ID."""
        from db.models import User as UserModel
        from db.base import SessionLocal

        db = SessionLocal()
        try:
            user = db.query(UserModel).filter(UserModel.id == id).first()

            if not user:
                return None

            return User(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                affiliation=user.affiliation,
                country=user.country,
                orcid=user.orcid,
                role=user.role.value,
                created_at=user.created_at
            )
        finally:
            db.close()


# Mutations

@strawberry.type
class Mutation:
    @strawberry.mutation
    def increment_manuscript_views(self, manuscript_id: int, info: strawberry.Info) -> bool:
        """Increment view count for a manuscript."""
        from db.models import Manuscript
        from db.base import SessionLocal

        db = SessionLocal()
        try:
            manuscript = db.query(Manuscript).filter(Manuscript.id == manuscript_id).first()

            if manuscript:
                manuscript.views += 1
                db.commit()
                return True

            return False
        finally:
            db.close()

    @strawberry.mutation
    def increment_manuscript_downloads(self, manuscript_id: int, info: strawberry.Info) -> bool:
        """Increment download count for a manuscript."""
        from db.models import Manuscript
        from db.base import SessionLocal

        db = SessionLocal()
        try:
            manuscript = db.query(Manuscript).filter(Manuscript.id == manuscript_id).first()

            if manuscript:
                manuscript.downloads += 1
                db.commit()
                return True

            return False
        finally:
            db.close()


# Create schema
schema = strawberry.Schema(query=Query, mutation=Mutation)

# Create GraphQL router for FastAPI
graphql_router = GraphQLRouter(schema, path="/graphql")


"""
To integrate with FastAPI app (in main.py):

from graphql_schema import graphql_router

app.include_router(graphql_router, prefix="/api/v1")

Then access GraphQL playground at: http://localhost:8000/api/v1/graphql
"""
