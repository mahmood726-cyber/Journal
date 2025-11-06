# Deployment Guide

This guide covers deploying the Diamond OA Journal Management System in various environments.

## Quick Start with Docker

The fastest way to get started is using Docker Compose:

```bash
# Clone the repository
git clone https://github.com/mahmood726-cyber/Journal.git
cd Journal

# Copy environment file
cp backend/.env.example backend/.env

# Edit .env with your configuration
nano backend/.env

# Start all services
docker-compose up -d

# Initialize database
docker-compose exec backend python /app/../scripts/init_db.py

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Manual Installation

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis 6+

### Backend Setup

1. **Install Python dependencies:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your settings
```

3. **Initialize database:**
```bash
# Create PostgreSQL database
createdb journal_db

# Run migrations
alembic upgrade head

# Initialize with default data
python ../scripts/init_db.py
```

4. **Start backend server:**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

5. **Start Celery worker (in another terminal):**
```bash
celery -A tasks worker --loglevel=info
```

### Frontend Setup

1. **Install dependencies:**
```bash
cd frontend
npm install
```

2. **Configure environment:**
```bash
# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
```

3. **Start development server:**
```bash
npm run dev
```

## Production Deployment

### Option 1: VPS/Dedicated Server

#### 1. Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3.11 python3.11-venv postgresql redis-server nginx certbot python3-certbot-nginx

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

#### 2. Database Setup

```bash
# Create PostgreSQL user and database
sudo -u postgres psql
CREATE USER journal_user WITH PASSWORD 'secure_password';
CREATE DATABASE journal_db OWNER journal_user;
GRANT ALL PRIVILEGES ON DATABASE journal_db TO journal_user;
\q
```

#### 3. Application Setup

```bash
# Clone repository
git clone https://github.com/mahmood726-cyber/Journal.git /var/www/journal
cd /var/www/journal

# Backend setup
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# Configure environment
cp .env.example .env
nano .env  # Edit with production settings

# Run migrations
alembic upgrade head
python ../scripts/init_db.py

# Frontend setup
cd ../frontend
npm install
npm run build
```

#### 4. Systemd Services

Create `/etc/systemd/system/journal-backend.service`:

```ini
[Unit]
Description=Journal Backend API
After=network.target postgresql.service redis.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/journal/backend
Environment="PATH=/var/www/journal/backend/venv/bin"
ExecStart=/var/www/journal/backend/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 127.0.0.1:8000

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/journal-celery.service`:

```ini
[Unit]
Description=Journal Celery Worker
After=network.target redis.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/journal/backend
Environment="PATH=/var/www/journal/backend/venv/bin"
ExecStart=/var/www/journal/backend/venv/bin/celery -A tasks worker --loglevel=info

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/journal-frontend.service`:

```ini
[Unit]
Description=Journal Frontend
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/journal/frontend
ExecStart=/usr/bin/npm start
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
```

Enable and start services:

```bash
sudo systemctl daemon-reload
sudo systemctl enable journal-backend journal-celery journal-frontend
sudo systemctl start journal-backend journal-celery journal-frontend
```

#### 5. Nginx Configuration

Create `/etc/nginx/sites-available/journal`:

```nginx
# Backend API
server {
    listen 80;
    server_name api.yourjournal.com;

    client_max_body_size 100M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Frontend
server {
    listen 80;
    server_name yourjournal.com www.yourjournal.com;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable site and SSL:

```bash
sudo ln -s /etc/nginx/sites-available/journal /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Get SSL certificates
sudo certbot --nginx -d yourjournal.com -d www.yourjournal.com -d api.yourjournal.com
```

### Option 2: Docker in Production

1. **Update docker-compose.yml for production:**

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    restart: always
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    restart: always
    volumes:
      - redis_data:/data

  backend:
    build: ./backend
    restart: always
    command: gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
    volumes:
      - ./uploads:/app/uploads
    env_file:
      - .env.production
    depends_on:
      - db
      - redis

  celery:
    build: ./backend
    restart: always
    command: celery -A tasks worker --loglevel=info
    volumes:
      - ./uploads:/app/uploads
    env_file:
      - .env.production
    depends_on:
      - db
      - redis

  frontend:
    build: ./frontend
    restart: always
    command: npm start
    env_file:
      - .env.production
    depends_on:
      - backend

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend

volumes:
  postgres_data:
  redis_data:
```

2. **Deploy:**

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Option 3: Cloud Platforms

#### AWS Deployment

1. **Use AWS Elastic Beanstalk:**
   - Create environment
   - Deploy using Docker
   - Configure RDS for PostgreSQL
   - Configure ElastiCache for Redis

#### DigitalOcean App Platform

1. **Create app from GitHub:**
   - Connect repository
   - Configure build settings
   - Add PostgreSQL database
   - Add Redis cluster

#### Heroku

```bash
# Install Heroku CLI
heroku login

# Create app
heroku create yourjournal

# Add PostgreSQL
heroku addons:create heroku-postgresql:standard-0

# Add Redis
heroku addons:create heroku-redis:premium-0

# Deploy
git push heroku main
```

## Post-Deployment

### 1. Security Checklist

- [ ] Change default admin password
- [ ] Generate strong SECRET_KEY
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall (UFW/iptables)
- [ ] Set up fail2ban
- [ ] Configure backup strategy
- [ ] Enable database encryption
- [ ] Set up monitoring

### 2. Performance Optimization

```bash
# PostgreSQL tuning
sudo nano /etc/postgresql/15/main/postgresql.conf

# Recommended settings:
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 4MB
min_wal_size = 1GB
max_wal_size = 4GB
```

### 3. Monitoring

Set up monitoring with Prometheus and Grafana:

```yaml
# docker-compose.monitoring.yml
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

### 4. Backup Strategy

```bash
# Database backup script
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

pg_dump journal_db > $BACKUP_DIR/journal_db_$DATE.sql
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz /var/www/journal/uploads

# Keep only last 30 days
find $BACKUP_DIR -type f -mtime +30 -delete
```

Add to crontab:
```bash
0 2 * * * /path/to/backup.sh
```

## Scaling

### Horizontal Scaling

1. **Database:**
   - Use PostgreSQL replication
   - Read replicas for queries
   - Connection pooling (PgBouncer)

2. **Application:**
   - Load balancer (Nginx/HAProxy)
   - Multiple backend instances
   - Shared file storage (S3/NFS)

3. **Celery:**
   - Multiple worker instances
   - Task routing by queue
   - Monitoring with Flower

### Vertical Scaling

- Increase server resources
- Optimize database queries
- Enable caching (Redis)
- CDN for static files

## Maintenance

### Regular Tasks

```bash
# Update dependencies
pip install --upgrade -r requirements.txt
npm update

# Run database migrations
alembic upgrade head

# Clean up old files
find ./uploads -type f -mtime +365 -delete

# Vacuum database
psql journal_db -c "VACUUM ANALYZE;"
```

### Monitoring Health

```bash
# Check service status
systemctl status journal-backend journal-celery journal-frontend

# Check logs
journalctl -u journal-backend -f

# Database connections
psql journal_db -c "SELECT count(*) FROM pg_stat_activity;"

# Redis memory
redis-cli INFO memory
```

## Troubleshooting

### Common Issues

1. **Database connection errors:**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check connection
psql -h localhost -U journal_user journal_db
```

2. **Celery not processing tasks:**
```bash
# Check Redis connection
redis-cli ping

# Restart Celery
sudo systemctl restart journal-celery
```

3. **High memory usage:**
```bash
# Check processes
htop

# Restart services
sudo systemctl restart journal-backend
```

## Support

For deployment assistance:
- GitHub Issues: https://github.com/mahmood726-cyber/Journal/issues
- Documentation: https://github.com/mahmood726-cyber/Journal/docs
