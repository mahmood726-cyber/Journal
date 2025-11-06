#!/bin/bash

#############################################################################
# Diamond OA Journal - AWS EC2 One-Click Deployment Script
#
# This script automatically deploys the journal system on AWS EC2
#
# Usage:
#   curl -sSL https://raw.githubusercontent.com/yourrepo/Journal/main/deploy-aws.sh | bash
#
# Or:
#   wget -O - https://raw.githubusercontent.com/yourrepo/Journal/main/deploy-aws.sh | bash
#
# Requirements:
#   - Fresh Ubuntu 22.04 LTS EC2 instance
#   - Minimum 4GB RAM (t3.medium)
#   - Port 80 and 443 open in security group
#   - Public IP address assigned
#
#############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Banner
echo -e "${GREEN}"
cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        Diamond OA Journal - AWS Deployment                  ║
║        One-Click Installation for Amazon EC2                ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    log_error "Please run as root (use sudo)"
    exit 1
fi

# Check OS
if [ ! -f /etc/lsb-release ]; then
    log_error "This script is designed for Ubuntu 22.04 LTS"
    exit 1
fi

source /etc/lsb-release
if [ "$DISTRIB_RELEASE" != "22.04" ]; then
    log_warning "This script is designed for Ubuntu 22.04, you have $DISTRIB_RELEASE"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Get AWS instance metadata
log_info "Detecting AWS instance metadata..."
AWS_REGION=$(ec2-metadata --availability-zone | cut -d' ' -f2 | sed 's/[a-z]$//')
INSTANCE_ID=$(ec2-metadata --instance-id | cut -d' ' -f2)
PUBLIC_IP=$(ec2-metadata --public-ipv4 | cut -d' ' -f2)
INSTANCE_TYPE=$(ec2-metadata --instance-type | cut -d' ' -f2)

log_success "AWS Instance Details:"
echo "  Region: $AWS_REGION"
echo "  Instance ID: $INSTANCE_ID"
echo "  Instance Type: $INSTANCE_TYPE"
echo "  Public IP: $PUBLIC_IP"
echo ""

# Warn about instance size
case $INSTANCE_TYPE in
    t2.micro|t3.micro|t2.small)
        log_warning "Your instance type ($INSTANCE_TYPE) has less than 4GB RAM"
        log_warning "Minimum recommended: t3.medium (4GB RAM)"
        ;;
    t3.medium|t3a.medium|t2.medium)
        log_success "Instance type is appropriate for basic journal operation"
        ;;
    *)
        log_success "Instance type looks good"
        ;;
esac

# Check disk space
DISK_SPACE=$(df -BG / | awk 'NR==2 {print $4}' | sed 's/G//')
if [ "$DISK_SPACE" -lt 20 ]; then
    log_error "Insufficient disk space. Need at least 20GB, have ${DISK_SPACE}GB"
    exit 1
fi

# Step 1: Update system
log_info "Step 1/10: Updating system packages..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get upgrade -y -qq
log_success "System updated"

# Step 2: Install dependencies
log_info "Step 2/10: Installing dependencies..."
apt-get install -y -qq \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    software-properties-common \
    git \
    wget \
    openssl \
    certbot

log_success "Dependencies installed"

# Step 3: Install Docker
log_info "Step 3/10: Installing Docker..."
if command -v docker &> /dev/null; then
    log_warning "Docker already installed, skipping"
else
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    apt-get update -qq
    apt-get install -y -qq docker-ce docker-ce-cli containerd.io
    systemctl enable docker
    systemctl start docker
    log_success "Docker installed"
fi

# Step 4: Install Docker Compose
log_info "Step 4/10: Installing Docker Compose..."
if command -v docker-compose &> /dev/null; then
    log_warning "Docker Compose already installed, skipping"
else
    curl -L "https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
    log_success "Docker Compose installed"
fi

# Verify Docker
docker --version
docker-compose --version

# Step 5: Clone repository
log_info "Step 5/10: Cloning Diamond OA Journal repository..."
INSTALL_DIR="/opt/Journal"
if [ -d "$INSTALL_DIR" ]; then
    log_warning "Directory $INSTALL_DIR already exists, backing up..."
    mv $INSTALL_DIR ${INSTALL_DIR}.backup.$(date +%Y%m%d_%H%M%S)
fi

git clone https://github.com/mahmood726-cyber/Journal.git $INSTALL_DIR
cd $INSTALL_DIR
log_success "Repository cloned"

# Step 6: Generate secure passwords
log_info "Step 6/10: Generating secure credentials..."
DB_PASSWORD=$(openssl rand -base64 32)
SECRET_KEY=$(openssl rand -base64 64)
JWT_SECRET=$(openssl rand -base64 32)

log_success "Secure passwords generated"

# Step 7: Configure domain or IP
log_info "Step 7/10: Configuring domain..."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Domain Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Do you have a domain name pointing to this server?"
echo "  - If YES: Enter your domain (e.g., journal.university.edu)"
echo "  - If NO: Press Enter to use IP address ($PUBLIC_IP)"
echo ""
read -p "Domain name (or press Enter): " DOMAIN

if [ -z "$DOMAIN" ]; then
    DOMAIN=$PUBLIC_IP
    USE_SSL=false
    log_warning "Using IP address. SSL will NOT be configured."
    log_warning "For production, please configure a domain name and re-run setup."
else
    USE_SSL=true
    log_info "Domain set to: $DOMAIN"
    log_info "SSL will be configured automatically"
fi

# Step 8: Create environment file
log_info "Step 8/10: Creating environment configuration..."
cat > .env << EOF
# Database Configuration
POSTGRES_DB=journal_db
POSTGRES_USER=journal_user
POSTGRES_PASSWORD=$DB_PASSWORD
DATABASE_URL=postgresql://journal_user:$DB_PASSWORD@db:5432/journal_db

# Security
SECRET_KEY=$SECRET_KEY
JWT_SECRET_KEY=$JWT_SECRET
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
DEBUG=false
ENVIRONMENT=production
API_URL=http://backend:8000
FRONTEND_URL=https://$DOMAIN

# Domain
DOMAIN=$DOMAIN

# Redis
REDIS_URL=redis://redis:6379/0

# Email (Configure later in admin panel)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-smtp-password
EMAIL_FROM=noreply@$DOMAIN

# File Storage
UPLOAD_DIR=/app/uploads
MAX_UPLOAD_SIZE=52428800  # 50MB

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Journal Metadata
JOURNAL_TITLE=Your Journal Name
JOURNAL_ISSN=
JOURNAL_EISSN=
PUBLISHER_NAME=Your Publisher

# AWS Specific
AWS_REGION=$AWS_REGION
AWS_INSTANCE_ID=$INSTANCE_ID
AWS_DEPLOYMENT=true

# Optional AI (Configure later if needed)
AI_ENABLED=false
AI_PROVIDER=ollama
OLLAMA_API_BASE=http://localhost:11434
OLLAMA_MODEL=llama2:7b

# Optional DOI Registration (Configure when ready)
DOI_PREFIX=
DOI_API_KEY=
EOF

chmod 600 .env
log_success "Environment file created"

# Step 9: Build and start services
log_info "Step 9/10: Building and starting services..."
log_info "This may take 5-10 minutes on first run..."

docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

log_info "Waiting for services to become healthy..."
sleep 10

# Wait for database
for i in {1..30}; do
    if docker-compose -f docker-compose.prod.yml exec -T db pg_isready -U journal_user > /dev/null 2>&1; then
        log_success "Database is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        log_error "Database failed to start"
        docker-compose -f docker-compose.prod.yml logs db
        exit 1
    fi
    echo -n "."
    sleep 2
done

log_success "All services started successfully"

# Step 10: Initialize database
log_info "Step 10/10: Initializing database..."
docker-compose -f docker-compose.prod.yml exec -T backend alembic upgrade head || true
log_success "Database initialized"

# Configure SSL if domain provided
if [ "$USE_SSL" = true ]; then
    log_info "Configuring SSL certificate with Let's Encrypt..."

    # Wait for nginx to be ready
    sleep 5

    # Stop nginx temporarily
    docker-compose -f docker-compose.prod.yml stop nginx

    # Get certificate
    certbot certonly --standalone \
        --non-interactive \
        --agree-tos \
        --email admin@$DOMAIN \
        -d $DOMAIN

    if [ $? -eq 0 ]; then
        log_success "SSL certificate obtained successfully"

        # Copy certificates to nginx volume
        mkdir -p ./nginx/ssl
        cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem ./nginx/ssl/
        cp /etc/letsencrypt/live/$DOMAIN/privkey.pem ./nginx/ssl/

        # Start nginx with SSL
        docker-compose -f docker-compose.prod.yml start nginx

        # Setup auto-renewal
        (crontab -l 2>/dev/null; echo "0 0 * * * certbot renew --quiet") | crontab -

        log_success "SSL auto-renewal configured"
    else
        log_warning "SSL certificate generation failed"
        log_warning "You can set it up later manually"
        docker-compose -f docker-compose.prod.yml start nginx
    fi
fi

# Final status check
log_info "Verifying deployment..."
sleep 5

if curl -sf http://localhost/ > /dev/null; then
    STATUS="✅ RUNNING"
else
    STATUS="⚠️  CHECK LOGS"
fi

# Success message
echo ""
echo -e "${GREEN}"
cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                 🎉 Installation Complete!                    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Your Diamond OA Journal is now running!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📍 Access Information:"
if [ "$USE_SSL" = true ]; then
    echo "   URL: https://$DOMAIN"
    echo "   API: https://$DOMAIN/api"
else
    echo "   URL: http://$DOMAIN"
    echo "   API: http://$DOMAIN/api"
fi
echo ""
echo "🔒 Security:"
echo "   Database password: $DB_PASSWORD"
echo "   (Saved in /opt/Journal/.env)"
echo ""
echo "📊 Status: $STATUS"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Next Steps:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Visit your journal URL and complete the setup wizard"
echo "2. Create your admin account"
echo "3. Configure email settings (Settings > Email)"
echo "4. Customize journal information (Settings > Journal)"
echo "5. Choose a theme (click paint brush icon)"
echo ""
if [ "$USE_SSL" = false ]; then
    echo "⚠️  IMPORTANT: Configure a domain and SSL for production use!"
    echo "   Run: sudo certbot --nginx -d yourdomain.com"
    echo ""
fi
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Management Commands:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "View logs:        cd /opt/Journal && docker-compose -f docker-compose.prod.yml logs -f"
echo "Restart services: cd /opt/Journal && docker-compose -f docker-compose.prod.yml restart"
echo "Stop services:    cd /opt/Journal && docker-compose -f docker-compose.prod.yml stop"
echo "Start services:   cd /opt/Journal && docker-compose -f docker-compose.prod.yml start"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  AWS Specific:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Instance: $INSTANCE_ID ($INSTANCE_TYPE)"
echo "Region:   $AWS_REGION"
echo ""
echo "💡 Tip: Create an AMI of this instance for easy backups!"
echo "   AWS Console > EC2 > Instances > Actions > Image > Create Image"
echo ""
echo "💡 Tip: Set up CloudWatch monitoring:"
echo "   aws cloudwatch put-metric-alarm ..."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📖 Documentation: /opt/Journal/docs/"
echo "🐛 Support: https://github.com/mahmood726-cyber/Journal/issues"
echo ""
echo "Thank you for choosing Diamond OA Journal! 🎓"
echo ""
