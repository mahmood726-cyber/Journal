#!/bin/bash

# ================================================================
# Diamond OA Journal - One-Click Digital Ocean Deployment
# ================================================================
#
# This script automates the complete deployment of the journal
# system on a fresh Ubuntu 22.04 Digital Ocean droplet
#
# Usage:
#   curl -sSL https://raw.githubusercontent.com/yourrepo/Journal/main/deploy-digitalocean.sh | bash
# ================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "\n${BLUE}=================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}=================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root"
   exit 1
fi

print_header "Diamond OA Journal - One-Click Deployment"

# Step 1: System Update
print_header "Step 1/10: Updating System"
apt-get update -qq
apt-get upgrade -y -qq
print_success "System updated"

# Step 2: Install Docker
print_header "Step 2/10: Installing Docker"
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    systemctl enable docker
    systemctl start docker
    print_success "Docker installed"
else
    print_success "Docker already installed"
fi

# Step 3: Install Docker Compose
print_header "Step 3/10: Installing Docker Compose"
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    print_success "Docker Compose installed"
else
    print_success "Docker Compose already installed"
fi

# Step 4: Clone Repository
print_header "Step 4/10: Downloading Application"
cd /opt
if [ -d "Journal" ]; then
    print_warning "Application directory already exists, pulling latest changes"
    cd Journal
    git pull
else
    git clone https://github.com/yourrepo/Journal.git
    cd Journal
fi
print_success "Application downloaded"

# Step 5: Create Environment File
print_header "Step 5/10: Generating Configuration"

# Get server IP
SERVER_IP=$(curl -s ifconfig.me)

# Generate secure random passwords and secrets
DB_PASSWORD=$(openssl rand -base64 32)
SECRET_KEY=$(openssl rand -base64 64)

# Prompt for domain or use IP
echo -e "${YELLOW}Enter your domain name (or press Enter to use IP: $SERVER_IP):${NC}"
read -r DOMAIN
if [ -z "$DOMAIN" ]; then
    DOMAIN=$SERVER_IP
fi

cat > .env << EOF
# Database Configuration
DB_USER=journal_user
DB_PASSWORD=$DB_PASSWORD
DB_NAME=journal_db

# Application Configuration
SECRET_KEY=$SECRET_KEY
ENVIRONMENT=production
ALLOWED_HOSTS=$DOMAIN,localhost,127.0.0.1
CORS_ORIGINS=https://$DOMAIN,http://$DOMAIN

# URLs
API_URL=https://$DOMAIN/api
NEXT_PUBLIC_API_URL=https://$DOMAIN/api

# Domain
DOMAIN=$DOMAIN

# Email Configuration (configure later in admin panel)
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=journal@example.com
SMTP_PASSWORD=changeme
EMAIL_FROM=journal@example.com

# Optional Services (configure later)
STRIPE_SECRET_KEY=
ORCID_CLIENT_ID=
ORCID_CLIENT_SECRET=
CROSSREF_DOI_PREFIX=
DATACITE_PREFIX=
EOF

print_success "Configuration generated"

# Step 6: Create necessary directories
print_header "Step 6/10: Creating Directories"
mkdir -p uploads static nginx/ssl
chmod 755 uploads static
print_success "Directories created"

# Step 7: Build and Start Services
print_header "Step 7/10: Building Application (this may take 5-10 minutes)"
docker-compose -f docker-compose.prod.yml build --no-cache
print_success "Application built"

# Step 8: Start Services
print_header "Step 8/10: Starting Services"
docker-compose -f docker-compose.prod.yml up -d
print_success "Services started"

# Step 9: Wait for services to be healthy
print_header "Step 9/10: Waiting for Services"
echo "Waiting for database..."
sleep 10

# Run database migrations
print_header "Running Database Setup"
docker-compose -f docker-compose.prod.yml exec -T backend python -c "
from db.database import engine
from db.models import Base
Base.metadata.create_all(bind=engine)
print('Database initialized')
"
print_success "Database setup complete"

# Step 10: Setup SSL (if domain provided)
print_header "Step 10/10: SSL Configuration"
if [ "$DOMAIN" != "$SERVER_IP" ]; then
    print_warning "Setting up SSL for domain: $DOMAIN"

    # Update nginx config with actual domain
    sed -i "s/your-domain.com/$DOMAIN/g" nginx/nginx.conf

    # Get SSL certificate
    docker-compose -f docker-compose.prod.yml run --rm certbot certonly \
        --webroot --webroot-path=/var/www/certbot \
        --email admin@$DOMAIN \
        --agree-tos --no-eff-email \
        -d $DOMAIN

    # Reload nginx
    docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload

    print_success "SSL configured for $DOMAIN"
else
    print_warning "Using IP address. SSL not configured. Access via: http://$DOMAIN"
    print_warning "For production, please configure a domain name and SSL"
fi

# Display completion message
print_header "🎉 Installation Complete!"
echo ""
echo -e "${GREEN}Your Diamond OA Journal is now running!${NC}"
echo ""
echo -e "${BLUE}Access Information:${NC}"
if [ "$DOMAIN" != "$SERVER_IP" ]; then
    echo -e "  URL: ${GREEN}https://$DOMAIN${NC}"
else
    echo -e "  URL: ${GREEN}http://$DOMAIN${NC}"
fi
echo -e "  API: ${GREEN}https://$DOMAIN/api${NC}"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo "  1. Visit your journal and complete the setup wizard"
echo "  2. Create your admin account"
echo "  3. Configure email settings in the admin panel"
echo "  4. Customize your journal settings"
echo ""
echo -e "${BLUE}Useful Commands:${NC}"
echo "  View logs:    docker-compose -f docker-compose.prod.yml logs -f"
echo "  Stop:         docker-compose -f docker-compose.prod.yml stop"
echo "  Start:        docker-compose -f docker-compose.prod.yml start"
echo "  Restart:      docker-compose -f docker-compose.prod.yml restart"
echo "  Status:       docker-compose -f docker-compose.prod.yml ps"
echo ""
echo -e "${BLUE}Configuration Files:${NC}"
echo "  Environment:  /opt/Journal/.env"
echo "  Nginx:        /opt/Journal/nginx/nginx.conf"
echo ""
echo -e "${YELLOW}Important:${NC}"
echo "  - Your database password has been randomly generated"
echo "  - The .env file contains sensitive information"
echo "  - Configure email settings in the admin panel"
echo "  - Set up backups for the database and uploads"
echo ""
print_success "Deployment completed successfully!"
