#!/bin/bash

# =============================================================================
# Journal Craft Crew - Platform Setup Script
# =============================================================================
# Universal setup script for different deployment environments
#
# Usage: ./setup-platform.sh [environment] [options]
#
# Environments:
#   - codespaces: GitHub Codespaces development
#   - docker: Docker container development
#   - production: Production server deployment
#   - staging: Staging server deployment
#   - development: Local development (default)
#
# Options:
#   --skip-deps: Skip dependency installation
#   --skip-tests: Skip test execution
#   --monitoring: Enable monitoring services
#   --backup: Enable backup services
#
# Examples:
#   ./setup-platform.sh codespaces
#   ./setup-platform.sh production --monitoring --backup
#   ./setup-platform.sh development --skip-deps

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Global variables
ENVIRONMENT="development"
SKIP_DEPS=false
SKIP_TESTS=false
ENABLE_MONITORING=false
ENABLE_BACKUP=false
VERBOSE=false

# Default ports
FRONTEND_PORT=5173
BACKEND_PORT=6770
DASHBOARD_PORT=6771
NGINX_HTTP_PORT=80
NGINX_HTTPS_PORT=443

# Functions
print_step() {
    echo -e "${BLUE}🔧 STEP $1: $2${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo -e "${PURPLE}🚀 Journal Craft Crew - Platform Setup${NC}"
    echo -e "${PURPLE}======================================${NC}"
    echo
}

detect_environment() {
    print_step "1" "Detecting deployment environment"

    if [[ -n "$CODESPACES" ]]; then
        ENVIRONMENT="codespaces"
        print_success "Detected GitHub Codespaces environment"
    elif [[ -f "/.dockerenv" ]] || grep -q docker /proc/1/cgroup 2>/dev/null; then
        ENVIRONMENT="docker"
        print_success "Detected Docker container environment"
    elif [[ "$EUID" -eq 0 ]]; then
        print_warning "Running as root - assuming server deployment"
        read -p "Is this a production deployment? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            ENVIRONMENT="production"
        else
            ENVIRONMENT="staging"
        fi
    else
        print_success "Using default development environment"
    fi

    print_success "Environment: $ENVIRONMENT"
}

parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            codespaces|docker|production|staging|development)
                ENVIRONMENT="$1"
                shift
                ;;
            --skip-deps)
                SKIP_DEPS=true
                shift
                ;;
            --skip-tests)
                SKIP_TESTS=true
                shift
                ;;
            --monitoring)
                ENABLE_MONITORING=true
                shift
                ;;
            --backup)
                ENABLE_BACKUP=true
                shift
                ;;
            --verbose)
                VERBOSE=true
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                print_error "Unknown argument: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

show_help() {
    cat << EOF
Journal Craft Crew Platform Setup Script

Usage: $0 [environment] [options]

Environments:
    codespaces      GitHub Codespaces development environment
    docker          Docker container development environment
    production      Production server deployment
    staging         Staging server deployment
    development     Local development environment (default)

Options:
    --skip-deps     Skip dependency installation
    --skip-tests    Skip test execution
    --monitoring    Enable monitoring services
    --backup        Enable backup services
    --verbose       Verbose output
    --help, -h      Show this help message

Examples:
    $0 codespaces
    $0 production --monitoring --backup
    $0 docker --skip-deps
    $0 development --verbose

EOF
}

validate_environment() {
    print_step "2" "Validating environment requirements"

    case $ENVIRONMENT in
        codespaces)
            if [[ -z "$CODESPACES" ]]; then
                print_warning "Not running in Codespaces, but continuing anyway"
            fi
            ;;
        production)
            if [[ "$EUID" -ne 0 ]]; then
                print_error "Production setup requires root privileges"
                exit 1
            fi
            ;;
        staging)
            if [[ "$EUID" -ne 0 ]]; then
                print_error "Staging setup requires root privileges"
                exit 1
            fi
            ;;
    esac

    print_success "Environment validation passed"
}

setup_environment_variables() {
    print_step "3" "Setting up environment variables"

    case $ENVIRONMENT in
        codespaces)
            export CODESPACES=true
            export NODE_ENV=development
            export PYTHONPATH=$PWD/journal-platform-backend
            ;;
        docker)
            export DOCKER_ENV=true
            export NODE_ENV=development
            ;;
        production)
            export ENVIRONMENT=production
            export NODE_ENV=production
            export LOG_LEVEL=INFO
            ;;
        staging)
            export ENVIRONMENT=staging
            export NODE_ENV=staging
            export LOG_LEVEL=DEBUG
            ;;
        development)
            export ENVIRONMENT=development
            export NODE_ENV=development
            ;;
    esac

    print_success "Environment variables configured"
}

install_dependencies() {
    if [[ "$SKIP_DEPS" = true ]]; then
        print_warning "Skipping dependency installation"
        return
    fi

    print_step "4" "Installing dependencies"

    case $ENVIRONMENT in
        codespaces|docker)
            # Dependencies are pre-installed in containers
            print_success "Using pre-installed container dependencies"
            ;;
        production|staging)
            print_step "4.1" "Installing system dependencies"
            apt-get update
            apt-get install -y \
                curl \
                wget \
                git \
                build-essential \
                python3.12 \
                python3-pip \
                python3-venv \
                nodejs \
                npm \
                nginx \
                postgresql \
                redis-server \
                docker \
                docker-compose

            print_step "4.2" "Installing UV"
            curl -LsSf https://astral.sh/uv/install.sh | sh
            export PATH="$HOME/.cargo/bin:$PATH"

            print_success "Production dependencies installed"
            ;;
        development)
            print_step "4.1" "Running local setup script"
            if [[ -f "setup-journal-crew.sh" ]]; then
                ./setup-journal-crew.sh
            else
                print_error "Local setup script not found"
                exit 1
            fi
            ;;
    esac
}

configure_services() {
    print_step "5" "Configuring services"

    case $ENVIRONMENT in
        codespaces)
            # Configure for Codespaces
            print_step "5.1" "Configuring Codespaces services"

            # Setup port forwarding
            echo "Configuring port forwarding for Codespaces..."
            gh codespace ports set 5173:frontend
            gh codespace ports set 6770:backend
            gh codespace ports set 6771:dashboard
            ;;
        docker)
            print_step "5.1" "Configuring Docker services"

            # Build Docker images
            docker-compose -f docker-compose.dev.yml build
            ;;
        production|staging)
            print_step "5.1" "Configuring production services"

            # Setup systemd services
            cat > /etc/systemd/system/journal-crew.service << EOF
[Unit]
Description=Journal Craft Crew Application
After=network.target

[Service]
Type=forking
User=journal-crew
Group=journal-crew
WorkingDirectory=/opt/journal-crew
ExecStart=/usr/local/bin/docker-compose -f docker-compose.prod.yml up -d
ExecStop=/usr/local/bin/docker-compose -f docker-compose.prod.yml down
TimeoutStartSec=0
Restart=always

[Install]
WantedBy=multi-user.target
EOF

            systemctl daemon-reload
            systemctl enable journal-crew
            ;;
        development)
            print_step "5.1" "Development services configuration"
            # Services are handled by start-journal-crew.sh
            ;;
    esac

    print_success "Services configured"
}

setup_database() {
    if [[ "$SKIP_DEPS" = true ]]; then
        return
    fi

    print_step "6" "Setting up database"

    case $ENVIRONMENT in
        production|staging)
            print_step "6.1" "Configuring PostgreSQL"

            # Start PostgreSQL
            systemctl enable postgresql
            systemctl start postgresql

            # Create database and user
            sudo -u postgres createuser journal_user || true
            sudo -u postgres createdb journal_platform || true
            sudo -u postgres psql -c "ALTER USER journal_user PASSWORD 'secure_password';" || true

            print_step "6.2" "Configuring Redis"
            systemctl enable redis-server
            systemctl start redis-server
            ;;
        development)
            # Database is handled by local setup
            print_success "Database handled by local setup"
            ;;
        codespaces|docker)
            print_success "Database handled by container services"
            ;;
    esac

    print_success "Database setup complete"
}

generate_ssl_certificates() {
    print_step "7" "Setting up SSL certificates"

    case $ENVIRONMENT in
        production|staging)
            print_step "7.1" "Checking for existing SSL certificates"

            # Use Let's Encrypt for production
            if [[ "$ENVIRONMENT" = "production" ]] && command -v certbot &> /dev/null; then
                DOMAIN=$(hostname -f)
                if [[ -n "$DOMAIN" && "$DOMAIN" != "localhost" ]]; then
                    certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos --email admin@"$DOMAIN" || true
                fi
            else
                print_warning "Let's Encrypt not available, using self-signed certificates"
                mkdir -p /opt/journal-crew/ssl
                openssl req -x509 -newkey rsa:4096 -keyout /opt/journal-crew/ssl/journal_crew.key -out /opt/journal-crew/ssl/journal_crew.crt -days 365 -nodes -subj "/C=US/ST=California/L=San Francisco/O=Journal Craft Crew/OU=$ENVIRONMENT/CN=localhost"
            fi
            ;;
        development|codespaces|docker)
            # Development SSL is handled by local setup
            print_success "SSL handled by development setup"
            ;;
    esac

    print_success "SSL certificates configured"
}

run_tests() {
    if [[ "$SKIP_TESTS" = true ]]; then
        print_warning "Skipping tests"
        return
    fi

    print_step "8" "Running tests"

    case $ENVIRONMENT in
        codespaces|docker)
            print_step "8.1" "Running container tests"
            npm test
            pytest
            ;;
        production|staging)
            print_step "8.1" "Running production smoke tests"
            curl -f "http://localhost:$BACKEND_PORT/health" || print_error "Backend health check failed"
            curl -f "http://localhost:$FRONTEND_PORT" || print_error "Frontend health check failed"
            ;;
        development)
            print_step "8.1" "Running development tests"
            if [[ -f "start-journal-crew.sh" ]]; then
                ./start-journal-crew.sh --test
            fi
            ;;
    esac

    print_success "Tests completed"
}

setup_monitoring() {
    if [[ "$ENABLE_MONITORING" != true ]]; then
        return
    fi

    print_step "9" "Setting up monitoring"

    case $ENVIRONMENT in
        production|staging)
            print_step "9.1" "Configuring monitoring services"

            # Setup Prometheus and Grafana
            docker-compose -f docker-compose.prod.yml --profile monitoring up -d

            # Configure log rotation
            cat > /etc/logrotate.d/journal-crew << EOF
/opt/journal-crew/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 journal-crew journal-crew
    postrotate
        docker kill -s USR1 journal-crew-backend-1
    endscript
}
EOF
            ;;
        *)
            print_warning "Monitoring not available for $ENVIRONMENT environment"
            ;;
    esac

    print_success "Monitoring setup complete"
}

setup_backups() {
    if [[ "$ENABLE_BACKUP" != true ]]; then
        return
    fi

    print_step "10" "Setting up backup services"

    case $ENVIRONMENT in
        production|staging)
            print_step "10.1" "Configuring backup services"

            # Enable backup service in docker-compose
            docker-compose -f docker-compose.prod.yml --profile backup up -d

            # Setup backup script
            cat > /opt/journal-crew/scripts/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups"

# Create backup directory
mkdir -p $BACKUP_DIR

# Database backup
docker exec journal-crew-postgres pg_dump -U journal_user journal_platform > $BACKUP_DIR/db_$DATE.sql

# Files backup
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz /opt/journal-crew/uploads/

# Clean old backups (keep 7 days)
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
EOF

            chmod +x /opt/journal-crew/scripts/backup.sh

            # Add to crontab
            (crontab -l 2>/dev/null; echo "0 2 * * * /opt/journal-crew/scripts/backup.sh") | crontab -
            ;;
        *)
            print_warning "Backup services not available for $ENVIRONMENT environment"
            ;;
    esac

    print_success "Backup setup complete"
}

start_services() {
    print_step "11" "Starting services"

    case $ENVIRONMENT in
        codespaces|docker)
            print_step "11.1" "Starting container services"
            docker-compose -f docker-compose.dev.yml up -d
            ;;
        production|staging)
            print_step "11.1" "Starting production services"
            systemctl start journal-crew
            ;;
        development)
            print_step "11.1" "Starting development services"
            if [[ -f "start-journal-crew.sh" ]]; then
                ./start-journal-crew.sh
            fi
            ;;
    esac

    print_success "Services started"
}

show_access_information() {
    print_step "12" "Displaying access information"

    echo
    echo -e "${CYAN}🌐 Access Information:${NC}"
    echo

    case $ENVIRONMENT in
        codespaces)
            echo -e "${BLUE}Frontend:${NC}   https://$CODESPACE_NAME-5173.github.dev"
            echo -e "${BLUE}Backend:${NC}    https://$CODESPACE_NAME-6770.github.dev"
            echo -e "${BLUE}Dashboard:${NC}  https://$CODESPACE_NAME-6771.github.dev"
            ;;
        production)
            echo -e "${BLUE}Frontend:${NC}   https://$(hostname -f)"
            echo -e "${BLUE}Backend:${NC}    https://$(hostname -f)/api"
            echo -e "${BLUE}Dashboard:${NC}  https://$(hostname -f)/admin"
            ;;
        staging)
            echo -e "${BLUE}Frontend:${NC}   https://staging.$(hostname -f)"
            echo -e "${BLUE}Backend:${NC}    https://staging.$(hostname -f)/api"
            echo -e "${BLUE}Dashboard:${NC}  https://staging.$(hostname -f)/admin"
            ;;
        docker)
            echo -e "${BLUE}Frontend:${NC}   http://localhost:$FRONTEND_PORT"
            echo -e "${BLUE}Backend:${NC}    http://localhost:$BACKEND_PORT"
            echo -e "${BLUE}Dashboard:${NC}  http://localhost:$DASHBOARD_PORT"
            ;;
        development)
            echo -e "${BLUE}Frontend:${NC}   http://localhost:$FRONTEND_PORT"
            echo -e "${BLUE}Backend:${NC}    http://localhost:$BACKEND_PORT"
            echo -e "${BLUE}Dashboard:${NC}  http://localhost:$DASHBOARD_PORT"
            ;;
    esac

    if [[ "$ENABLE_MONITORING" = true ]]; then
        echo -e "${BLUE}Grafana:${NC}    http://localhost:3000"
        echo -e "${BLUE}Prometheus:${NC} http://localhost:9090"
    fi

    echo
    echo -e "${CYAN}📋 Next Steps:${NC}"
    echo -e "1. Configure your OPENAI_API_KEY in the environment"
    echo -e "2. Access the application using the URLs above"
    echo -e "3. Review the deployment documentation at DEPLOYMENT.md"
    echo
}

main() {
    print_header

    # Parse command line arguments
    parse_arguments "$@"

    # Detect environment if not specified
    if [[ "$ENVIRONMENT" = "development" && $# -eq 0 ]]; then
        detect_environment
    fi

    print_success "Setting up Journal Craft Crew for: $ENVIRONMENT"

    validate_environment
    setup_environment_variables
    install_dependencies
    configure_services
    setup_database
    generate_ssl_certificates
    run_tests
    setup_monitoring
    setup_backups
    start_services
    show_access_information

    print_success "🎉 Platform setup completed successfully!"
}

# Run main function with all arguments
main "$@"