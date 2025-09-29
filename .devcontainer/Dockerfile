# Use the official Microsoft devcontainer base image with Node.js and Python
FROM mcr.microsoft.com/devcontainers/python:1-3.11-bullseye

# Install Node.js 18.x
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Install additional tools and dependencies
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
        # Basic development tools
        git \
        curl \
        wget \
        unzip \
        vim \
        nano \
        htop \
        tree \
        jq \
        # Build tools
        build-essential \
        # For Python packages that need compilation
        python3-dev \
        # For image processing (if needed by AI services)
        libgl1-mesa-glx \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender-dev \
        libgomp1 \
        # Network tools
        netcat \
        telnet \
        # Database clients (if needed)
        postgresql-client \
        # Clean up
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

# Install global Node.js tools
RUN npm install -g \
    npm@latest \
    yarn \
    pnpm \
    @vscode/vsce \
    firebase-tools \
    nodemon \
    concurrently \
    pm2

# Install global Python tools
RUN python -m pip install --upgrade pip \
    && pip install \
        # Development tools
        black \
        flake8 \
        pylint \
        autopep8 \
        mypy \
        pytest \
        pytest-cov \
        # FastAPI and related tools
        fastapi \
        uvicorn \
        # Google Cloud tools
        google-cloud-storage \
        google-cloud-pubsub \
        google-cloud-firestore \
        firebase-admin \
        # AI/ML libraries (commonly used)
        requests \
        pandas \
        numpy

# Install Docker Compose
RUN curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose \
    && chmod +x /usr/local/bin/docker-compose

# Set up the workspace
WORKDIR /workspace

# Create a non-root user
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Configure git safe directory
RUN git config --global --add safe.directory /workspace

# Switch to the vscode user
USER $USERNAME

# Set up shell aliases and environment
RUN echo 'alias ll="ls -alF"' >> ~/.bashrc \
    && echo 'alias la="ls -A"' >> ~/.bashrc \
    && echo 'alias l="ls -CF"' >> ~/.bashrc \
    && echo 'alias ..="cd .."' >> ~/.bashrc \
    && echo 'alias dc="docker-compose"' >> ~/.bashrc \
    && echo 'alias dcup="docker-compose up -d"' >> ~/.bashrc \
    && echo 'alias dcdown="docker-compose down"' >> ~/.bashrc \
    && echo 'alias dclogs="docker-compose logs -f"' >> ~/.bashrc \
    && echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc

# Set default shell to bash
ENV SHELL=/bin/bash