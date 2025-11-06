"""
Initialize database with default data.
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).resolve().parents[1] / "backend"))

from db.base import engine, Base, SessionLocal
from db.models import User, Specialization, UserRole
from core.security import get_password_hash


def init_db():
    """Initialize database with tables and default data."""

    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created successfully")

    db = SessionLocal()

    try:
        # Check if admin user already exists
        admin = db.query(User).filter(User.email == "admin@journal.com").first()

        if not admin:
            print("Creating default admin user...")
            admin = User(
                email="admin@journal.com",
                hashed_password=get_password_hash("admin123"),
                full_name="Admin User",
                role=UserRole.ADMIN,
                is_active=True,
                is_verified=True
            )
            db.add(admin)
            print("✓ Admin user created (email: admin@journal.com, password: admin123)")
            print("  ⚠️  IMPORTANT: Change this password immediately!")

        # Create default specializations
        print("Creating default specializations...")
        default_specializations = [
            "Molecular Biology",
            "Genetics",
            "Biochemistry",
            "Cell Biology",
            "Immunology",
            "Neuroscience",
            "Microbiology",
            "Pharmacology",
            "Physiology",
            "Bioinformatics"
        ]

        for spec_name in default_specializations:
            existing = db.query(Specialization).filter(Specialization.name == spec_name).first()
            if not existing:
                spec = Specialization(name=spec_name)
                db.add(spec)

        db.commit()
        print(f"✓ Created {len(default_specializations)} default specializations")

        print("\n✅ Database initialized successfully!")
        print("\nNext steps:")
        print("1. Start the backend server: cd backend && uvicorn main:app --reload")
        print("2. Access API docs at: http://localhost:8000/docs")
        print("3. Change the default admin password!")

    except Exception as e:
        print(f"\n❌ Error initializing database: {str(e)}")
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    init_db()
