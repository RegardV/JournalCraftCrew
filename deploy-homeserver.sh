#!/bin/bash

# =============================================================================
# Journal Craft Crew - Homeserver Deployment Script
# =============================================================================

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
PROJECT_NAME="journal-crew"
COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env.homeserver"

print_step() {
    echo -e "${BLUE}🔧 $1${NC}"
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

# Check if running as root (for Docker operations)
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_warning "Some operations may require sudo privileges"
    fi
}

# Check Docker and Docker Compose
check_docker() {
    print_step "Checking Docker Installation"

    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi

    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running. Please start Docker service."
        exit 1
    fi

    print_success "Docker and Docker Compose are available"
}

# Setup environment
setup_environment() {
    print_step "Setting Up Environment"

    # Copy homeserver environment file
    if [[ -f "$ENV_FILE" ]]; then
        cp "$ENV_FILE" .env
        print_success "Environment configuration loaded"
    else
        print_error "Environment file $ENV_FILE not found"
        exit 1
    fi

    # Create required directories
    mkdir -p uploads logs static backups
    chmod 755 uploads logs static

    # Set proper permissions for SSL
    if [[ -d "ssl" ]]; then
        chmod 600 ssl/journal_crew.key
        chmod 644 ssl/journal_crew.crt
        print_success "SSL certificate permissions set"
    fi

    print_success "Environment setup completed"
}

# Stop development servers
stop_dev_servers() {
    print_step "Stopping Development Servers"

    # Kill any running development servers
    pkill -f "npm run dev" 2>/dev/null || true
    pkill -f "python unified_backend.py" 2>/dev/null || true
    pkill -f "python app.py" 2>/dev/null || true

    # Wait a moment for processes to stop
    sleep 2

    print_success "Development servers stopped"
}

# Build and start services
deploy_services() {
    print_step "Building and Starting Services"

    # Stop existing containers
    docker-compose -f "$COMPOSE_FILE" down --remove-orphans || true

    # Build images
    print_step "Building Docker Images"
    docker-compose -f "$COMPOSE_FILE" build --no-cache

    # Start core services
    print_step "Starting Core Services"
    docker-compose -f "$COMPOSE_FILE" up -d postgres redis

    # Wait for database to be ready
    print_step "Waiting for Database to be Ready"
    timeout 60 bash -c 'until docker-compose -f '"$COMPOSE_FILE"' exec -T postgres pg_isready -U journal_user -d journal_crew; do sleep 2; done'

    # Start application services
    print_step "Starting Application Services"
    docker-compose -f "$COMPOSE_FILE" up -d backend frontend

    # Wait for backend to be healthy
    print_step "Waiting for Backend to be Ready"
    timeout 120 bash -c 'until [[ "$(curl -s -o /dev/null -w "%{http_code}" https://localhost:8000/health)" == "200" ]]; do sleep 5; done'

    # Start Nginx reverse proxy
    print_step "Starting Nginx Reverse Proxy"
    docker-compose -f "$COMPOSE_FILE" up -d nginx

    print_success "All services started successfully"
}

# Setup monitoring (optional)
setup_monitoring() {
    print_step "Setting Up Monitoring"

    read -p "Do you want to enable monitoring with Prometheus and Grafana? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose -f "$COMPOSE_FILE" --profile monitoring up -d prometheus grafana
        print_success "Monitoring services started"
        print_warning "Access Grafana at: http://localhost:3000 (admin/admin)"
        print_warning "Access Prometheus at: http://localhost:9090"
    fi
}

# Setup backup (optional)
setup_backup() {
    print_step "Setting Up Backup Service"

    read -p "Do you want to enable automated backups? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose -f "$COMPOSE_FILE" --profile backup up -d backup
        print_success "Backup service started"
        print_warning "Backups will be stored in the ./backups directory"
    fi
}

# Verify deployment
verify_deployment() {
    print_step "Verifying Deployment"

    # Check if all containers are running
    if docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
        print_success "Services are running"
    else
        print_error "Some services failed to start"
        docker-compose -f "$COMPOSE_FILE" ps
        exit 1
    fi

    # Check HTTPS accessibility
    print_step "Testing HTTPS Access"
    if curl -k -s -o /dev/null -w "%{http_code}" https://localhost/health | grep -q "200"; then
        print_success "HTTPS proxy is working"
    else
        print_warning "HTTPS proxy may not be fully ready yet"
    fi

    # Check API accessibility
    print_step "Testing API Access"
    if curl -k -s -o /dev/null -w "%{http_code}" https://localhost/api/health | grep -q "200"; then
        print_success "API is accessible"
    else
        print_warning "API may still be starting up"
    fi
}

# Show deployment info
show_info() {
    print_success "🎉 Journal Craft Crew deployment completed!"
    echo
    echo -e "${YELLOW}=== Access Information ===${NC}"
    echo -e "Frontend: ${GREEN}https://localhost${NC}"
    echo -e "API: ${GREEN}https://localhost/api${NC}"
    echo -e "Health Check: ${GREEN}https://localhost/health${NC}"
    echo
    echo -e "${YELLOW}=== Management Commands ===${NC}"
    echo -e "View logs: ${BLUE}docker-compose -f $COMPOSE_FILE logs -f${NC}"
    echo -e "Stop services: ${BLUE}docker-compose -f $COMPOSE_FILE down${NC}"
    echo -e "Restart services: ${BLUE}docker-compose -f $COMPOSE_FILE restart${NC}"
    echo -e "View status: ${BLUE}docker-compose -f $COMPOSE_FILE ps${NC}"
    echo
    echo -e "${YELLOW}=== SSL Certificate${NC}"
    echo -e "The deployment uses a self-signed certificate for localhost."
    echo -e "Your browser will show a security warning - this is expected."
    echo
    if docker-compose -f "$COMPOSE_FILE" ps | grep -q "grafana"; then
        echo -e "${YELLOW}=== Monitoring${NC}"
        echo -e "Grafana: ${GREEN}http://localhost:3000${NC} (admin/admin)"
        echo -e "Prometheus: ${GREEN}http://localhost:9090${NC}"
        echo
    fi
}

# Cleanup function
cleanup() {
    print_step "Cleanup"
    docker-compose -f "$COMPOSE_FILE" down --remove-orphans || true
    docker system prune -f || true
    print_success "Cleanup completed"
}

# Main execution
main() {
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}  Journal Craft Crew - Homeserver Deployment${NC}"
    echo -e "${BLUE}============================================${NC}"
    echo

    # Parse command line arguments
    case "${1:-deploy}" in
        "deploy")
            check_root
            check_docker
            setup_environment
            stop_dev_servers
            deploy_services
            setup_monitoring
            setup_backup
            verify_deployment
            show_info
            ;;
        "stop")
            docker-compose -f "$COMPOSE_FILE" down
            print_success "Services stopped"
            ;;
        "restart")
            docker-compose -f "$COMPOSE_FILE" restart
            print_success "Services restarted"
            ;;
        "logs")
            docker-compose -f "$COMPOSE_FILE" logs -f
            ;;
        "status")
            docker-compose -f "$COMPOSE_FILE" ps
            ;;
        "cleanup")
            cleanup
            ;;
        "help"|"-h"|"--help")
            echo "Usage: $0 {deploy|stop|restart|logs|status|cleanup|help}"
            echo "  deploy   - Deploy the application (default)"
            echo "  stop     - Stop all services"
            echo "  restart  - Restart all services"
            echo "  logs     - Show service logs"
            echo "  status   - Show service status"
            echo "  cleanup  - Clean up containers and images"
            echo "  help     - Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown command: $1"
            echo "Use '$0 help' for available commands"
            exit 1
            ;;
    esac
}

# Handle script interruption
trap 'print_error "Deployment interrupted"; exit 1' INT TERM

# Run main function with all arguments
main "$@"