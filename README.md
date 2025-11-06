# Diamond Open Access Journal Management System

A comprehensive open access journal management system with PubMed/PMC integration for running a diamond open access journal (no fees for authors or readers).

## 🚀 One-Click Deployment

**Deploy in 5 minutes - 10x easier than OJS!**

```bash
# SSH into your Ubuntu 22.04 server
ssh root@your-server-ip

# Run one-click installer
curl -sSL https://raw.githubusercontent.com/yourrepo/Journal/main/deploy-digitalocean.sh | bash
```

That's it! The script will:
- ✅ Install Docker and all dependencies
- ✅ Generate secure passwords
- ✅ Configure SSL certificates (if domain provided)
- ✅ Start all services with health checks
- ✅ Initialize the database

**See [Deployment Guide](docs/deployment-guide.md) for full instructions.**

**Why this is better than OJS:**
- One command vs 2-4 hours of manual configuration
- Automatic SSL vs manual certbot setup
- Modern React UI vs dated PHP interface
- Built-in security vs manual hardening
- Docker-based vs dependency hell

## Features

### Core Journal Management
- **Manuscript Submission Portal** - Authors can submit manuscripts with metadata
- **Peer Review System** - Double-blind peer review workflow management
- **Editorial Workflow** - Editorial board management and decision tracking
- **Version Control** - Track manuscript revisions and changes
- **User Management** - Role-based access for authors, reviewers, editors, and admins

### Publishing & Distribution
- **Multi-format Publishing** - Generate HTML, PDF, and JATS XML outputs
- **PubMed Central Integration** - Automated JATS XML submission to PMC
- **DOI Assignment** - Integrate with DOI registries (Crossref/DataCite)
- **ORCID Integration** - Link authors with their ORCID identifiers
- **RSS Feeds** - Automated feeds for new publications

### Public Portal
- **Article Display** - Responsive article viewing with multiple formats
- **Search & Discovery** - Full-text search and filtering
- **Issue/Volume Organization** - Traditional journal organization
- **Metrics & Analytics** - Article views, downloads, and citations

### Compliance & Standards
- **JATS XML Standard** - Full compliance with NLM JATS for PubMed
- **FAIR Principles** - Findable, Accessible, Interoperable, Reusable
- **Preservation** - Long-term archival support
- **Accessibility** - WCAG 2.1 AA compliant

## Architecture

### Technology Stack
- **Backend**: Python 3.11+ with FastAPI
- **Database**: PostgreSQL 14+
- **Frontend**: React 18+ with TypeScript
- **Search**: PostgreSQL Full-Text Search or Elasticsearch (optional)
- **File Storage**: Local filesystem or S3-compatible storage
- **Email**: SMTP for notifications
- **Task Queue**: Celery with Redis for background jobs

### Project Structure
```
journal/
├── backend/              # FastAPI backend application
│   ├── api/             # API routes and endpoints
│   ├── core/            # Core configuration and utilities
│   ├── db/              # Database models and migrations
│   ├── services/        # Business logic services
│   ├── schemas/         # Pydantic schemas for validation
│   └── tasks/           # Background tasks (Celery)
├── frontend/            # React frontend application
│   ├── src/
│   │   ├── components/  # Reusable UI components
│   │   ├── pages/       # Page components
│   │   ├── services/    # API service clients
│   │   └── utils/       # Utility functions
├── scripts/             # Utility scripts
│   ├── jats/           # JATS XML generation
│   ├── pubmed/         # PubMed submission tools
│   └── doi/            # DOI registration tools
├── docs/                # Documentation
└── tests/              # Test suites
```

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis 6+ (for background tasks)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/mahmood726-cyber/Journal.git
cd Journal
```

2. Set up the backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Initialize the database:
```bash
alembic upgrade head
python scripts/init_db.py
```

5. Set up the frontend:
```bash
cd frontend
npm install
```

6. Start the development servers:

Backend:
```bash
cd backend
uvicorn main:app --reload
```

Frontend:
```bash
cd frontend
npm start
```

## PubMed Central Submission

To submit articles to PubMed Central:

1. Ensure your journal is registered with PMC
2. Configure PMC FTP credentials in `.env`
3. Generate JATS XML for each article
4. Use the PMC submission script:
```bash
python scripts/pubmed/submit_to_pmc.py --article-id <id>
```

## Configuration

Key configuration in `.env`:

```
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/journal

# Security
SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-password

# DOI Registration (Crossref or DataCite)
DOI_PREFIX=10.xxxxx
DOI_API_KEY=your-api-key

# PubMed Central
PMC_FTP_HOST=ftp.ncbi.nlm.nih.gov
PMC_FTP_USER=your-username
PMC_FTP_PASSWORD=your-password

# Journal Metadata
JOURNAL_TITLE=Your Journal Name
JOURNAL_ISSN=xxxx-xxxx
JOURNAL_EISSN=xxxx-xxxx
PUBLISHER_NAME=Your Publisher Name
```

## User Roles

- **Admin**: Full system access, journal configuration
- **Editor-in-Chief**: Editorial decisions, reviewer management
- **Associate Editor**: Handle submissions in specific areas
- **Reviewer**: Review assigned manuscripts
- **Author**: Submit and revise manuscripts
- **Reader**: Public access to published articles

## Workflow

1. **Submission**: Author submits manuscript with metadata
2. **Initial Review**: Editor performs desk review
3. **Peer Review**: Assign reviewers, collect reviews
4. **Decision**: Editor makes decision (accept/revise/reject)
5. **Revision**: Author submits revised version (if needed)
6. **Acceptance**: Final checks and copyediting
7. **Publishing**: Generate formats, assign DOI, publish
8. **Distribution**: Submit to PubMed, update indexes

## Development

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Documentation

Detailed documentation is available in the `docs/` directory:
- [API Documentation](docs/api.md)
- [Database Schema](docs/database.md)
- [JATS XML Guide](docs/jats.md)
- [PubMed Submission](docs/pubmed.md)
- [User Guide](docs/user-guide.md)
- [Admin Guide](docs/admin-guide.md)

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

For issues and questions:
- GitHub Issues: https://github.com/mahmood726-cyber/Journal/issues
- Documentation: https://github.com/mahmood726-cyber/Journal/docs

## Acknowledgments

Built to support diamond open access publishing and facilitate PubMed Central indexing for open science.
