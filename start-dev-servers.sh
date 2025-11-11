#!/bin/bash
# Journal Craft Crew Development Server Startup Script
# This script starts the backend and frontend servers in the correct order

echo "🚀 Starting Journal Craft Crew Development Servers..."
echo "================================================"

# Function to check if a port is in use
check_port() {
    if lsof -i :$1 >/dev/null 2>&1; then
        echo "⚠️  Port $1 is already in use"
        return 1
    fi
    return 0
}

# Function to wait for server to start
wait_for_server() {
    local port=$1
    local name=$2
    local max_attempts=30
    local attempt=1

    echo "⏳ Waiting for $name to start on port $port..."

    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:$port/health >/dev/null 2>&1 || curl -s http://localhost:$port >/dev/null 2>&1; then
            echo "✅ $name is ready!"
            return 0
        fi
        sleep 1
        attempt=$((attempt + 1))
    done

    echo "❌ $name failed to start within $max_attempts seconds"
    return 1
}

# Check if required ports are available
echo "🔍 Checking port availability..."
if ! check_port 6770; then
    echo "❌ Backend port 6770 is not available. Please stop the existing process."
    exit 1
fi

if ! check_port 5173; then
    echo "⚠️  Frontend port 5173 is in use. This might be okay if it's our dev server."
fi

# Start Backend Server
echo ""
echo "🔧 Starting Backend Server..."
cd "$(dirname "$0")/journal-platform-backend"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please run: python -m venv .venv"
    exit 1
fi

# Activate virtual environment and start backend
source .venv/bin/activate
echo "📦 Starting backend on port 6770..."
python unified_backend.py &
BACKEND_PID=$!

# Wait for backend to start
if wait_for_server 6770 "Backend"; then
    echo "✅ Backend server started successfully (PID: $BACKEND_PID)"
    echo "📍 Backend URL: http://localhost:6770"
    echo "📍 Health Check: http://localhost:6770/health"
else
    echo "❌ Failed to start backend server"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Start Frontend Server
echo ""
echo "🎨 Starting Frontend Server..."
cd "../journal-platform-frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

echo "📦 Starting frontend on port 5173..."
npm run dev &
FRONTEND_PID=$!

# Wait a moment for frontend to start
sleep 3

echo ""
echo "🎉 Development servers are ready!"
echo "=================================="
echo "📍 Frontend: http://localhost:5173"
echo "📍 Backend:  http://localhost:6770"
echo "📍 Health:   http://localhost:6770/health"
echo ""
echo "💡 To stop servers:"
echo "   kill $BACKEND_PID  # Stop backend"
echo "   kill $FRONTEND_PID  # Stop frontend"
echo ""
echo "💡 Or use: pkill -f 'python unified_backend.py' && pkill -f 'npm run dev'"
echo ""
echo "🔧 Password Requirements (Updated):"
echo "   • Minimum 6 characters"
echo "   • At least 2 of: lowercase, uppercase, numbers, special characters"
echo "   • Cannot contain common patterns like '123456' or 'password'"
echo ""

# Save PIDs to file for easy cleanup
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

echo "✅ Server PIDs saved to .backend.pid and .frontend.pid"
echo "🎯 Ready for development!"