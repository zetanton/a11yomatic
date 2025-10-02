#!/bin/bash
# Development setup script for A11yomatic

set -e

echo "🚀 A11yomatic Development Setup"
echo "================================"

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your API keys"
    echo ""
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not available. Please ensure Docker Desktop is installed."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Create uploads directory
mkdir -p uploads
echo "✅ Created uploads directory"
echo ""

# Start services
echo "🐳 Starting Docker containers..."
docker compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service health
echo "🔍 Checking service health..."

if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is running at http://localhost:8000"
    echo "📚 API Documentation: http://localhost:8000/docs"
else
    echo "⚠️  Backend may still be starting up. Please check logs with: docker compose logs backend"
fi

if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend is running at http://localhost:3000"
else
    echo "⚠️  Frontend may still be starting up. Please check logs with: docker compose logs frontend"
fi

echo ""
echo "🎉 A11yomatic is ready!"
echo ""
echo "📖 Next steps:"
echo "   1. Configure your AI API keys in .env file"
echo "   2. Access the application at http://localhost:3000"
echo "   3. View API docs at http://localhost:8000/docs"
echo ""
echo "💡 Useful commands:"
echo "   - View logs: docker compose logs -f"
echo "   - Stop services: docker compose down"
echo "   - Restart services: docker compose restart"
echo ""


