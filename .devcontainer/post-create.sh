#!/bin/bash

# Post-create script for AI Analyst for Startups devcontainer
echo "🚀 Setting up AI Analyst for Startups development environment..."

# Make sure we're in the workspace directory
cd /workspace

# Install root dependencies
echo "📦 Installing root dependencies..."
if [ -f "package.json" ]; then
    npm install
fi

# Install web/frontend dependencies
echo "🌐 Installing frontend dependencies..."
if [ -f "web/package.json" ]; then
    cd web
    npm install
    cd ..
fi

# Install Node.js service dependencies
echo "⚙️ Installing Node.js service dependencies..."
for service in api-gateway user-service reporting-service data-curation-service; do
    if [ -f "services/$service/package.json" ]; then
        echo "Installing dependencies for $service..."
        cd "services/$service"
        npm install
        cd ../..
    fi
done

# Install Python service dependencies
echo "🐍 Installing Python service dependencies..."
for service in ingestion-service analysis-service enhanced-ingestion-service preprocessing-worker; do
    if [ -f "services/$service/requirements.txt" ]; then
        echo "Installing dependencies for $service..."
        cd "services/$service"
        pip install -r requirements.txt
        cd ../..
    fi
done

# Set up pre-commit hooks (if .pre-commit-config.yaml exists)
if [ -f ".pre-commit-config.yaml" ]; then
    echo "🔧 Setting up pre-commit hooks..."
    pip install pre-commit
    pre-commit install
fi

# Create useful development directories
mkdir -p .vscode/launch.json
mkdir -p logs
mkdir -p tmp

# Set up Git configuration
echo "🔧 Configuring Git..."
git config --global init.defaultBranch main
git config --global pull.rebase false

# Create a helpful development script
cat > dev.sh << 'EOF'
#!/bin/bash
# Development helper script

case "$1" in
    "start")
        echo "🚀 Starting all services..."
        docker-compose up -d
        ;;
    "stop")
        echo "⏹️ Stopping all services..."
        docker-compose down
        ;;
    "logs")
        echo "📋 Showing logs for all services..."
        docker-compose logs -f
        ;;
    "frontend")
        echo "🌐 Starting frontend development server..."
        cd web && npm run dev
        ;;
    "build")
        echo "🔨 Building all services..."
        docker-compose build
        ;;
    "clean")
        echo "🧹 Cleaning up Docker resources..."
        docker-compose down -v
        docker system prune -f
        ;;
    "test")
        echo "🧪 Running tests..."
        cd web && npm test
        # Add Python tests when available
        ;;
    *)
        echo "Available commands:"
        echo "  start    - Start all services with Docker Compose"
        echo "  stop     - Stop all services"
        echo "  logs     - Show logs from all services"
        echo "  frontend - Start frontend development server"
        echo "  build    - Build all Docker images"
        echo "  clean    - Clean up Docker resources"
        echo "  test     - Run tests"
        ;;
esac
EOF

chmod +x dev.sh

echo "✅ Development environment setup complete!"
echo ""
echo "🎯 Quick start commands:"
echo "  ./dev.sh start    - Start all services"
echo "  ./dev.sh frontend - Start frontend dev server"
echo "  ./dev.sh logs     - View service logs"
echo ""
echo "📚 Available services:"
echo "  Frontend:         http://localhost:5173"
echo "  API Gateway:      http://localhost:3000"
echo "  User Service:     http://localhost:3001"
echo "  Reporting:        http://localhost:3002"
echo "  Ingestion API:    http://localhost:8000"
echo "  Analysis API:     http://localhost:8001"