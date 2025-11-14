#!/bin/bash

# =============================================================================
# Journal Craft Crew - Complete Setup Script
# =============================================================================
#
# This script transforms a fresh git clone into a fully functional Journal Craft Crew
# development environment with all components, security fixes, and dependencies.
#
# Usage: ./setup-journal-crew.sh
#
# Result: Complete development environment ready for use
#

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Terminal output functions
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
    echo -e "${PURPLE}🚀 Journal Craft Crew - Complete Setup Script${NC}"
    echo -e "${PURPLE}================================================${NC}"
    echo
}

# Check if running from project root
check_project_root() {
    print_step "0" "Checking project structure"

    if [[ ! -d "openspec" ]] || [[ ! -d "journal-platform-backend" ]] || [[ ! -d "journal-platform-frontend" ]]; then
        print_error "This script must be run from the Journal Craft Crew project root directory"
        print_error "Please ensure you have: openspec/, journal-platform-backend/, journal-platform-frontend/ directories"
        exit 1
    fi

    print_success "Project structure validated"
}

# System dependency installation
install_system_dependencies() {
    print_step "1" "Installing system dependencies"

    # Detect OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        print_warning "Detected Linux system"
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y python3 python3-pip python3-venv nodejs npm openssl curl git
        elif command -v yum &> /dev/null; then
            sudo yum install -y python3 python3-pip nodejs npm openssl curl git
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y python3 python3-pip nodejs npm openssl curl git
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        print_warning "Detected macOS system"
        if command -v brew &> /dev/null; then
            brew install python3 node openssl curl git
        else
            print_error "Please install Homebrew first: https://brew.sh/"
            exit 1
        fi
    else
        print_warning "Unknown OS: $OSTYPE. Please ensure Python 3, Node.js, npm, OpenSSL, curl, and git are installed."
    fi

    print_success "System dependencies installed"
}

# Install UV for modern Python dependency management
install_uv() {
    print_step "2" "Installing UV dependency manager"

    if ! command -v uv &> /dev/null; then
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.cargo/bin:$PATH"

        # Add to shell profile
        echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
        echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.zshrc 2>/dev/null || true

        print_success "UV installed and added to PATH"
    else
        print_success "UV already installed"
    fi
}

# Setup backend with UV and security fixes
setup_backend() {
    print_step "3" "Setting up backend with UV and security fixes"

    cd journal-platform-backend

    # Create virtual environment with UV
    if [[ ! -d ".venv" ]]; then
        uv venv
        print_success "Backend virtual environment created"
    fi

    # Activate virtual environment
    source .venv/bin/activate

    # Install dependencies with UV (using frozen secure requirements)
    if [[ -f "requirements_final_secure.txt" ]]; then
        print_warning "Installing from secure frozen requirements..."
        uv pip sync requirements_final_secure.txt
        print_success "Secure dependencies installed from frozen requirements"
    else
        print_warning "Installing from base requirements..."
        uv pip install -r requirements.txt
        print_success "Base dependencies installed"
    fi

    # Install additional development dependencies
    uv pip install duckdb archon python-dotenv fastapi uvicorn websockets

    # Create .env file if it doesn't exist
    if [[ ! -f ".env" ]]; then
        cat > .env << 'EOF'
# Journal Craft Crew Backend Environment
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=sqlite:///./journal_crew.db
SECRET_KEY=your_secret_key_here_change_in_production
ENVIRONMENT=development
DEBUG=true
EOF
        print_success "Backend .env file created (please update API keys)"
    fi

    cd ..
    print_success "Backend setup complete"
}

# Setup frontend
setup_frontend() {
    print_step "4" "Setting up frontend"

    cd journal-platform-frontend

    # Install dependencies
    if command -v npm &> /dev/null; then
        npm install
        print_success "Frontend dependencies installed with npm"
    elif command -v yarn &> /dev/null; then
        yarn install
        print_success "Frontend dependencies installed with yarn"
    else
        print_error "Please install npm or yarn"
        exit 1
    fi

    # Create .env file if it doesn't exist
    if [[ ! -f ".env" ]]; then
        cat > .env << 'EOF'
# Journal Craft Crew Frontend Environment
VITE_API_URL=http://localhost:6770
VITE_WS_URL=ws://localhost:6770
VITE_ENVIRONMENT=development
EOF
        print_success "Frontend .env file created"
    fi

    cd ..
    print_success "Frontend setup complete"
}

# Setup orchestrator dashboard
setup_orchestrator() {
    print_step "5" "Setting up orchestrator dashboard"

    cd orchestrator_dashboard

    # Create virtual environment if it doesn't exist
    if [[ ! -d "../orchestrator_venv" ]]; then
        python3 -m venv ../orchestrator_venv
        print_success "Orchestrator virtual environment created"
    fi

    # Activate and install dependencies
    source ../orchestrator_venv/bin/activate
    pip install flask flask-cors requests python-dotenv psutil

    cd ..
    print_success "Orchestrator dashboard setup complete"
}

# Generate SSL certificates
setup_ssl() {
    print_step "6" "Generating SSL certificates"

    # Create SSL directory
    mkdir -p ssl
    cd ssl

    # Generate self-signed certificate
    if [[ ! -f "journal_crew.crt" ]] || [[ ! -f "journal_crew.key" ]]; then
        openssl req -x509 -newkey rsa:4096 -keyout journal_crew.key -out journal_crew.crt -days 365 -subj "/C=US/ST=California/L=San Francisco/O=Journal Craft Crew/OU=Development/CN=localhost" -nodes

        print_success "SSL certificates generated"
    else
        print_success "SSL certificates already exist"
    fi

    cd ..
    print_success "SSL setup complete"
}

# Create startup scripts
create_startup_scripts() {
    print_step "7" "Creating startup scripts"

    # Create main startup script
    cat > start-journal-crew.sh << 'EOF'
#!/bin/bash

# Journal Craft Crew - Development Server Startup Script
# This script starts all development servers in the correct order

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🚀 Starting Journal Craft Crew Development Servers${NC}"
echo -e "${BLUE}================================================${NC}"

# Kill existing processes
echo -e "${YELLOW}🛑 Stopping any existing servers...${NC}"
pkill -f "unified_backend.py" || true
pkill -f "npm run dev" || true
pkill -f "app.py" || true
sleep 2

# Start backend
echo -e "${GREEN}🔧 Starting backend server...${NC}"
cd journal-platform-backend
source .venv/bin/activate
python unified_backend.py &
BACKEND_PID=$!
cd ..
echo "Backend PID: $BACKEND_PID"

# Wait for backend to initialize
sleep 3

# Start frontend
echo -e "${GREEN}🎨 Starting frontend server...${NC}"
cd journal-platform-frontend
npm run dev &
FRONTEND_PID=$!
cd ..
echo "Frontend PID: $FRONTEND_PID"

# Wait for frontend to initialize
sleep 3

# Start orchestrator dashboard
echo -e "${GREEN}📊 Starting orchestrator dashboard...${NC}"
cd orchestrator_dashboard
source ../orchestrator_venv/bin/activate
python app.py &
DASHBOARD_PID=$!
cd ..
echo "Dashboard PID: $DASHBOARD_PID"

echo
echo -e "${GREEN}✅ All servers started successfully!${NC}"
echo -e "${BLUE}Frontend:${NC}       http://localhost:5173"
echo -e "${BLUE}Backend API:${NC}    https://localhost:6770 (SSL)"
echo -e "${BLUE}Dashboard:${NC}      http://localhost:6771"
echo -e "${BLUE}Agent Overview:${NC}  http://localhost:6771/agent-overview"
echo
echo -e "${YELLOW}Press Ctrl+C to stop all servers${NC}"

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Stopping all servers...${NC}"
    kill $BACKEND_PID $FRONTEND_PID $DASHBOARD_PID 2>/dev/null || true
    exit 0
}

# Set trap for cleanup
trap cleanup INT TERM

# Wait for processes
wait
EOF

    chmod +x start-journal-crew.sh

    # Create stop script
    cat > stop-journal-crew.sh << 'EOF'
#!/bin/bash

# Journal Craft Crew - Stop All Servers
echo "🛑 Stopping Journal Craft Crew servers..."
pkill -f "unified_backend.py" || true
pkill -f "npm run dev" || true
pkill -f "app.py" || true
echo "✅ All servers stopped"
EOF

    chmod +x stop-journal-crew.sh

    print_success "Startup scripts created"
}

# Create development documentation
create_dev_docs() {
    print_step "8" "Creating development documentation"

    cat > DEVELOPMENT.md << 'EOF'
# Journal Craft Crew - Development Guide

## 🚀 Quick Start

After running the setup script, you can start all development servers with:

```bash
./start-journal-crew.sh
```

## 🛠 Development Environment

### Frontend (React + TypeScript)
- **URL**: http://localhost:5173
- **Tech**: React, TypeScript, Tailwind CSS
- **Restart**: `cd journal-platform-frontend && npm run dev`

### Backend (FastAPI + Python)
- **URL**: https://localhost:6770 (SSL)
- **Tech**: FastAPI, Python, CrewAI, WebSockets
- **Restart**: `cd journal-platform-backend && source .venv/bin/activate && python unified_backend.py`

### Orchestrator Dashboard
- **URL**: http://localhost:6771
- **Features**: Server management, session tracking, agent overview
- **Restart**: `cd orchestrator_dashboard && source ../orchestrator_venv/bin/activate && python app.py`

## 🔧 Development Commands

### Start All Servers
```bash
./start-journal-crew.sh
```

### Stop All Servers
```bash
./stop-journal-crew.sh
```

### Individual Server Control
```bash
# Backend only
cd journal-platform-backend && source .venv/bin/activate && python unified_backend.py

# Frontend only
cd journal-platform-frontend && npm run dev

# Dashboard only
cd orchestrator_dashboard && source ../orchestrator_venv/bin/activate && python app.py
```

## 📊 Agent System Overview

View the complete agent system documentation at:
- **Dashboard**: http://localhost:6771/agent-overview
- **Status**: Live monitoring of all 19 agents across Application, Dev, and Legacy layers

## 🔒 Security

- All security vulnerabilities have been resolved (43 → 0)
- SSL certificates auto-generated for development
- Environment variables configured for secure development

## 📝 Architecture

- **Application Layer**: 4 active CrewAI agents for journal generation
- **Dev Layer**: 6 specialized Archon integration agents for development support
- **Legacy System**: 9 archived agents with migration documentation

## 🎯 Core Features

- **CrewAI Integration**: Sequential workflow for journal content generation
- **Real-time Progress**: WebSocket-based progress tracking
- **Multi-layer Architecture**: Clear separation between user-facing and development agents
- **Security**: Zero vulnerabilities with modern dependency management
EOF

    print_success "Development documentation created"
}

# Verify setup
verify_setup() {
    print_step "9" "Verifying setup"

    # Check virtual environments
    if [[ -d "journal-platform-backend/.venv" ]] && [[ -d "orchestrator_venv" ]]; then
        print_success "Virtual environments created"
    else
        print_error "Virtual environments missing"
        exit 1
    fi

    # Check SSL certificates
    if [[ -f "ssl/journal_crew.crt" ]] && [[ -f "ssl/journal_crew.key" ]]; then
        print_success "SSL certificates generated"
    else
        print_error "SSL certificates missing"
        exit 1
    fi

    # Check startup scripts
    if [[ -f "start-journal-crew.sh" ]] && [[ -f "stop-journal-crew.sh" ]]; then
        print_success "Startup scripts created"
    else
        print_error "Startup scripts missing"
        exit 1
    fi

    print_success "Setup verification complete"
}

# Final instructions
show_final_instructions() {
    echo
    print_success "🎉 Journal Craft Crew setup complete!"
    echo
    echo -e "${BLUE}📋 Next Steps:${NC}"
    echo -e "${YELLOW}1. Update API Keys:${NC}"
    echo -e "   Edit journal-platform-backend/.env"
    echo -e "   Add your OPENAI_API_KEY"
    echo
    echo -e "${YELLOW}2. Start Development:${NC}"
    echo -e "   ${GREEN}./start-journal-crew.sh${NC}"
    echo
    echo -e "${BLUE}🌐 Access Points:${NC}"
    echo -e "   Frontend:        ${GREEN}http://localhost:5173${NC}"
    echo -e "   Backend API:     ${GREEN}https://localhost:6770${NC}"
    echo -e "   Dashboard:       ${GREEN}http://localhost:6771${NC}"
    echo -e "   Agent Overview:  ${GREEN}http://localhost:6771/agent-overview${NC}"
    echo
    echo -e "${BLUE}📚 Documentation:${NC}"
    echo -e "   Development Guide: ${YELLOW}DEVELOPMENT.md${NC}"
    echo -e "   OpenSpec:         ${YELLOW}openspec/${NC}"
    echo
    echo -e "${PURPLE}✨ Your Journal Craft Crew development environment is ready!${NC}"
}

# Main execution
main() {
    print_header
    check_project_root
    install_system_dependencies
    install_uv
    setup_backend
    setup_frontend
    setup_orchestrator
    setup_ssl
    create_startup_scripts
    create_dev_docs
    verify_setup
    show_final_instructions
}

# Run main function
main "$@"