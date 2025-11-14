# =============================================================================
# Journal Craft Crew - Development Dockerfile
# =============================================================================
# Optimized for GitHub Codespaces and local Docker development

FROM mcr.microsoft.com/vscode/devcontainers/python:3.12

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV NODE_ENV=development
ENV PYTHONPATH=/workspace/journal-platform-backend

# Install system dependencies
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive && \
    apt-get -y install --no-install-recommends \
        # Core utilities
        curl \
        wget \
        git \
        build-essential \
        # Python dependencies
        python3-dev \
        python3-pip \
        python3-venv \
        # Node.js dependencies
        ca-certificates \
        gnupg \
        # SSL certificates
        openssl \
        # Other tools
        jq \
        tree \
        htop \
        # Clean up
    && apt-get clean -y && \
    rm -rf /var/lib/apt/lists/*

# Install Node.js 18
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g npm@latest

# Install UV for modern Python dependency management
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Install global Python tools
RUN pip install --no-cache-dir \
    pip==latest \
    setuptools==latest \
    wheel==latest && \
    pip install --no-cache-dir \
    black \
    flake8 \
    mypy \
    pytest \
    pre-commit

# Install global Node.js tools
RUN npm install -g \
    typescript \
    ts-node \
    nodemon \
    concurrently

# Create workspace directory
WORKDIR /workspace

# Create non-root user for Codespaces
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Create development directories
RUN mkdir -p \
    /workspace/logs \
    /workspace/ssl \
    /workspace/uploads \
    /workspace/.vscode

# Set ownership
RUN chown -R $USERNAME:$USERNAME /workspace

# Switch to non-root user
USER $USERNAME

# Install Python development dependencies
RUN uv pip install --system \
    duckdb \
    python-dotenv \
    fastapi \
    uvicorn \
    websockets

# Display welcome message
RUN echo '🚀 Journal Craft Crew Development Environment Ready!' && \
    echo '📋 Available commands:' && \
    echo '  ./setup-journal-crew.sh    - Initial setup' && \
    echo '  ./start-journal-crew.sh    - Start all services' && \
    echo '  ./stop-journal-crew.sh     - Stop all services'

# Multi-stage build support
FROM development as production

# Production target would go here for future CI/CD deployment

# Default command
CMD ["sleep", "infinity"]