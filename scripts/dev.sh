#!/bin/bash

# Development setup script for A11yomatic

echo "🚀 Starting A11yomatic Development Environment"
echo "=============================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please update .env with your API keys before running the application"
    echo "   Especially set your GROQ_API_KEY or OPENAI_API_KEY"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads
mkdir -p backend/app
mkdir -p frontend/src

# Start Docker containers
echo "🐳 Starting Docker containers..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check service health
echo "🏥 Checking service health..."
echo ""
echo "Backend API: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "Database: localhost:5432"
echo "Redis: localhost:6379"
echo "Flower (Celery Monitor): http://localhost:5555"
echo ""

# Show logs
echo "📋 Showing logs (press Ctrl+C to exit)..."
echo "   You can also run 'docker-compose logs -f' to see logs"
echo ""
docker-compose logs -f --tail=100
