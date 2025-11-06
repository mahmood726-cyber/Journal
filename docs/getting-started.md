# Getting Started Guide

Welcome to the Diamond Open Access Journal Management System! This guide will help you get up and running quickly.

## What You're Getting

This is a complete, production-ready journal management system that includes:

✅ **Manuscript submission and tracking**
✅ **Peer review management**
✅ **Editorial workflow with decision tracking**
✅ **Automated JATS XML generation for PubMed**
✅ **Automated PubMed Central submission**
✅ **DOI registration (Crossref/DataCite)**
✅ **Email notifications for all workflow steps**
✅ **Modern web interface**
✅ **Role-based access control**
✅ **Multi-format article publishing (HTML, PDF, XML)**
✅ **Analytics and metrics dashboard**
✅ **Full compliance with PubMed/MEDLINE standards**

## Prerequisites

Before you begin, ensure you have:

- **Docker** and **Docker Compose** (recommended), OR
- **Python 3.11+**, **Node.js 18+**, **PostgreSQL 14+**, **Redis 6+**

## Quick Start (Docker - Recommended)

This is the fastest way to get started:

### Step 1: Clone the Repository

```bash
git clone https://github.com/mahmood726-cyber/Journal.git
cd Journal
```

### Step 2: Configure Environment

```bash
# Copy the example environment file
cp backend/.env.example backend/.env

# Edit the configuration file
nano backend/.env
```

**Minimum required configuration:**

```bash
# Database (will be created by Docker)
DATABASE_URL=postgresql://journal_user:journal_pass@db:5432/journal_db

# Security - CHANGE THIS!
SECRET_KEY=your-very-secure-secret-key-change-this

# Email configuration (for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@yourjournal.com
SMTP_FROM_NAME=Your Journal Name

# Journal metadata
JOURNAL_TITLE=Your Journal Name
JOURNAL_ISSN=1234-5678
JOURNAL_EISSN=8765-4321
JOURNAL_PUBLISHER=Your Publisher Name
JOURNAL_URL=http://localhost:3000
JOURNAL_EMAIL=editor@yourjournal.com
```

### Step 3: Start the Application

```bash
# Start all services (database, backend, frontend, workers)
docker-compose up -d

# Wait for services to start (about 30 seconds)
docker-compose ps

# Initialize the database with default data
docker-compose exec backend python ../scripts/init_db.py
```

### Step 4: Access the Application

- **Frontend (Website):** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

**Default Admin Login:**
- Email: `admin@journal.com`
- Password: `admin123`

⚠️ **IMPORTANT:** Change the admin password immediately after first login!

### Step 5: Next Steps

1. **Login** with the admin credentials
2. **Change the admin password** in settings
3. **Configure journal settings** (logo, description, etc.)
4. **Add editorial board members**
5. **Create subject specializations** for your field
6. **Invite reviewers** to join the platform
7. **Start accepting submissions!**

## Manual Installation

If you prefer not to use Docker:

### Step 1: Install Dependencies

**On Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv postgresql redis-server nodejs npm
```

**On macOS:**
```bash
brew install python@3.11 postgresql redis node
```

### Step 2: Set Up PostgreSQL

```bash
# Start PostgreSQL
sudo systemctl start postgresql  # Linux
brew services start postgresql   # macOS

# Create database and user
sudo -u postgres psql

CREATE USER journal_user WITH PASSWORD 'your_password';
CREATE DATABASE journal_db OWNER journal_user;
GRANT ALL PRIVILEGES ON DATABASE journal_db TO journal_user;
\q
```

### Step 3: Set Up Backend

```bash
cd backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Edit with your settings

# Run database migrations
alembic upgrade head

# Initialize database
python ../scripts/init_db.py

# Start backend server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 4: Set Up Celery Worker (in a new terminal)

```bash
cd backend
source venv/bin/activate
redis-server  # If not already running
celery -A tasks worker --loglevel=info
```

### Step 5: Set Up Frontend (in a new terminal)

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Build and start
npm run dev
```

### Step 6: Access the Application

Same as Docker setup - visit http://localhost:3000

## Configuration Deep Dive

### Email Configuration

For Gmail:
1. Enable 2-factor authentication
2. Generate an App Password
3. Use the App Password in SMTP_PASSWORD

```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

For other providers, consult their SMTP documentation.

### DOI Registration

#### Option 1: Crossref

1. Register at https://www.crossref.org/
2. Get your DOI prefix, username, and password
3. Configure in .env:

```bash
DOI_PREFIX=10.xxxxx
DOI_USERNAME=your-username
DOI_PASSWORD=your-password
DOI_PROVIDER=crossref
DOI_TEST_MODE=true  # Set to false for production
```

#### Option 2: DataCite

```bash
DOI_PREFIX=10.xxxxx
DOI_PROVIDER=datacite
DATACITE_REPOSITORY_ID=your-repo-id
DATACITE_PASSWORD=your-password
DOI_TEST_MODE=true
```

### PubMed Central Setup

When you're ready to submit to PMC:

1. Apply for PMC participation
2. Get FTP credentials from NLM
3. Configure in .env:

```bash
PMC_FTP_HOST=ftp.ncbi.nlm.nih.gov
PMC_FTP_USER=your-pmc-username
PMC_FTP_PASSWORD=your-pmc-password
PMC_FTP_PATH=/upload
```

### ORCID Integration (Optional)

For ORCID authentication:

1. Register at https://orcid.org/developer-tools
2. Get client ID and secret
3. Configure:

```bash
ORCID_CLIENT_ID=your-client-id
ORCID_CLIENT_SECRET=your-client-secret
```

## User Roles Explained

### Admin
- Full system access
- Manage users and roles
- Configure journal settings
- View all manuscripts and reviews

### Editor-in-Chief
- Manage editorial board
- Assign manuscripts to associate editors
- Make final publication decisions
- Invite and manage reviewers
- Publish articles

### Associate Editor
- Handle manuscripts in specific areas
- Invite reviewers
- Make editorial decisions
- Track review progress

### Reviewer
- Accept/decline review invitations
- Submit reviews
- Rate manuscripts
- Provide feedback

### Author
- Submit manuscripts
- Upload files
- Submit revisions
- Track submission status
- Communicate with editors

## Common Workflows

### Manuscript Submission (Author)

1. Register/login
2. Click "Submit Manuscript"
3. Fill in metadata (title, abstract, keywords)
4. Add co-authors
5. Upload manuscript file
6. Upload figures/supplementary materials
7. Review and submit

### Peer Review (Editor)

1. Receive notification of new submission
2. Perform desk review
3. Invite reviewers (system suggests matches)
4. Track review progress
5. Send reminders if needed
6. Make decision based on reviews
7. Notify author

### Publishing (Editor-in-Chief)

1. Accept manuscript
2. Request revisions if needed
3. Final copyediting
4. Assign to volume/issue
5. Click "Publish"
6. System automatically:
   - Generates JATS XML
   - Registers DOI
   - Creates PDF and HTML versions
   - Submits to PubMed Central
   - Notifies authors
   - Updates indexes

## Troubleshooting

### Backend won't start

```bash
# Check if port 8000 is in use
lsof -i :8000

# Check database connection
psql -h localhost -U journal_user -d journal_db

# Check logs
docker-compose logs backend
```

### Database errors

```bash
# Reset database (WARNING: deletes all data)
docker-compose down -v
docker-compose up -d
docker-compose exec backend python ../scripts/init_db.py
```

### Email not sending

- Check SMTP credentials
- Ensure less secure apps enabled (Gmail)
- Check firewall rules
- Test with a different provider

### File upload fails

```bash
# Check upload directory permissions
chmod 755 uploads/

# Check size limits in .env
MAX_UPLOAD_SIZE=52428800  # 50MB
```

## Getting Help

- **Documentation:** Check the `docs/` directory
- **API Docs:** http://localhost:8000/docs
- **GitHub Issues:** https://github.com/mahmood726-cyber/Journal/issues
- **Email Support:** [Your support email]

## Next Steps

Now that you have the system running:

1. **Customize your journal:**
   - Add journal description and policies
   - Upload logo and branding
   - Configure editorial board page

2. **Set up integrations:**
   - Register DOI prefix
   - Apply for PubMed Central
   - Configure ORCID

3. **Prepare for launch:**
   - Test the full workflow
   - Train editorial team
   - Create author guidelines
   - Set up backup strategy

4. **Go live:**
   - Deploy to production server
   - Announce to research community
   - Start accepting submissions

## Best Practices

- **Backup regularly:** Database and uploaded files
- **Update regularly:** Check for security updates
- **Monitor logs:** Watch for errors or issues
- **Test changes:** Use test mode for DOI/PMC
- **Document policies:** Clear author and reviewer guidelines
- **Train users:** Provide tutorials for each role

Welcome to the future of diamond open access publishing! 🚀
