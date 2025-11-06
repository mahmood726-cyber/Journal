# Production Deployment Guide

**Diamond Open Access Journal Management System**
**Version**: 1.0
**Date**: January 6, 2025

---

## Overview

This guide covers the complete production deployment of the Diamond OA Journal Management System with all Phase 1 and Phase 2 features, including local LLM capabilities.

**System Requirements**:
- Linux server (Ubuntu 20.04+ or similar)
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Ollama (for local LLM)
- 16GB+ RAM (32GB recommended)
- Optional: GPU with 8GB+ VRAM for faster AI inference

---

## Table of Contents

1. [Server Setup](#server-setup)
2. [Database Setup](#database-setup)
3. [Backend Deployment](#backend-deployment)
4. [Frontend Deployment](#frontend-deployment)
5. [Local LLM Setup](#local-llm-setup)
6. [Configuration](#configuration)
7. [Database Migrations](#database-migrations)
8. [Service Setup](#service-setup)
9. [Nginx Configuration](#nginx-configuration)
10. [SSL/TLS Setup](#ssltls-setup)
11. [Monitoring & Logging](#monitoring--logging)
12. [Backup Strategy](#backup-strategy)
13. [Testing Checklist](#testing-checklist)
14. [Troubleshooting](#troubleshooting)

---

## 1. Server Setup

### System Packages

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y \
    build-essential \
    git \
    curl \
    wget \
    nginx \
    supervisor \
    postgresql \
    postgresql-contrib \
    redis-server \
    python3.11 \
    python3.11-venv \
    python3-pip \
    nodejs \
    npm

# Install GPU drivers (if using GPU for LLM)
# For NVIDIA:
sudo apt install -y nvidia-driver-535
nvidia-smi  # Verify installation
```

### Create Application User

```bash
# Create dedicated user
sudo useradd -m -s /bin/bash journal
sudo usermod -aG sudo journal

# Switch to journal user
sudo su - journal
```

---

## 2. Database Setup

### PostgreSQL Configuration

```bash
# Switch to postgres user
sudo su - postgres

# Create database and user
createuser journal_user -P  # Enter password when prompted
createdb journal_db -O journal_user

# Enable extensions
psql journal_db <<EOF
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
EOF

# Exit postgres user
exit
```

### Database Configuration

Edit PostgreSQL configuration:

```bash
sudo nano /etc/postgresql/14/main/postgresql.conf
```

Add/modify:

```conf
max_connections = 200
shared_buffers = 4GB
effective_cache_size = 12GB
work_mem = 16MB
maintenance_work_mem = 512MB
```

Restart PostgreSQL:

```bash
sudo systemctl restart postgresql
```

---

## 3. Backend Deployment

### Clone Repository

```bash
cd /opt
sudo git clone https://github.com/your-org/journal.git
sudo chown -R journal:journal /opt/journal
cd /opt/journal
```

### Python Environment

```bash
cd /opt/journal/backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Additional dependencies for production
pip install gunicorn uvicorn[standard] psycopg2-binary redis user-agents
```

### Environment Configuration

Create production `.env` file:

```bash
nano /opt/journal/backend/.env
```

```env
# API
API_V1_PREFIX=/api/v1
PROJECT_NAME=Diamond OA Journal
DEBUG=False

# Security
SECRET_KEY=your-super-secret-key-generate-with-openssl
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS (your frontend domain)
BACKEND_CORS_ORIGINS=https://journal.yourorganization.com,https://www.journal.yourorganization.com

# Database
DATABASE_URL=postgresql://journal_user:your_password@localhost:5432/journal_db

# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@journal.yourorganization.com
SMTP_FROM_NAME=Diamond OA Journal

# File Upload
UPLOAD_DIR=/opt/journal/uploads
MAX_UPLOAD_SIZE=52428800
ALLOWED_MANUSCRIPT_FORMATS=pdf,doc,docx,tex,zip

# DOI - Crossref
DOI_PREFIX=10.XXXX
DOI_USERNAME=your_crossref_username
DOI_PASSWORD=your_crossref_password
DOI_TEST_MODE=False
DOI_PROVIDER=crossref

# Crossref DOI Registration
CROSSREF_USERNAME=your_crossref_username
CROSSREF_PASSWORD=your_crossref_password
CROSSREF_DOI_PREFIX=10.XXXX
CROSSREF_DEPOSITOR_NAME=Your Journal Name
CROSSREF_DEPOSITOR_EMAIL=deposits@journal.yourorganization.com

# DataCite (optional)
DATACITE_REPOSITORY_ID=REPO.INST
DATACITE_PASSWORD=your_datacite_password
DATACITE_DOI_PREFIX=10.XXXX

# PubMed Central
PMC_FTP_HOST=ftp.ncbi.nlm.nih.gov
PMC_FTP_USER=your_pmc_username
PMC_FTP_PASSWORD=your_pmc_password
PMC_FTP_PATH=/upload

# Journal Metadata
JOURNAL_TITLE=Diamond Open Access Journal
JOURNAL_SHORT_TITLE=Diamond OA J
JOURNAL_ABBREV=Diamond OA J
JOURNAL_ISSN=2XXX-XXXX
JOURNAL_EISSN=2XXX-XXXX
JOURNAL_PUBLISHER=Your Organization
JOURNAL_URL=https://journal.yourorganization.com
JOURNAL_EMAIL=info@journal.yourorganization.com

# Redis
REDIS_URL=redis://localhost:6379/0

# ORCID
ORCID_CLIENT_ID=your_orcid_client_id
ORCID_CLIENT_SECRET=your_orcid_client_secret
ORCID_API_URL=https://pub.orcid.org/v3.0

# Storage (S3 optional)
STORAGE_TYPE=local
# AWS_ACCESS_KEY_ID=your_aws_key
# AWS_SECRET_ACCESS_KEY=your_aws_secret
# AWS_BUCKET_NAME=journal-files
# AWS_REGION=us-east-1

# Local LLM (Ollama)
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
OLLAMA_TIMEOUT=120

# Vector Database (ChromaDB - optional)
CHROMADB_URL=http://localhost:8000
CHROMADB_COLLECTION=manuscripts

# AI Features Configuration
PLAGIARISM_SIMILARITY_THRESHOLD=0.85
PLAGIARISM_MIN_MATCH_LENGTH=50
REVIEWER_MATCH_THRESHOLD=0.70
REVIEWER_TOP_K=10
```

### Create Upload Directory

```bash
sudo mkdir -p /opt/journal/uploads
sudo chown -R journal:journal /opt/journal/uploads
sudo chmod 755 /opt/journal/uploads
```

---

## 4. Frontend Deployment

### Build Frontend

```bash
cd /opt/journal/frontend

# Install dependencies
npm install

# Build for production
npm run build

# The build will be in /opt/journal/frontend/build
```

### Serve Static Files

The built frontend will be served by Nginx (configured later).

---

## 5. Local LLM Setup

### Install Ollama

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Verify installation
ollama --version
```

### Pull Models

```bash
# Text generation model (choose based on your hardware)
# For 16GB RAM: use 8B model
ollama pull llama3.1:8b

# For 32GB+ RAM: use 70B model (better quality)
# ollama pull llama3.1:70b

# Embedding model (required)
ollama pull nomic-embed-text

# Verify models
ollama list
```

### Configure Ollama as System Service

Create systemd service:

```bash
sudo nano /etc/systemd/system/ollama.service
```

```ini
[Unit]
Description=Ollama LLM Service
After=network.target

[Service]
Type=simple
User=journal
Environment="HOME=/home/journal"
Environment="PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=/usr/local/bin/ollama serve
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable ollama
sudo systemctl start ollama
sudo systemctl status ollama
```

### Optional: ChromaDB for Vector Storage

```bash
# Using Docker
docker run -d \
  --name chromadb \
  -p 8000:8000 \
  -v /opt/journal/chroma_data:/chroma/chroma \
  --restart unless-stopped \
  chromadb/chroma:latest
```

---

## 6. Configuration

### Generate Secret Key

```bash
# Generate a secure secret key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
# Use this in your .env as SECRET_KEY
```

### Test Configuration

```bash
cd /opt/journal/backend
source venv/bin/activate

# Test database connection
python3 -c "from db.database import engine; print('Database connection successful!')"

# Test Ollama connection
curl http://localhost:11434/api/tags
```

---

## 7. Database Migrations

### Run Alembic Migrations

```bash
cd /opt/journal/backend
source venv/bin/activate

# Run migrations
alembic upgrade head

# Verify migrations
alembic current
```

### Create Admin User

```bash
# Create initial admin user
python3 -c "
from db.database import SessionLocal
from db.models import User, UserRole
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

db = SessionLocal()
admin = User(
    email='admin@journal.com',
    hashed_password=pwd_context.hash('changeme123'),
    full_name='System Administrator',
    role=UserRole.ADMIN,
    is_active=True,
    is_verified=True
)
db.add(admin)
db.commit()
print('Admin user created: admin@journal.com / changeme123')
"
```

**⚠️ IMPORTANT**: Change the admin password immediately after first login!

---

## 8. Service Setup

### Gunicorn Configuration

Create Gunicorn config:

```bash
sudo nano /opt/journal/backend/gunicorn_config.py
```

```python
# Gunicorn configuration
import multiprocessing

# Server socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
timeout = 120
keepalive = 5

# Logging
accesslog = "/var/log/journal/gunicorn-access.log"
errorlog = "/var/log/journal/gunicorn-error.log"
loglevel = "info"

# Process naming
proc_name = "journal"

# Server mechanics
daemon = False
pidfile = "/var/run/journal.pid"
user = "journal"
group = "journal"
```

### Create Log Directory

```bash
sudo mkdir -p /var/log/journal
sudo chown -R journal:journal /var/log/journal
```

### Supervisor Configuration

Create supervisor config:

```bash
sudo nano /etc/supervisor/conf.d/journal.conf
```

```ini
[program:journal-backend]
command=/opt/journal/backend/venv/bin/gunicorn main:app -c /opt/journal/backend/gunicorn_config.py
directory=/opt/journal/backend
user=journal
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/journal/backend.log
environment=PATH="/opt/journal/backend/venv/bin"
```

Update supervisor:

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start journal-backend
sudo supervisorctl status
```

---

## 9. Nginx Configuration

### Create Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/journal
```

```nginx
# Rate limiting
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=upload_limit:10m rate=5r/m;

# Upstream backend
upstream journal_backend {
    server 127.0.0.1:8000 fail_timeout=0;
}

# HTTP -> HTTPS redirect
server {
    listen 80;
    listen [::]:80;
    server_name journal.yourorganization.com www.journal.yourorganization.com;

    return 301 https://$server_name$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name journal.yourorganization.com www.journal.yourorganization.com;

    # SSL certificates (configured after Let's Encrypt setup)
    ssl_certificate /etc/letsencrypt/live/journal.yourorganization.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/journal.yourorganization.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Client body size (for file uploads)
    client_max_body_size 100M;

    # Root and index
    root /opt/journal/frontend/build;
    index index.html;

    # Static files (React app)
    location / {
        try_files $uri $uri/ /index.html;
        expires 1h;
        add_header Cache-Control "public, immutable";
    }

    # API endpoints
    location /api {
        limit_req zone=api_limit burst=20 nodelay;

        proxy_pass http://journal_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_buffering off;

        # Timeouts
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }

    # File uploads (with rate limiting)
    location /api/v1/manuscripts/upload {
        limit_req zone=upload_limit burst=5 nodelay;

        proxy_pass http://journal_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Extended timeout for uploads
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
        proxy_read_timeout 600s;
    }

    # Uploaded files
    location /uploads {
        alias /opt/journal/uploads;
        expires 1y;
        add_header Cache-Control "public, immutable";

        # Security: prevent execution of uploaded files
        location ~* \.(php|py|sh|bash)$ {
            deny all;
        }
    }

    # Health check endpoint
    location /health {
        proxy_pass http://journal_backend;
        access_log off;
    }

    # Logs
    access_log /var/log/nginx/journal-access.log;
    error_log /var/log/nginx/journal-error.log;
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/journal /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 10. SSL/TLS Setup

### Install Certbot

```bash
sudo apt install -y certbot python3-certbot-nginx
```

### Obtain Certificate

```bash
# Stop nginx temporarily
sudo systemctl stop nginx

# Obtain certificate
sudo certbot certonly --standalone \
    -d journal.yourorganization.com \
    -d www.journal.yourorganization.com \
    --agree-tos \
    --email admin@yourorganization.com

# Start nginx
sudo systemctl start nginx
```

### Auto-renewal

```bash
# Test renewal
sudo certbot renew --dry-run

# Certbot automatically sets up a cron job for renewal
```

---

## 11. Monitoring & Logging

### System Monitoring

Install monitoring tools:

```bash
sudo apt install -y htop iotop nethogs
```

### Application Logs

View logs:

```bash
# Backend logs
sudo tail -f /var/log/journal/backend.log

# Gunicorn logs
sudo tail -f /var/log/journal/gunicorn-access.log
sudo tail -f /var/log/journal/gunicorn-error.log

# Nginx logs
sudo tail -f /var/log/nginx/journal-access.log
sudo tail -f /var/log/nginx/journal-error.log

# Ollama logs
sudo journalctl -u ollama -f

# Supervisor logs
sudo tail -f /var/log/supervisor/supervisord.log
```

### Log Rotation

Configure log rotation:

```bash
sudo nano /etc/logrotate.d/journal
```

```
/var/log/journal/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 journal journal
    sharedscripts
    postrotate
        supervisorctl restart journal-backend
    endscript
}
```

---

## 12. Backup Strategy

### Database Backups

Create backup script:

```bash
sudo nano /opt/journal/scripts/backup_database.sh
```

```bash
#!/bin/bash

# Configuration
BACKUP_DIR="/opt/journal/backups"
DB_NAME="journal_db"
DB_USER="journal_user"
RETENTION_DAYS=30

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup filename with timestamp
BACKUP_FILE="$BACKUP_DIR/journal_db_$(date +%Y%m%d_%H%M%S).sql.gz"

# Create backup
PGPASSWORD="$DB_PASSWORD" pg_dump -U $DB_USER -h localhost $DB_NAME | gzip > $BACKUP_FILE

# Remove old backups
find $BACKUP_DIR -name "journal_db_*.sql.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed: $BACKUP_FILE"
```

Make executable and schedule:

```bash
sudo chmod +x /opt/journal/scripts/backup_database.sh

# Add to crontab (daily at 2 AM)
sudo crontab -e
# Add: 0 2 * * * /opt/journal/scripts/backup_database.sh
```

### File Backups

```bash
# Backup uploads directory
sudo rsync -avz /opt/journal/uploads/ /backup/journal/uploads/

# Or use cloud backup (e.g., AWS S3)
# aws s3 sync /opt/journal/uploads/ s3://your-backup-bucket/uploads/
```

---

## 13. Testing Checklist

### Pre-Deployment Tests

- [ ] Database connection works
- [ ] All migrations applied successfully
- [ ] Admin user created
- [ ] Environment variables configured
- [ ] Ollama is running and models pulled
- [ ] Backend starts without errors
- [ ] Frontend builds successfully
- [ ] Nginx configuration valid

### Post-Deployment Tests

**Basic Functionality**:
- [ ] Website loads at https://journal.yourorganization.com
- [ ] Login with admin credentials works
- [ ] API health check returns healthy
- [ ] File upload works

**AI Features**:
- [ ] Ollama health check passes: GET /api/v1/ai/llm/health
- [ ] Test generation works (admin only)
- [ ] Plagiarism check can be initiated
- [ ] Reviewer matching returns results
- [ ] Email templates can be generated

**DOI Features**:
- [ ] Crossref DOI registration works (test environment)
- [ ] DataCite DOI registration works (test environment)
- [ ] DOI status check returns data

**Metrics**:
- [ ] Article view tracking works
- [ ] Metrics dashboard displays data
- [ ] AI insights generation works

**Export Features**:
- [ ] PubMed XML export downloads
- [ ] JATS XML export downloads
- [ ] Crossref XML generates correctly

### Load Testing

```bash
# Install Apache Bench
sudo apt install -y apache2-utils

# Test API endpoint
ab -n 1000 -c 10 https://journal.yourorganization.com/api/v1/health

# Test static files
ab -n 1000 -c 10 https://journal.yourorganization.com/
```

---

## 14. Troubleshooting

### Backend Won't Start

```bash
# Check supervisor status
sudo supervisorctl status

# Check logs
sudo tail -f /var/log/journal/backend.log

# Common issues:
# 1. Database connection - check DATABASE_URL in .env
# 2. Missing dependencies - pip install -r requirements.txt
# 3. Port conflict - check if port 8000 is in use
```

### Ollama Issues

```bash
# Check Ollama status
sudo systemctl status ollama

# Check if models are pulled
ollama list

# Test Ollama manually
curl http://localhost:11434/api/tags

# Re-pull models if needed
ollama pull llama3.1:8b
ollama pull nomic-embed-text
```

### Database Migration Errors

```bash
# Check current migration version
cd /opt/journal/backend
source venv/bin/activate
alembic current

# View migration history
alembic history

# Downgrade one version if needed
alembic downgrade -1

# Upgrade to head
alembic upgrade head
```

### Performance Issues

```bash
# Check system resources
htop
free -h
df -h

# Check database performance
sudo -u postgres psql journal_db -c "SELECT * FROM pg_stat_activity;"

# Check slow queries
sudo -u postgres psql journal_db -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"
```

### SSL Certificate Issues

```bash
# Test SSL configuration
sudo nginx -t

# Check certificate expiry
sudo certbot certificates

# Renew certificate manually
sudo certbot renew
```

---

## Quick Reference

### Service Management

```bash
# Backend
sudo supervisorctl restart journal-backend
sudo supervisorctl stop journal-backend
sudo supervisorctl start journal-backend

# Ollama
sudo systemctl restart ollama
sudo systemctl stop ollama
sudo systemctl start ollama

# Nginx
sudo systemctl restart nginx
sudo systemctl reload nginx

# PostgreSQL
sudo systemctl restart postgresql

# Redis
sudo systemctl restart redis
```

### Logs

```bash
# All logs
sudo tail -f /var/log/journal/*.log

# Specific service
sudo journalctl -u ollama -f
sudo journalctl -u nginx -f
```

### Database

```bash
# Connect to database
sudo -u postgres psql journal_db

# Backup
/opt/journal/scripts/backup_database.sh

# Restore
gunzip < backup.sql.gz | sudo -u postgres psql journal_db
```

---

## Security Checklist

- [ ] Change default admin password
- [ ] Configure firewall (UFW)
- [ ] Enable fail2ban for SSH
- [ ] Regular security updates
- [ ] Monitor logs for suspicious activity
- [ ] Backup encryption enabled
- [ ] SSL/TLS configured with strong ciphers
- [ ] CORS origins restricted
- [ ] Rate limiting enabled
- [ ] File upload validation enabled

---

## Maintenance Schedule

**Daily**:
- Check application logs for errors
- Monitor disk space usage
- Check backup completion

**Weekly**:
- Review security logs
- Check SSL certificate expiry
- Update system packages

**Monthly**:
- Test backup restoration
- Review and optimize database
- Update application dependencies
- Review and rotate logs

---

## Support

For issues or questions:
- Documentation: `/opt/journal/docs/`
- Logs: `/var/log/journal/`
- Issues: https://github.com/your-org/journal/issues

---

**Document Version**: 1.0
**Last Updated**: January 6, 2025
**Status**: Production Ready
