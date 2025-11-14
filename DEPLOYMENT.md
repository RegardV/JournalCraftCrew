# Journal Craft Crew - Deployment Guide

## 📋 Table of Contents

1. [Development Environments](#development-environments)
2. [Production Deployment](#production-deployment)
3. [Platform-Specific Instructions](#platform-specific-instructions)
4. [Docker Deployment](#docker-deployment)
5. [CI/CD Integration](#cicd-integration)
6. [Environment Configuration](#environment-configuration)
7. [Troubleshooting](#troubleshooting)

---

## 🛠️ Development Environments

### GitHub Codespaces (Recommended for Quick Start)

**Instant Cloud Development Environment**

1. **Create Codespace**
   ```bash
   # GitHub UI: Click "Code" → "Codespaces" → "Create codespace"
   # OR CLI: gh codespace create -R RegardV/JournalCraftCrew
   ```

2. **Automatic Setup**
   - ✅ All dependencies installed automatically
   - ✅ Development servers started on creation
   - ✅ VS Code extensions pre-configured
   - ✅ Ports forwarded and ready to use

3. **Access Your Development Environment**
   - **Frontend**: `https://<codespace-name>-5173.github.dev`
   - **Backend API**: `https://<codespace-name>-6770.github.dev`
   - **Dashboard**: `https://<codespace-name>-6771.github.dev`
   - **Agent Overview**: `https://<codespace-name>-6771.github.dev/agent-overview`

4. **Codespace Features**
   - 🚀 **Zero Setup**: Fully configured environment in 2-3 minutes
   - 💻 **VS Code Online**: Full IDE experience in browser
   - 🔧 **Pre-installed Tools**: Python 3.12, Node.js 18, UV, Docker
   - 🚦 **Auto Port Forwarding**: All services accessible via HTTPS
   - 🔐 **Secure**: Isolated development environment

### Local Development (Traditional)

**Manual Setup for Your Machine**

1. **Clone and Setup**
   ```bash
   git clone https://github.com/RegardV/JournalCraftCrew.git
   cd JournalCraftCrew
   ./setup-journal-crew.sh
   ./start-journal-crew.sh
   ```

2. **Access Points**
   - Frontend: http://localhost:5173
   - Backend: https://localhost:6770
   - Dashboard: http://localhost:6771

---

## 🚀 Production Deployment

### Prerequisites

- **Server Requirements**: 2+ CPU, 4+ GB RAM, 20+ GB storage
- **Operating System**: Ubuntu 20.04+, CentOS 8+, or Amazon Linux 2
- **Domain**: Configured domain name with SSL certificates
- **Database**: PostgreSQL 14+ (recommended) or MySQL 8+
- **Redis**: 6+ (recommended for caching)
- **SSL**: Valid SSL certificate (Let's Encrypt recommended)

### Quick Production Setup

1. **Server Preparation**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y

   # Install Docker & Docker Compose
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker $USER

   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

2. **Deploy with Docker**
   ```bash
   # Clone repository
   git clone https://github.com/RegardV/JournalCraftCrew.git
   cd JournalCraftCrew

   # Configure environment
   cp .env.example .env.production
   # Edit .env.production with your values

   # Deploy
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Configure Reverse Proxy**
   ```bash
   # Install Nginx
   sudo apt install nginx -y

   # Configure SSL (Let's Encrypt)
   sudo apt install certbot python3-certbot-nginx -y
   sudo certbot --nginx -d yourdomain.com

   # Copy Nginx configuration
   sudo cp deploy/nginx.conf /etc/nginx/sites-available/journal-crew
   sudo ln -s /etc/nginx/sites-available/journal-crew /etc/nginx/sites-enabled/
   sudo nginx -t && sudo systemctl reload nginx
   ```

---

## 🌐 Platform-Specific Instructions

### AWS (Amazon Web Services)

**EC2 Deployment**

1. **Launch EC2 Instance**
   ```bash
   # AWS CLI (if configured)
   aws ec2 run-instances \
     --image-id ami-0c55b159cbfafe1f0 \
     --instance-type t3.medium \
     --key-name your-key-pair \
     --security-group-ids sg-xxxxxxxxx

   # Or via AWS Console:
   # 1. Choose Ubuntu 22.04 LTS AMI
   # 2. Select t3.medium or larger instance
   # 3. Configure security group (ports 80, 443, 22)
   # 4. Launch and connect via SSH
   ```

2. **Deploy Application**
   ```bash
   # SSH into instance
   ssh -i your-key-pair.pem ubuntu@your-ec2-ip

   # Follow production setup steps
   git clone https://github.com/RegardV/JournalCraftCrew.git
   cd JournalCraftCrew
   ./setup-production.sh
   ```

3. **Configure AWS Services**
   ```bash
   # RDS PostgreSQL (Optional)
   aws rds create-db-instance \
     --db-name journal_platform \
     --db-instance-class db.t3.micro \
     --engine postgres \
     --master-username journal_user \
     --master-user-password your_password

   # ElastiCache Redis (Optional)
   aws elasticache create-cache-cluster \
     --cache-cluster-name journal-redis \
     --cache-node-type cache.t3.micro \
     --engine redis
   ```

### Google Cloud Platform (GCP)

**Compute Engine Deployment**

1. **Create VM Instance**
   ```bash
   # gcloud CLI
   gcloud compute instances create journal-crew-vm \
     --machine-type=e2-medium \
     --image-family=ubuntu-2204-lts \
     --image-project=ubuntu-os-cloud \
     --zone=us-central1-a

   # Or via Cloud Console:
   # 1. Go to Compute Engine → VM instances
   # 2. Create instance with Ubuntu 22.04
   # 3. e2-medium or larger machine type
   # 4. Allow HTTP/HTTPS traffic
   ```

2. **Deploy Application**
   ```bash
   # SSH into instance
   gcloud compute ssh journal-crew-vm --zone=us-central1-a

   # Setup and deploy
   git clone https://github.com/RegardV/JournalCraftCrew.git
   cd JournalCraftCrew
   ./setup-production.sh
   ```

3. **Configure Cloud Services**
   ```bash
   # Cloud SQL PostgreSQL (Optional)
   gcloud sql instances create journal-db \
     --database-version=POSTGRES_14 \
     --tier=db-f1-micro \
     --region=us-central1

   # Memorystore Redis (Optional)
   gcloud redis instances create journal-redis \
     --size=1 \
     --region=us-central1
   ```

### DigitalOcean

**Droplet Deployment**

1. **Create Droplet**
   ```bash
   # Using doctl CLI
   doctl compute droplet create journal-crew-droplet \
     --region nyc3 \
     --size s-2vcpu-4gb \
     --image ubuntu-22-04-x64 \
     --enable-monitoring

   # Or via DigitalOcean Console:
   # 1. Create Droplet
   # 2. Choose Ubuntu 22.04
   # 3. Select Basic plan, $20/month or higher
   # 4. Add SSH keys
   # 5. Enable IPv6 and monitoring
   ```

2. **Deploy Application**
   ```bash
   # SSH into droplet
   ssh root@your-droplet-ip

   # Create user and setup
   adduser journal
   usermod -aG sudo journal
   su - journal

   git clone https://github.com/RegardV/JournalCraftCrew.git
   cd JournalCraftCrew
   ./setup-production.sh
   ```

3. **Managed Database (Optional)**
   ```bash
   # DigitalOcean Managed PostgreSQL
   # Create via Console: Databases → PostgreSQL Cluster
   # Choose plan, region, and version
   # Add connection string to .env.production
   ```

---

## 🐳 Docker Deployment

### Development Docker

```bash
# Build development image
docker build -f .devcontainer/Dockerfile -t journal-crew:dev .

# Run with docker-compose
docker-compose -f docker-compose.dev.yml up -d

# Access services
# Frontend: http://localhost:5173
# Backend: http://localhost:6770
# Dashboard: http://localhost:6771
```

### Production Docker

```bash
# Build production image
docker build -t journal-crew:latest .

# Run with environment variables
docker run -d \
  --name journal-crew \
  -p 80:5173 \
  -p 443:6770 \
  -e DATABASE_URL="postgresql://user:pass@host:5432/db" \
  -e OPENAI_API_KEY="your-api-key" \
  -v /path/to/ssl:/app/ssl \
  journal-crew:latest

# Or use production compose
docker-compose -f docker-compose.prod.yml up -d
```

### Docker Compose Production

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  frontend:
    build:
      context: ./journal-platform-frontend
      dockerfile: Dockerfile.prod
    ports:
      - "80:80"
    environment:
      - VITE_API_URL=https://yourdomain.com

  backend:
    build:
      context: ./journal-platform-backend
      dockerfile: Dockerfile.prod
    ports:
      - "443:6770"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - ./ssl:/app/ssl

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

---

## ⚙️ CI/CD Integration

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: ./setup-journal-crew.sh
      - name: Run tests
        run: |
          npm test
          pytest

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build Docker image
        run: docker build -t journal-crew:${{ github.sha }} .
      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker tag journal-crew:${{ github.sha }} your-registry/journal-crew:latest
          docker push your-registry/journal-crew:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to server
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /opt/journal-crew
            docker-compose pull
            docker-compose up -d
            docker system prune -f
```

### GitLab CI/CD

Create `.gitlab-ci.yml`:

```yaml
stages:
  - test
  - build
  - deploy

variables:
  DOCKER_DRIVER: overlay2
  DOCKER_TLS_CERTDIR: "/certs"

test:
  stage: test
  image: python:3.12
  services:
    - postgres:15
  script:
    - apt-get update -qy
    - apt-get install -y nodejs npm
    - ./setup-journal-crew.sh
    - npm test
    - pytest

build:
  stage: build
  image: docker:20.10.16
  services:
    - docker:20.10.16-dind
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

deploy:
  stage: deploy
  image: alpine:latest
  before_script:
    - apk add --no-cache openssh-client
    - eval $(ssh-agent -s)
    - echo "$SSH_PRIVATE_KEY" | tr -d '\r' | ssh-add -
    - mkdir -p ~/.ssh
    - chmod 700 ~/.ssh
    - echo -e "Host *\n\tStrictHostKeyChecking no\n\n" > ~/.ssh/config
  script:
    - ssh $SERVER_USER@$SERVER_HOST "cd /opt/journal-crew && docker-compose pull && docker-compose up -d"
  only:
    - main
```

---

## 🔧 Environment Configuration

### Environment Variables

**Backend (.env.production)**
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/journal_platform

# Security
SECRET_KEY=your-super-secret-production-key
JWT_SECRET_KEY=your-jwt-secret-key
ENVIRONMENT=production

# APIs
OPENAI_API_KEY=sk-your-openai-api-key

# Services
REDIS_URL=redis://localhost:6379
CELERY_BROKER_URL=redis://localhost:6379

# SSL
SSL_CERT_PATH=/app/ssl/journal_crew.crt
SSL_KEY_PATH=/app/ssl/journal_crew.key

# Monitoring
SENTRY_DSN=your-sentry-dsn
LOG_LEVEL=INFO

# File Storage
UPLOAD_PATH=/app/uploads
MAX_FILE_SIZE=10485760
```

**Frontend (.env.production)**
```bash
VITE_API_URL=https://yourdomain.com
VITE_WS_URL=wss://yourdomain.com
VITE_ENVIRONMENT=production
VITE_SENTRY_DSN=your-frontend-sentry-dsn
```

### Production Checklist

- [ ] **Security**: SSL certificates installed and configured
- [ ] **Database**: Production database created and migrated
- [ ] **Environment**: All required environment variables set
- [ ] **Backup**: Database and file backup strategy implemented
- [ ] **Monitoring**: Application monitoring and alerting configured
- [ ] **Logging**: Centralized logging setup
- [ ] **Performance**: Caching and CDN configured
- [ ] **Scaling**: Auto-scaling policies configured (if needed)
- [ ] **Domain**: DNS records pointing to server
- [ ] **Firewall**: Security rules configured

---

## 🔍 Troubleshooting

### Common Issues

#### 1. Port Conflicts
```bash
# Check what's using ports
sudo netstat -tulpn | grep :5173
sudo netstat -tulpn | grep :6770

# Kill conflicting processes
sudo kill -9 <PID>
```

#### 2. SSL Certificate Issues
```bash
# Verify certificate
openssl x509 -in ssl/journal_crew.crt -text -noout

# Check certificate validity
openssl s_client -connect localhost:6770 -servername localhost
```

#### 3. Database Connection Issues
```bash
# Test database connection
psql -h localhost -U journal_user -d journal_platform

# Check PostgreSQL status
sudo systemctl status postgresql
```

#### 4. Docker Issues
```bash
# Check container logs
docker logs journal-crew-backend-1
docker logs journal-crew-frontend-1

# Restart containers
docker-compose restart

# Clean up Docker
docker system prune -a
```

#### 5. Performance Issues
```bash
# Check system resources
htop
df -h
free -h

# Monitor application
docker stats
tail -f /var/log/nginx/error.log
```

### Health Checks

```bash
# Backend health check
curl -f https://yourdomain.com/health || exit 1

# Frontend health check
curl -f https://yourdomain.com || exit 1

# Database connection
python -c "import asyncio; from app.core.database import engine; asyncio.run(engine.connect())"
```

### Log Locations

- **Backend logs**: `/var/log/journal-crew/backend.log`
- **Nginx logs**: `/var/log/nginx/access.log`, `/var/log/nginx/error.log`
- **System logs**: `/var/log/syslog`
- **Docker logs**: `docker logs <container-name>`

### Support Channels

- **Documentation**: [Project README](README.md)
- **Issues**: [GitHub Issues](https://github.com/RegardV/JournalCraftCrew/issues)
- **Community**: [Discord Server](https://discord.gg/journalcraftcrew)
- **Email**: support@journalcraftcrew.com

---

## 📊 Monitoring and Maintenance

### Application Monitoring

```bash
# Set up monitoring with Prometheus
docker run -d \
  --name prometheus \
  -p 9090:9090 \
  -v /path/to/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus

# Set up Grafana for dashboards
docker run -d \
  --name grafana \
  -p 3000:3000 \
  grafana/grafana
```

### Backup Strategy

```bash
# Database backup
pg_dump -h localhost -U journal_user journal_platform > backup_$(date +%Y%m%d_%H%M%S).sql

# File backup
tar -czf uploads_backup_$(date +%Y%m%d_%H%M%S).tar.gz uploads/

# Automated backup script
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -h localhost -U journal_user journal_platform > /backups/db_$DATE.sql
tar -czf /backups/uploads_$DATE.tar.gz uploads/
find /backups -name "*.sql" -mtime +7 -delete
find /backups -name "*.tar.gz" -mtime +7 -delete
```

---

*This deployment guide covers all major platforms and deployment methods for the Journal Craft Crew application. For additional support, please refer to the project documentation or contact the development team.*