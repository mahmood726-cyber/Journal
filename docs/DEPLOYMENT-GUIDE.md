# Deployment Guide - Diamond OA Journal System

**Version 1.0**
**Last Updated: November 2024**

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start (Development)](#quick-start-development)
3. [Database Setup](#database-setup)
4. [Redis Setup](#redis-setup)
5. [Backend Deployment](#backend-deployment)
6. [Frontend Deployment](#frontend-deployment)
7. [Production Deployment](#production-deployment)
8. [Environment Variables](#environment-variables)
9. [Monitoring & Maintenance](#monitoring--maintenance)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

**Minimum:**
- CPU: 2 cores
- RAM: 4 GB
- Storage: 50 GB
- OS: Ubuntu 20.04+ / Debian 10+ / macOS 10.15+

**Recommended:**
- CPU: 4+ cores
- RAM: 8+ GB
- Storage: 100+ GB SSD
- OS: Ubuntu 22.04 LTS

### Software Requirements

**Required:**
- Docker 20.10+ & Docker Compose 2.0+
- Git 2.30+
- Node.js 18+ & npm 9+ (for local development)
- Python 3.9+ (for local development)

**Optional:**
- Nginx (for production reverse proxy)
- SSL certificate (Let's Encrypt recommended)
- PostgreSQL client tools
- Redis CLI tools

### Install Docker (Ubuntu/Debian)

```bash
# Update package index
sudo apt-get update

# Install dependencies
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add your user to docker group
sudo usermod -aG docker $USER

# Log out and back in for group changes to take effect
```

### Verify Installation

```bash
docker --version
# Docker version 24.0.0+

docker compose version
# Docker Compose version v2.20.0+

git --version
# git version 2.40.0+
```

---

## Quick Start (Development)

### 1. Clone Repository

```bash
git clone https://github.com/yourorg/Journal.git
cd Journal
```

### 2. Configure Environment

```bash
# Copy example environment file
cp backend/.env.example backend/.env

# Edit with your settings
nano backend/.env
```

**Minimum Required Settings:**
```env
# Database
DATABASE_URL=postgresql://journal_user:journal_pass@db:5432/journal_db

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=redis_pass

# Security
SECRET_KEY=generate-a-secure-random-key-here
JWT_SECRET_KEY=generate-another-secure-key

# CORS
CORS_ORIGINS=["http://localhost:3000"]
```

### 3. Generate Secret Keys

```bash
# Generate strong secret keys
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
# Copy output to SECRET_KEY

python3 -c "import secrets; print(secrets.token_urlsafe(32))"
# Copy output to JWT_SECRET_KEY
```

### 4. Start Services

```bash
# Start all services
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f
```

### 5. Initialize Database

```bash
# Run migrations
docker compose exec backend python -m alembic upgrade head

# Or run SQL directly
docker compose exec backend python backend/models_additional.py > schema.sql
docker compose exec db psql -U journal_user -d journal_db -f /app/schema.sql
```

### 6. Create Admin User

```bash
docker compose exec backend python -c "
from models import User
from database import SessionLocal
from passlib.context import CryptContext

db = SessionLocal()
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

admin = User(
    email='admin@journal.com',
    username='admin',
    password=pwd_context.hash('ChangeMe123!'),
    role='editor',
    is_active=True
)
db.add(admin)
db.commit()
print('Admin user created: admin@journal.com / ChangeMe123!')
"
```

### 7. Access Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Redis**: localhost:6379

---

## Database Setup

### PostgreSQL Configuration

**Create database and user:**

```sql
-- Connect to PostgreSQL
psql -U postgres

-- Create user
CREATE USER journal_user WITH PASSWORD 'journal_pass';

-- Create database
CREATE DATABASE journal_db OWNER journal_user;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE journal_db TO journal_user;

-- Exit
\q
```

**Run migrations:**

```bash
# Copy SQL schema
docker compose exec backend python models_additional.py > schema.sql

# Execute schema
docker compose exec db psql -U journal_user -d journal_db -f /app/schema.sql
```

### Verify Database

```bash
# Connect to database
docker compose exec db psql -U journal_user -d journal_db

# List tables
\dt

# Expected tables:
# - ab_tests, ab_variants, ab_assignments, ab_exposures, ab_conversions
# - user_profiles, user_interests, reading_history
# - article_views, article_downloads, user_sessions, search_queries
# + your existing tables

# Exit
\q
```

### Database Backup

```bash
# Create backup
docker compose exec db pg_dump -U journal_user journal_db > backup_$(date +%Y%m%d).sql

# Restore backup
docker compose exec -T db psql -U journal_user journal_db < backup_20241107.sql
```

---

## Redis Setup

### Redis Configuration

**Default configuration (docker-compose.yml):**
```yaml
redis:
  image: redis:7-alpine
  command: redis-server --appendonly yes --requirepass redis_pass
  ports:
    - "6379:6379"
  volumes:
    - redis_data:/data
```

**Custom redis.conf (optional):**

```bash
# Create redis config
cat > redis/redis.conf <<EOF
# Network
bind 0.0.0.0
port 6379
requirepass redis_pass

# Persistence
appendonly yes
appendfsync everysec

# Memory
maxmemory 2gb
maxmemory-policy allkeys-lru

# Logging
loglevel notice
logfile /var/log/redis/redis.log
EOF

# Update docker-compose.yml to mount config
# volumes:
#   - ./redis/redis.conf:/usr/local/etc/redis/redis.conf
# command: redis-server /usr/local/etc/redis/redis.conf
```

### Verify Redis

```bash
# Connect to Redis
docker compose exec redis redis-cli -a redis_pass

# Test connection
127.0.0.1:6379> PING
PONG

# Check memory usage
127.0.0.1:6379> INFO memory

# View keys (development only)
127.0.0.1:6379> KEYS *

# Exit
127.0.0.1:6379> exit
```

### Redis Monitoring

```bash
# View real-time commands
docker compose exec redis redis-cli -a redis_pass MONITOR

# Get server info
docker compose exec redis redis-cli -a redis_pass INFO

# Check connected clients
docker compose exec redis redis-cli -a redis_pass CLIENT LIST
```

---

## Backend Deployment

### Build Backend

```bash
# Build image
docker compose build backend

# Or pull from registry
docker pull yourorg/journal-backend:latest
```

### Environment Variables

Create `backend/.env` with all required settings (see Environment Variables section below).

### Run Migrations

```bash
# Apply database migrations
docker compose exec backend alembic upgrade head

# Verify
docker compose exec backend alembic current
```

### Start Backend

```bash
# Start backend service
docker compose up -d backend

# Check logs
docker compose logs -f backend

# Check health
curl http://localhost:8000/health
# {"status":"healthy","performance":"optimized"}
```

### Celery Workers

```bash
# Start Celery worker
docker compose up -d celery_worker

# Check status
docker compose exec celery_worker celery -A tasks inspect active

# Monitor tasks
docker compose exec celery_worker celery -A tasks events
```

---

## Frontend Deployment

### Build Frontend

**Development:**
```bash
cd frontend
npm install
npm run dev
```

**Production:**
```bash
cd frontend

# Install dependencies
npm ci --production

# Build for production
npm run build

# Output in: frontend/dist/
```

### Deploy Static Files

**Option 1: Nginx (Recommended)**
```nginx
server {
    listen 80;
    server_name yourjournal.com;

    # Frontend static files
    location / {
        root /var/www/journal/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API proxy
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # WebSocket proxy
    location /api/v1/ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

**Option 2: Docker**
```bash
docker compose up -d frontend
```

**Option 3: CDN**
- Upload `frontend/dist/` to S3/CloudFront
- Configure CORS for API access

---

## Production Deployment

### Pre-Deployment Checklist

- [ ] All environment variables configured
- [ ] SECRET_KEY and JWT_SECRET_KEY are strong & unique
- [ ] Database backup created
- [ ] Redis password set
- [ ] HTTPS certificate obtained
- [ ] Domain DNS configured
- [ ] Firewall rules configured
- [ ] Monitoring tools set up
- [ ] Error tracking configured (Sentry)
- [ ] Log aggregation configured (ELK/Loki)

### SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourjournal.com -d www.yourjournal.com

# Auto-renewal (Certbot sets this up automatically)
sudo certbot renew --dry-run
```

### Production docker-compose.yml

```bash
# Use production compose file
docker compose -f docker-compose.prod.yml up -d

# Or set profile
docker compose --profile production up -d
```

### Nginx Production Config

```nginx
# /etc/nginx/sites-available/journal
server {
    listen 80;
    server_name yourjournal.com www.yourjournal.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourjournal.com www.yourjournal.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourjournal.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourjournal.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Gzip Compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    gzip_min_length 1000;

    # Frontend
    location / {
        root /var/www/journal/frontend/dist;
        try_files $uri $uri/ /index.html;
        expires 1h;
    }

    # API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
    }

    # WebSocket
    location /api/v1/ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }

    # Static files with aggressive caching
    location /static {
        alias /var/www/journal/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### Enable and Start Nginx

```bash
# Test configuration
sudo nginx -t

# Enable site
sudo ln -s /etc/nginx/sites-available/journal /etc/nginx/sites-enabled/

# Reload Nginx
sudo systemctl reload nginx

# Enable auto-start
sudo systemctl enable nginx
```

### Firewall Configuration

```bash
# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

---

## Environment Variables

### Backend Environment (.env)

```bash
# ==================== Database ====================
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# ==================== Redis ====================
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password
REDIS_DB=0
REDIS_URL=redis://:your-redis-password@redis:6379/0

# ==================== Security ====================
SECRET_KEY=your-secret-key-min-32-chars
JWT_SECRET_KEY=your-jwt-secret-key-min-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# ==================== CORS ====================
CORS_ORIGINS=["https://yourjournal.com","https://www.yourjournal.com"]
CORS_ALLOW_CREDENTIALS=true

# ==================== API ====================
API_V1_PREFIX=/api/v1
PROJECT_NAME=Diamond OA Journal
DEBUG=false

# ==================== Email (SMTP) ====================
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=noreply@yourjournal.com
SMTP_TLS=true

# ==================== AWS S3 (Optional) ====================
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_S3_BUCKET=journal-uploads
AWS_REGION=us-east-1

# ==================== Celery ====================
CELERY_BROKER_URL=redis://:your-redis-password@redis:6379/1
CELERY_RESULT_BACKEND=redis://:your-redis-password@redis:6379/1

# ==================== Monitoring (Optional) ====================
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
LOG_LEVEL=INFO

# ==================== Features ====================
ENABLE_AB_TESTING=true
ENABLE_PERSONALIZATION=true
ENABLE_ANALYTICS=true
ENABLE_CACHE=true
```

### Frontend Environment (.env)

```bash
# API URL
VITE_API_URL=https://yourjournal.com

# WebSocket URL
VITE_WS_URL=wss://yourjournal.com

# Features
VITE_ENABLE_AB_TESTING=true
VITE_ENABLE_PERSONALIZATION=true
VITE_ENABLE_ANALYTICS=true

# Google Analytics (Optional)
VITE_GA_ID=G-XXXXXXXXXX

# Sentry (Optional)
VITE_SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
```

---

## Monitoring & Maintenance

### Health Checks

```bash
# Backend health
curl https://yourjournal.com/health
# {"status":"healthy","performance":"optimized"}

# Redis health
docker compose exec redis redis-cli -a redis_pass PING
# PONG

# Database health
docker compose exec db pg_isready -U journal_user
# journal_db:5432 - accepting connections
```

### Log Monitoring

```bash
# View all logs
docker compose logs -f

# Backend logs only
docker compose logs -f backend

# Tail last 100 lines
docker compose logs --tail=100 backend

# Follow with grep filter
docker compose logs -f backend | grep ERROR
```

### Resource Monitoring

```bash
# Container stats
docker stats

# Disk usage
docker system df

# Clean up
docker system prune -a --volumes
```

### Database Maintenance

```bash
# Vacuum database
docker compose exec db psql -U journal_user -d journal_db -c "VACUUM FULL ANALYZE;"

# Check table sizes
docker compose exec db psql -U journal_user -d journal_db -c "
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"

# Reindex
docker compose exec db psql -U journal_user -d journal_db -c "REINDEX DATABASE journal_db;"
```

### Redis Maintenance

```bash
# Check memory
docker compose exec redis redis-cli -a redis_pass INFO memory

# Flush database (DANGER!)
docker compose exec redis redis-cli -a redis_pass FLUSHDB

# Save snapshot
docker compose exec redis redis-cli -a redis_pass BGSAVE

# Check last save time
docker compose exec redis redis-cli -a redis_pass LASTSAVE
```

### Backup Strategy

**Daily Backups:**
```bash
#!/bin/bash
# /opt/journal/backup.sh

DATE=$(date +%Y%m%d)
BACKUP_DIR=/backups/journal

# Database backup
docker compose exec -T db pg_dump -U journal_user journal_db | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Redis backup
docker compose exec redis redis-cli -a redis_pass --rdb /data/dump.rdb
cp /var/lib/docker/volumes/journal_redis_data/_data/dump.rdb $BACKUP_DIR/redis_$DATE.rdb

# Files backup
tar -czf $BACKUP_DIR/files_$DATE.tar.gz /var/www/journal/uploads

# Delete old backups (keep 30 days)
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
find $BACKUP_DIR -name "*.rdb" -mtime +30 -delete

echo "Backup completed: $DATE"
```

**Cron Schedule:**
```cron
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /opt/journal/backup.sh >> /var/log/journal-backup.log 2>&1
```

---

## Troubleshooting

### Issue: Backend won't start

**Symptoms:**
- Container exits immediately
- Error in logs: "Connection refused"

**Solutions:**
```bash
# Check database is ready
docker compose exec db pg_isready -U journal_user

# Check Redis is ready
docker compose exec redis redis-cli -a redis_pass PING

# View backend logs
docker compose logs backend

# Restart with fresh build
docker compose down
docker compose build --no-cache backend
docker compose up -d
```

### Issue: High memory usage

**Symptoms:**
- Redis memory > 2 GB
- OOM errors

**Solutions:**
```bash
# Check Redis memory
docker compose exec redis redis-cli -a redis_pass INFO memory

# Set max memory
docker compose exec redis redis-cli -a redis_pass CONFIG SET maxmemory 2gb
docker compose exec redis redis-cli -a redis_pass CONFIG SET maxmemory-policy allkeys-lru

# Clear cache if needed
docker compose exec redis redis-cli -a redis_pass FLUSHDB
```

### Issue: Slow database queries

**Symptoms:**
- API responses > 1 second
- High CPU on database

**Solutions:**
```bash
# Check slow queries
docker compose exec db psql -U journal_user -d journal_db -c "
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
"

# Add missing indexes
docker compose exec db psql -U journal_user -d journal_db -c "
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_article_views_article_id ON article_views(article_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_article_views_viewed_at ON article_views(viewed_at);
"

# Vacuum and analyze
docker compose exec db psql -U journal_user -d journal_db -c "VACUUM ANALYZE;"
```

### Issue: WebSocket not connecting

**Symptoms:**
- Real-time features not working
- Browser console error: "WebSocket failed"

**Solutions:**
```bash
# Check Nginx WebSocket config
sudo nginx -t

# Verify proxy_http_version 1.1
# Verify Upgrade and Connection headers

# Check backend WebSocket endpoint
curl -i -N \
  -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Version: 13" \
  -H "Sec-WebSocket-Key: test" \
  http://localhost:8000/api/v1/ws/test

# Restart Nginx
sudo systemctl restart nginx
```

### Issue: Frontend build fails

**Symptoms:**
- `npm run build` fails
- Out of memory error

**Solutions:**
```bash
# Increase Node memory
NODE_OPTIONS=--max-old-space-size=4096 npm run build

# Clean and rebuild
rm -rf node_modules package-lock.json
npm install
npm run build

# Use production dependencies only
npm ci --production
```

---

## Scaling & Performance

### Horizontal Scaling

**Backend:**
```yaml
# docker-compose.prod.yml
backend:
  deploy:
    replicas: 3
  # ... other config

nginx:
  # Add upstream load balancing in nginx.conf
```

**Database:**
- Set up read replicas
- Use connection pooling (PgBouncer)
- Implement sharding for large tables

**Redis:**
- Set up Redis Cluster (3+ nodes)
- Use Redis Sentinel for HA
- Separate cache and session Redis instances

### Performance Tuning

**Backend:**
```python
# Increase worker count
uvicorn main:app --workers 4 --host 0.0.0.0 --port 8000

# Use Gunicorn
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

**Database:**
```sql
-- Optimize for analytics queries
SET work_mem = '256MB';
SET maintenance_work_mem = '512MB';
SET effective_cache_size = '4GB';
SET shared_buffers = '1GB';
```

**Redis:**
```conf
# redis.conf
maxmemory 4gb
maxmemory-policy allkeys-lru
save ""  # Disable RDB for cache-only use
```

---

## Support

For deployment issues:
- Email: devops@yourjournal.com
- Slack: #journal-deployment
- GitHub: https://github.com/yourorg/Journal/issues

---

**Document Version:** 1.0
**Last Updated:** November 2024
