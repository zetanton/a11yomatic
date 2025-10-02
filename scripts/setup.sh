#!/bin/bash

# A11yomatic Development Environment Setup Script

set -e

echo "🚀 Setting up A11yomatic development environment..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p backend/{app,app/api/v1,app/core,app/models,app/services,app/utils}
mkdir -p frontend/{src,src/components,src/hooks,src/services,src/store,src/utils}
mkdir -p docs tests scripts uploads
mkdir -p backend/tests frontend/tests

# Set up environment file
echo "⚙️ Setting up environment configuration..."
if [ ! -f .env ]; then
    cp env.example .env
    echo "✅ Created .env file from template"
    echo "⚠️  Please update .env with your API keys and configuration"
else
    echo "✅ .env file already exists"
fi

# Create backend structure
echo "🐍 Setting up Python backend..."
cat > backend/app/__init__.py << EOF
# A11yomatic Backend Application
EOF

cat > backend/app/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(
    title="A11yomatic API",
    description="PDF Accessibility Remediation Tool",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "A11yomatic API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}
EOF

cat > backend/app/core/config.py << 'EOF'
from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://a11yomatic:password@localhost:5432/a11yomatic"
    REDIS_URL: str = "redis://localhost:6379"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # File Upload
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    
    # AI Services
    OPENAI_API_KEY: str = ""
    OPENAI_API_BASE_URL: str = "https://api.openai.com/v1"
    GROQ_API_KEY: str = ""
    HUGGINGFACE_API_KEY: str = ""
    
    class Config:
        env_file = ".env"

settings = Settings()
EOF

# Create frontend structure
echo "⚛️ Setting up React frontend..."
cat > frontend/src/App.tsx << 'EOF'
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Provider } from 'react-redux';
import { store } from './store/store';
import './App.css';

function App() {
  return (
    <Provider store={store}>
      <Router>
        <div className="min-h-screen bg-dark-900 text-text-primary">
          <Routes>
            <Route path="/" element={<div>Welcome to A11yomatic</div>} />
          </Routes>
        </div>
      </Router>
    </Provider>
  );
}

export default App;
EOF

cat > frontend/src/App.css << 'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --primary-50: #f0f9ff;
  --primary-500: #0ea5e9;
  --primary-600: #0284c7;
  --primary-700: #0369a1;
  --primary-900: #0c4a6e;
  
  --dark-50: #f8fafc;
  --dark-100: #f1f5f9;
  --dark-200: #e2e8f0;
  --dark-300: #cbd5e1;
  --dark-400: #94a3b8;
  --dark-500: #64748b;
  --dark-600: #475569;
  --dark-700: #334155;
  --dark-800: #1e293b;
  --dark-900: #0f172a;
  
  --text-primary: #f8fafc;
  --text-secondary: #cbd5e1;
  --text-muted: #94a3b8;
}

body {
  margin: 0;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: var(--dark-900);
  color: var(--text-primary);
}
EOF

# Create Docker files
echo "🐳 Creating Docker configuration..."

# Backend Dockerfile
cat > backend/Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

# Frontend Dockerfile
cat > frontend/Dockerfile << 'EOF'
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
EOF

# Create nginx configuration
cat > frontend/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    server {
        listen 80;
        server_name localhost;
        root /usr/share/nginx/html;
        index index.html;
        
        location / {
            try_files $uri $uri/ /index.html;
        }
        
        location /api {
            proxy_pass http://backend:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
EOF

# Create development scripts
cat > scripts/dev.sh << 'EOF'
#!/bin/bash

echo "🚀 Starting A11yomatic development environment..."

# Start all services
docker-compose up -d

echo "✅ Services started!"
echo "📊 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "🌱 Flower (Celery): http://localhost:5555"
echo "🗄️ Database: localhost:5432"
echo "🔄 Redis: localhost:6379"
EOF

chmod +x scripts/dev.sh

cat > scripts/stop.sh << 'EOF'
#!/bin/bash

echo "🛑 Stopping A11yomatic development environment..."

docker-compose down

echo "✅ All services stopped!"
EOF

chmod +x scripts/stop.sh

cat > scripts/logs.sh << 'EOF'
#!/bin/bash

echo "📋 Showing A11yomatic logs..."

docker-compose logs -f
EOF

chmod +x scripts/logs.sh

# Create README for development
cat > DEVELOPMENT.md << 'EOF'
# A11yomatic Development Guide

## Quick Start

1. **Set up environment variables:**
   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ```

2. **Start development environment:**
   ```bash
   ./scripts/dev.sh
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Development Commands

- Start services: `./scripts/dev.sh`
- Stop services: `./scripts/stop.sh`
- View logs: `./scripts/logs.sh`
- Rebuild services: `docker-compose up --build`

## Project Structure

```
a11yomatic/
├── backend/          # FastAPI backend
├── frontend/         # React frontend
├── docs/            # Documentation
├── scripts/         # Development scripts
├── tests/           # Test files
└── uploads/         # File uploads
```

## API Keys Required

- OpenAI API Key (for content generation)
- Hugging Face API Key (for local AI models)

## Next Steps

1. Set up your API keys in `.env`
2. Start the development environment
3. Begin implementing features according to the implementation plan
4. Run tests: `docker-compose exec backend pytest`
5. Check frontend: `docker-compose exec frontend npm test`
EOF

echo "✅ A11yomatic development environment setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Copy env.example to .env and add your API keys"
echo "2. Run './scripts/dev.sh' to start the development environment"
echo "3. Visit http://localhost:3000 to see the frontend"
echo "4. Visit http://localhost:8000/docs to see the API documentation"
echo ""
echo "📚 See DEVELOPMENT.md for detailed instructions"
