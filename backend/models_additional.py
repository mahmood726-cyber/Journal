"""
Additional Database Models for Analytics, Personalization, and A/B Testing

Add these models to your existing models.py file or import from this file.
"""
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()


# ==================== A/B Testing Models ====================

class ABTest(Base):
    """A/B Test configuration."""
    __tablename__ = "ab_tests"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(20), default="draft")  # draft, active, paused, completed
    target_audience = Column(Text)  # JSON
    metrics = Column(Text)  # JSON
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    confidence_level = Column(Float, default=0.95)
    sample_size = Column(Integer, nullable=True)
    created_by = Column(String(36), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    variants = relationship("ABVariant", back_populates="test", cascade="all, delete-orphan")
    exposures = relationship("ABExposure", back_populates="test", cascade="all, delete-orphan")
    conversions = relationship("ABConversion", back_populates="test", cascade="all, delete-orphan")


class ABVariant(Base):
    """A/B Test variant configuration."""
    __tablename__ = "ab_variants"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    test_id = Column(String(36), ForeignKey("ab_tests.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    traffic_percentage = Column(Integer, nullable=False)  # 0-100
    is_control = Column(Boolean, default=False)
    config = Column(Text)  # JSON - variant-specific configuration
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    test = relationship("ABTest", back_populates="variants")


class ABAssignment(Base):
    """User assignment to A/B test variant."""
    __tablename__ = "ab_assignments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    test_id = Column(String(36), ForeignKey("ab_tests.id"), nullable=False)
    variant_id = Column(String(36), ForeignKey("ab_variants.id"), nullable=False)
    user_id = Column(String(100), nullable=False)  # Can be user ID or anonymous ID
    assigned_at = Column(DateTime, default=datetime.utcnow)

    # Index for fast lookups
    __table_args__ = (
        {'mysql_engine': 'InnoDB'},
    )


class ABExposure(Base):
    """Track when user is exposed to variant."""
    __tablename__ = "ab_exposures"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    test_id = Column(String(36), ForeignKey("ab_tests.id"), nullable=False)
    variant_id = Column(String(36), ForeignKey("ab_variants.id"), nullable=False)
    user_id = Column(String(100), nullable=False)
    exposed_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    test = relationship("ABTest", back_populates="exposures")


class ABConversion(Base):
    """Track conversion events."""
    __tablename__ = "ab_conversions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    test_id = Column(String(36), ForeignKey("ab_tests.id"), nullable=False)
    variant_id = Column(String(36), ForeignKey("ab_variants.id"), nullable=False)
    metric_id = Column(String(100), nullable=False)
    user_id = Column(String(100), nullable=False)
    value = Column(Float, nullable=True)  # Optional numeric value
    converted_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    test = relationship("ABTest", back_populates="conversions")


# ==================== Personalization Models ====================

class UserProfile(Base):
    """User profile for personalization."""
    __tablename__ = "user_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(100), unique=True, nullable=False)
    preferences = Column(Text)  # JSON
    behavior = Column(Text)  # JSON
    demographics = Column(Text)  # JSON
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    interests = relationship("UserInterest", back_populates="profile", cascade="all, delete-orphan")
    reading_history = relationship("ReadingHistory", back_populates="profile", cascade="all, delete-orphan")


class UserInterest(Base):
    """User interests with weights."""
    __tablename__ = "user_interests"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(100), nullable=False)
    topic = Column(String(100), nullable=False)
    weight = Column(Float, default=0.5)  # 0.0 to 1.0
    source = Column(String(20), default="implicit")  # 'explicit' or 'implicit'
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    profile = relationship("UserProfile", back_populates="interests")

    # Unique constraint
    __table_args__ = (
        {'mysql_engine': 'InnoDB'},
    )


class ReadingHistory(Base):
    """User reading history."""
    __tablename__ = "reading_history"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(100), nullable=False)
    article_id = Column(String(36), nullable=False)
    article_title = Column(String(500))
    topics = Column(Text)  # JSON array
    viewed_at = Column(DateTime, default=datetime.utcnow)
    time_spent = Column(Integer, default=0)  # seconds
    scroll_depth = Column(Integer, default=0)  # 0-100 percentage
    completed = Column(Boolean, default=False)
    saved = Column(Boolean, default=False)
    shared = Column(Boolean, default=False)

    # Relationships
    profile = relationship("UserProfile", back_populates="reading_history")


# ==================== Analytics Models ====================

class ArticleView(Base):
    """Track article views."""
    __tablename__ = "article_views"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    article_id = Column(String(36), nullable=False)
    user_id = Column(String(100), nullable=False)  # Can be user ID or anonymous ID
    session_id = Column(String(100))
    viewed_at = Column(DateTime, default=datetime.utcnow)
    time_spent = Column(Integer, default=0)  # seconds
    scroll_depth = Column(Integer, default=0)  # 0-100 percentage
    device_type = Column(String(20))  # desktop, mobile, tablet
    referrer = Column(String(500))
    user_agent = Column(String(500))

    # Indexes for fast queries
    __table_args__ = (
        {'mysql_engine': 'InnoDB'},
    )


class ArticleDownload(Base):
    """Track article downloads."""
    __tablename__ = "article_downloads"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    article_id = Column(String(36), nullable=False)
    user_id = Column(String(100), nullable=False)
    format = Column(String(20), default="pdf")  # pdf, xml, etc.
    downloaded_at = Column(DateTime, default=datetime.utcnow)
    device_type = Column(String(20))
    referrer = Column(String(500))


class UserSession(Base):
    """Track user sessions."""
    __tablename__ = "user_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(100), unique=True, nullable=False)
    user_id = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    duration = Column(Integer, default=0)  # seconds
    page_views = Column(Integer, default=0)
    device_type = Column(String(20))  # desktop, mobile, tablet
    traffic_source = Column(String(50))  # organic, direct, social, referral, email
    referrer = Column(String(500))
    country = Column(String(100))
    city = Column(String(100))
    user_agent = Column(String(500))


class SearchQuery(Base):
    """Track search queries."""
    __tablename__ = "search_queries"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    query = Column(String(500), nullable=False)
    user_id = Column(String(100))
    results_count = Column(Integer, default=0)
    clicked_result_id = Column(String(36))  # Article ID if clicked
    searched_at = Column(DateTime, default=datetime.utcnow)
    device_type = Column(String(20))


# ==================== Migration Script ====================

def create_tables(engine):
    """Create all tables in the database."""
    Base.metadata.create_all(engine)
    print("All tables created successfully!")


def generate_migration_sql():
    """Generate SQL migration script for manual execution."""
    sql_statements = []

    # A/B Testing Tables
    sql_statements.append("""
CREATE TABLE IF NOT EXISTS ab_tests (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'draft',
    target_audience TEXT,
    metrics TEXT,
    start_date DATETIME,
    end_date DATETIME,
    confidence_level FLOAT DEFAULT 0.95,
    sample_size INT,
    created_by VARCHAR(36) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
""")

    sql_statements.append("""
CREATE TABLE IF NOT EXISTS ab_variants (
    id VARCHAR(36) PRIMARY KEY,
    test_id VARCHAR(36) NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    traffic_percentage INT NOT NULL,
    is_control BOOLEAN DEFAULT FALSE,
    config TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (test_id) REFERENCES ab_tests(id) ON DELETE CASCADE,
    INDEX idx_test_id (test_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
""")

    sql_statements.append("""
CREATE TABLE IF NOT EXISTS ab_assignments (
    id VARCHAR(36) PRIMARY KEY,
    test_id VARCHAR(36) NOT NULL,
    variant_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(100) NOT NULL,
    assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (test_id) REFERENCES ab_tests(id) ON DELETE CASCADE,
    FOREIGN KEY (variant_id) REFERENCES ab_variants(id) ON DELETE CASCADE,
    INDEX idx_user_test (user_id, test_id),
    INDEX idx_test_id (test_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
""")

    sql_statements.append("""
CREATE TABLE IF NOT EXISTS ab_exposures (
    id VARCHAR(36) PRIMARY KEY,
    test_id VARCHAR(36) NOT NULL,
    variant_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(100) NOT NULL,
    exposed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (test_id) REFERENCES ab_tests(id) ON DELETE CASCADE,
    FOREIGN KEY (variant_id) REFERENCES ab_variants(id) ON DELETE CASCADE,
    INDEX idx_test_id (test_id),
    INDEX idx_variant_id (variant_id),
    INDEX idx_user_test (user_id, test_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
""")

    sql_statements.append("""
CREATE TABLE IF NOT EXISTS ab_conversions (
    id VARCHAR(36) PRIMARY KEY,
    test_id VARCHAR(36) NOT NULL,
    variant_id VARCHAR(36) NOT NULL,
    metric_id VARCHAR(100) NOT NULL,
    user_id VARCHAR(100) NOT NULL,
    value FLOAT,
    converted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (test_id) REFERENCES ab_tests(id) ON DELETE CASCADE,
    FOREIGN KEY (variant_id) REFERENCES ab_variants(id) ON DELETE CASCADE,
    INDEX idx_test_id (test_id),
    INDEX idx_variant_id (variant_id),
    INDEX idx_user_test_metric (user_id, test_id, metric_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
""")

    # Personalization Tables
    sql_statements.append("""
CREATE TABLE IF NOT EXISTS user_profiles (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(100) UNIQUE NOT NULL,
    preferences TEXT,
    behavior TEXT,
    demographics TEXT,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
""")

    sql_statements.append("""
CREATE TABLE IF NOT EXISTS user_interests (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    topic VARCHAR(100) NOT NULL,
    weight FLOAT DEFAULT 0.5,
    source VARCHAR(20) DEFAULT 'implicit',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_user_topic (user_id, topic),
    INDEX idx_user_id (user_id),
    INDEX idx_topic (topic),
    INDEX idx_weight (weight)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
""")

    sql_statements.append("""
CREATE TABLE IF NOT EXISTS reading_history (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    article_id VARCHAR(36) NOT NULL,
    article_title VARCHAR(500),
    topics TEXT,
    viewed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    time_spent INT DEFAULT 0,
    scroll_depth INT DEFAULT 0,
    completed BOOLEAN DEFAULT FALSE,
    saved BOOLEAN DEFAULT FALSE,
    shared BOOLEAN DEFAULT FALSE,
    INDEX idx_user_id (user_id),
    INDEX idx_article_id (article_id),
    INDEX idx_viewed_at (viewed_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
""")

    # Analytics Tables
    sql_statements.append("""
CREATE TABLE IF NOT EXISTS article_views (
    id VARCHAR(36) PRIMARY KEY,
    article_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(100) NOT NULL,
    session_id VARCHAR(100),
    viewed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    time_spent INT DEFAULT 0,
    scroll_depth INT DEFAULT 0,
    device_type VARCHAR(20),
    referrer VARCHAR(500),
    user_agent VARCHAR(500),
    INDEX idx_article_id (article_id),
    INDEX idx_user_id (user_id),
    INDEX idx_viewed_at (viewed_at),
    INDEX idx_session_id (session_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
""")

    sql_statements.append("""
CREATE TABLE IF NOT EXISTS article_downloads (
    id VARCHAR(36) PRIMARY KEY,
    article_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(100) NOT NULL,
    format VARCHAR(20) DEFAULT 'pdf',
    downloaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    device_type VARCHAR(20),
    referrer VARCHAR(500),
    INDEX idx_article_id (article_id),
    INDEX idx_user_id (user_id),
    INDEX idx_downloaded_at (downloaded_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
""")

    sql_statements.append("""
CREATE TABLE IF NOT EXISTS user_sessions (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    user_id VARCHAR(100) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_activity DATETIME DEFAULT CURRENT_TIMESTAMP,
    duration INT DEFAULT 0,
    page_views INT DEFAULT 0,
    device_type VARCHAR(20),
    traffic_source VARCHAR(50),
    referrer VARCHAR(500),
    country VARCHAR(100),
    city VARCHAR(100),
    user_agent VARCHAR(500),
    INDEX idx_session_id (session_id),
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at),
    INDEX idx_last_activity (last_activity)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
""")

    sql_statements.append("""
CREATE TABLE IF NOT EXISTS search_queries (
    id VARCHAR(36) PRIMARY KEY,
    query VARCHAR(500) NOT NULL,
    user_id VARCHAR(100),
    results_count INT DEFAULT 0,
    clicked_result_id VARCHAR(36),
    searched_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    device_type VARCHAR(20),
    INDEX idx_query (query),
    INDEX idx_user_id (user_id),
    INDEX idx_searched_at (searched_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
""")

    return "\n\n".join(sql_statements)


if __name__ == "__main__":
    print("Database Migration SQL:\n")
    print("=" * 80)
    print(generate_migration_sql())
    print("=" * 80)
    print("\nCopy and execute this SQL in your database.")
