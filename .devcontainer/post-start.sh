#!/bin/bash

# Post-start script for AI Analyst for Startups devcontainer
echo "🌟 Starting development environment..."

# Make sure we're in the workspace directory
cd /workspace

# Display system info
echo "💻 System Information:"
echo "  Node.js: $(node --version)"
echo "  npm: $(npm --version)"
echo "  Python: $(python --version)"
echo "  Docker: $(docker --version 2>/dev/null || echo 'Not available')"
echo "  Git: $(git --version)"
echo ""

# Check if services are already running
if docker-compose ps | grep -q "Up"; then
    echo "🟢 Some services are already running:"
    docker-compose ps
    echo ""
else
    echo "🔵 No services currently running. Use './dev.sh start' to start all services."
    echo ""
fi

# Show available ports
echo "🌐 Available ports:"
echo "  5173 - Frontend (React/Vite)"
echo "  3000 - API Gateway"
echo "  3001 - User Service"
echo "  3002 - Reporting Service"
echo "  8000 - Ingestion Service"
echo "  8001 - Analysis Service"
echo ""

# Check for environment files
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. You may want to create one based on .env.example"
fi

if [ ! -f "serviceAccountKey.json" ]; then
    echo "⚠️  No serviceAccountKey.json found. Firebase services may not work properly."
fi

echo "✨ Environment ready! Happy coding! 🚀"