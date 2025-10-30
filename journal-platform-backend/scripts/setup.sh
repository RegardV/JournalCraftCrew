#!/bin/bash

# Journal Platform Backend Development Setup Script
# Phase 3.1: Database Integration with PostgreSQL

set -e

echo "🚀 Setting up Journal Platform Backend Development Environment..."

# Check if Python 3.11+ is installed
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    echo "✅ Python $python_version detected"
else
    echo "❌ Python 3.11+ is required. Found: $python_version"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads
mkdir -p logs
mkdir -p scripts

# Copy environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please update .env with your configuration"
fi

# Check Docker and Docker Compose
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    echo "🐳 Docker and Docker Compose found"

    # Ask if user wants to start development containers
    read -p "Would you like to start PostgreSQL and Redis containers? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🚀 Starting development containers..."
        docker-compose up -d postgres redis

        echo "⏳ Waiting for databases to be ready..."
        sleep 10

        echo "🗄️ Running database migrations..."
        python -m app.core.migrations migrate

        echo "✅ Development environment is ready!"
        echo ""
        echo "🌐 Available services:"
        echo "   - API: http://localhost:8000"
        echo "   - API Docs: http://localhost:8000/docs"
        echo "   - PostgreSQL: localhost:5432"
        echo "   - Redis: localhost:6379"
        echo "   - Adminer: http://localhost:8080"
        echo ""
        echo "🚀 To start the API server:"
        echo "   source venv/bin/activate"
        echo "   python main.py"
    else
        echo "⚠️  Skipping Docker containers. Make sure to set up your own databases."
    fi
else
    echo "⚠️  Docker not found. Please install Docker and Docker Compose for full development setup."
    echo "   Alternatively, set up PostgreSQL and Redis manually and update .env accordingly."
fi

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Update .env with your configuration"
echo "2. Activate virtual environment: source venv/bin/activate"
echo "3. Start the development server: python main.py"
echo "4. Visit http://localhost:8000/docs for API documentation"