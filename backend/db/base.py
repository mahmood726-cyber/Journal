"""
Performance-optimized database configuration with connection pooling.
"""
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from core.config import settings

# Create database engine with optimized connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    # Connection pool settings for performance
    poolclass=QueuePool,
    pool_size=20,              # Maintain 20 connections
    max_overflow=40,           # Allow 40 additional connections when pool is full
    pool_timeout=30,           # Timeout for getting connection from pool
    pool_recycle=3600,         # Recycle connections after 1 hour
    pool_pre_ping=True,        # Verify connections before using
    # Query optimization
    echo=False,                # Don't log SQL in production
    echo_pool=False,           # Don't log pool events
    # Connection arguments
    connect_args={
        "options": "-c timezone=utc",
        "application_name": "diamond_oa_journal",
    }
)

# Enable connection pooling optimizations
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Set SQLite-specific optimizations if using SQLite."""
    if 'sqlite' in settings.DATABASE_URL:
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=10000")
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.close()

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False  # Prevent extra queries after commit
)

# Create declarative base for models
Base = declarative_base()


def get_db():
    """
    Dependency for getting database sessions.
    Yields a database session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
