# AI Analyst for Startups - Development Container

This directory contains the development container configuration for the AI Analyst for Startups project.

## 🚀 Quick Start

1. **Open in VS Code**: Open this project in VS Code
2. **Reopen in Container**: When prompted, click "Reopen in Container" or use `Ctrl+Shift+P` → "Dev Containers: Reopen in Container"
3. **Wait for Setup**: The initial setup will install all dependencies automatically
4. **Start Development**: Use the provided helper scripts or VS Code tasks

## 📁 Files Overview

- `devcontainer.json` - Main configuration file
- `Dockerfile` - Custom container image with all required tools
- `docker-compose.devcontainer.yml` - Docker Compose override for development
- `post-create.sh` - Runs after container creation (installs dependencies)
- `post-start.sh` - Runs every time the container starts

## 🛠️ What's Included

### Languages & Runtimes
- **Node.js 18.x** with npm, yarn, pnpm
- **Python 3.11** with pip and common packages
- **TypeScript** support

### Development Tools
- **VS Code Extensions**: Pre-installed extensions for Python, TypeScript, React, Docker, etc.
- **Linting & Formatting**: ESLint, Prettier, Black, Flake8, Pylint
- **Docker Tools**: Docker CLI, Docker Compose
- **Git Tools**: Git, GitHub CLI
- **Debugging**: Configured launch configurations for all services

### Project-Specific Tools
- **Firebase Tools**: For Firebase integration
- **Google Cloud Libraries**: For GCS and Pub/Sub
- **FastAPI & Uvicorn**: For Python services
- **React Dev Tools**: Vite, testing libraries

## 🚀 Development Commands

The setup creates a `dev.sh` script with helpful commands:

```bash
# Start all services with Docker Compose
./dev.sh start

# Stop all services
./dev.sh stop

# View logs from all services
./dev.sh logs

# Start frontend development server only
./dev.sh frontend

# Build all Docker images
./dev.sh build

# Clean up Docker resources
./dev.sh clean

# Run tests
./dev.sh test
```

## 🌐 Available Services & Ports

Once started, you can access:

- **Frontend (React)**: http://localhost:5173
- **API Gateway**: http://localhost:3000
- **User Service**: http://localhost:3001
- **Reporting Service**: http://localhost:3002
- **Ingestion Service**: http://localhost:8000
- **Analysis Service**: http://localhost:8001

## 🔧 VS Code Features

### Multi-Root Workspace
- Organized workspace with folders for each service
- Service-specific settings and configurations

### Debugging
- Pre-configured launch configurations for all services
- Support for both Node.js and Python debugging
- Docker container debugging support

### API Testing
- `.vscode/api-tests.http` file for testing endpoints
- Uses REST Client extension

### Extensions Installed
- Python development (Pylance, Black, Flake8)
- TypeScript/JavaScript development
- React development tools
- Docker integration
- Git integration (GitLens)
- API testing (REST Client)
- Database tools

## 🐳 Docker Integration

The devcontainer is designed to work alongside your existing Docker Compose setup:
- Uses Docker-outside-of-Docker for container management
- Shares network with application services
- Volume mounting for efficient development

## 📦 Dependencies Management

Dependencies are automatically installed during container setup:
- **Root**: npm packages from main package.json
- **Frontend**: React/Vite dependencies from web/package.json
- **Node.js Services**: Each service's npm dependencies
- **Python Services**: Each service's requirements.txt

## 🔧 Customization

### Adding New Extensions
Edit `.devcontainer/devcontainer.json` and add to the `extensions` array.

### Adding New Tools
Edit `.devcontainer/Dockerfile` to install additional tools.

### Changing Ports
Update `forwardPorts` in `devcontainer.json` and corresponding service configurations.

### Environment Variables
Add to the `environment` section in `docker-compose.devcontainer.yml`.

## 🐛 Troubleshooting

### Container Won't Start
1. Check Docker is running
2. Try rebuilding: `Ctrl+Shift+P` → "Dev Containers: Rebuild Container"
3. Check Docker Desktop has sufficient resources allocated

### Port Conflicts
1. Stop other services using the same ports
2. Update port mappings in `devcontainer.json` if needed

### Permission Issues
1. The container runs as the `vscode` user
2. File permissions should be handled automatically

### Large Project Size
The devcontainer is configured for projects up to 32GB with optimizations:
- Named volumes for node_modules (faster installs)
- Efficient caching strategies
- Docker layer optimization

## 📚 Learn More

- [VS Code Dev Containers Documentation](https://code.visualstudio.com/docs/devcontainers/containers)
- [Dev Container Feature Reference](https://containers.dev/features)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

## 🤝 Contributing

When adding new services or dependencies:
1. Update the relevant package.json or requirements.txt
2. Update `post-create.sh` to install the new dependencies
3. Add appropriate VS Code settings/extensions if needed
4. Update port forwarding if the service exposes new ports