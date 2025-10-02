# System Architecture
## A11yomatic - PDF Accessibility Remediation Tool

### 1. High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   AI Services   │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (OpenAI/HF)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CDN/Static     │    │   Database      │    │   File Storage  │
│   Assets        │    │   (PostgreSQL)  │    │   (Local/S3)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 2. Backend Architecture (FastAPI)

#### 2.1 Core Components

**API Layer**
```python
# Main application structure
app/
├── main.py                 # FastAPI application entry point
├── api/
│   ├── v1/
│   │   ├── auth.py         # Authentication endpoints
│   │   ├── pdfs.py         # PDF management endpoints
│   │   ├── analysis.py    # Accessibility analysis endpoints
│   │   ├── remediation.py  # AI remediation endpoints
│   │   └── reports.py      # Reporting endpoints
│   └── dependencies.py     # Shared dependencies
├── core/
│   ├── config.py          # Configuration management
│   ├── security.py        # Security utilities
│   └── database.py        # Database connection
├── models/
│   ├── user.py            # User models
│   ├── pdf.py             # PDF document models
│   ├── analysis.py        # Analysis result models
│   └── remediation.py     # Remediation models
├── services/
│   ├── pdf_processor.py   # PDF processing service
│   ├── ai_service.py      # AI integration service
│   ├── analysis_service.py # Accessibility analysis
│   └── remediation_service.py # Content generation
└── utils/
    ├── validators.py      # Input validation
    ├── file_handlers.py   # File operations
    └── pdf_utils.py       # PDF utilities
```

#### 2.2 Key Services

**PDF Processing Service**
```python
class PDFProcessor:
    def __init__(self):
        self.pdf_analyzer = PDFAnalyzer()
        self.content_extractor = ContentExtractor()
        self.structure_analyzer = StructureAnalyzer()
    
    async def analyze_accessibility(self, pdf_path: str) -> AnalysisResult:
        """Analyze PDF for accessibility issues"""
        pass
    
    async def extract_content(self, pdf_path: str) -> ExtractedContent:
        """Extract text, images, and structure from PDF"""
        pass
    
    async def generate_remediation(self, issues: List[Issue]) -> RemediationPlan:
        """Generate AI-powered remediation suggestions"""
        pass
```

**AI Integration Service**
```python
class AIService:
    def __init__(self):
        self.openai_client = OpenAI()
        self.huggingface_client = HuggingFaceClient()
    
    async def generate_alt_text(self, image_description: str) -> str:
        """Generate alternative text for images"""
        pass
    
    async def generate_heading_structure(self, content: str) -> List[Heading]:
        """Generate proper heading structure"""
        pass
    
    async def improve_table_accessibility(self, table_data: dict) -> dict:
        """Generate accessible table structure"""
        pass
```

### 3. Frontend Architecture (React + TypeScript)

#### 3.1 Component Structure

```
src/
├── components/
│   ├── common/             # Reusable components
│   │   ├── Button.tsx
│   │   ├── Modal.tsx
│   │   ├── LoadingSpinner.tsx
│   │   └── FileUpload.tsx
│   ├── layout/             # Layout components
│   │   ├── Header.tsx
│   │   ├── Sidebar.tsx
│   │   └── Footer.tsx
│   ├── dashboard/          # Dashboard components
│   │   ├── ProjectOverview.tsx
│   │   ├── RecentActivity.tsx
│   │   └── QuickActions.tsx
│   ├── pdf/               # PDF management components
│   │   ├── PDFUpload.tsx
│   │   ├── PDFList.tsx
│   │   └── PDFPreview.tsx
│   ├── analysis/          # Analysis components
│   │   ├── IssueList.tsx
│   │   ├── IssueDetail.tsx
│   │   └── AnalysisProgress.tsx
│   ├── remediation/       # Remediation components
│   │   ├── RemediationEditor.tsx
│   │   ├── AIContentGenerator.tsx
│   │   └── RemediationPreview.tsx
│   └── reports/           # Reporting components
│       ├── ReportGenerator.tsx
│       ├── ReportViewer.tsx
│       └── AnalyticsDashboard.tsx
├── hooks/                 # Custom React hooks
│   ├── usePDFUpload.ts
│   ├── useAnalysis.ts
│   └── useRemediation.ts
├── services/              # API services
│   ├── api.ts
│   ├── pdfService.ts
│   └── aiService.ts
├── store/                 # State management
│   ├── slices/
│   │   ├── pdfSlice.ts
│   │   ├── analysisSlice.ts
│   │   └── userSlice.ts
│   └── store.ts
└── utils/                 # Utility functions
    ├── constants.ts
    ├── helpers.ts
    └── validators.ts
```

#### 3.2 State Management

**Redux Toolkit Store Structure**
```typescript
interface RootState {
  user: UserState;
  pdfs: PDFState;
  analysis: AnalysisState;
  remediation: RemediationState;
  ui: UIState;
}

interface PDFState {
  documents: PDFDocument[];
  uploadProgress: UploadProgress;
  selectedDocument: string | null;
  processingStatus: ProcessingStatus;
}

interface AnalysisState {
  issues: AccessibilityIssue[];
  analysisProgress: number;
  currentAnalysis: AnalysisResult | null;
  filters: AnalysisFilters;
}
```

### 4. Database Schema

#### 4.1 Core Tables

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    organization VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- PDF Documents table
CREATE TABLE pdf_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processing_status VARCHAR(50) DEFAULT 'pending',
    metadata JSONB
);

-- Accessibility Issues table
CREATE TABLE accessibility_issues (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pdf_id UUID REFERENCES pdf_documents(id),
    issue_type VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    page_number INTEGER,
    description TEXT NOT NULL,
    wcag_criteria VARCHAR(50),
    location JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Remediation Plans table
CREATE TABLE remediation_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    issue_id UUID REFERENCES accessibility_issues(id),
    ai_generated_content TEXT,
    user_approved BOOLEAN DEFAULT FALSE,
    implementation_status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Analysis Reports table
CREATE TABLE analysis_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pdf_id UUID REFERENCES pdf_documents(id),
    overall_score INTEGER,
    total_issues INTEGER,
    critical_issues INTEGER,
    report_data JSONB,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 5. API Design

#### 5.1 RESTful Endpoints

```python
# Authentication
POST /api/v1/auth/login
POST /api/v1/auth/register
POST /api/v1/auth/refresh
POST /api/v1/auth/logout

# PDF Management
GET /api/v1/pdfs                    # List user's PDFs
POST /api/v1/pdfs/upload            # Upload new PDF
GET /api/v1/pdfs/{pdf_id}            # Get PDF details
DELETE /api/v1/pdfs/{pdf_id}         # Delete PDF
POST /api/v1/pdfs/{pdf_id}/analyze   # Start analysis

# Analysis
GET /api/v1/analysis/{pdf_id}       # Get analysis results
GET /api/v1/analysis/{pdf_id}/issues # Get specific issues
POST /api/v1/analysis/{pdf_id}/re-analyze # Re-analyze PDF

# Remediation
GET /api/v1/remediation/{issue_id}  # Get remediation suggestions
POST /api/v1/remediation/{issue_id}/apply # Apply remediation
POST /api/v1/remediation/bulk       # Bulk remediation

# Reports
GET /api/v1/reports/{pdf_id}         # Generate report
GET /api/v1/reports/analytics       # Get analytics data
POST /api/v1/reports/export         # Export reports
```

#### 5.2 WebSocket Events

```typescript
// Real-time updates for processing status
interface WebSocketEvents {
  'pdf.upload.progress': { pdfId: string; progress: number };
  'pdf.analysis.started': { pdfId: string };
  'pdf.analysis.progress': { pdfId: string; progress: number };
  'pdf.analysis.completed': { pdfId: string; result: AnalysisResult };
  'pdf.remediation.applied': { issueId: string; success: boolean };
}
```

### 6. Security Architecture

#### 6.1 Authentication & Authorization

```python
# JWT-based authentication
class SecurityConfig:
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

# Role-based access control
class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"

# API key management for AI services
class AIServiceConfig:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    HUGGINGFACE_API_KEY: str = os.getenv("HUGGINGFACE_API_KEY")
```

#### 6.2 Data Protection

```python
# File encryption
class FileSecurity:
    def encrypt_file(self, file_path: str) -> str:
        """Encrypt uploaded files"""
        pass
    
    def decrypt_file(self, encrypted_path: str) -> str:
        """Decrypt files for processing"""
        pass

# Input validation
class InputValidator:
    def validate_pdf_file(self, file: UploadFile) -> bool:
        """Validate PDF file integrity"""
        pass
    
    def sanitize_user_input(self, text: str) -> str:
        """Sanitize user input to prevent XSS"""
        pass
```

### 7. Performance Optimization

#### 7.1 Caching Strategy

```python
# Redis caching for frequently accessed data
class CacheManager:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
    
    async def cache_analysis_result(self, pdf_id: str, result: dict):
        """Cache analysis results"""
        pass
    
    async def get_cached_result(self, pdf_id: str) -> dict:
        """Retrieve cached analysis results"""
        pass
```

#### 7.2 Background Processing

```python
# Celery for background tasks
from celery import Celery

celery_app = Celery('a11yomatic')

@celery_app.task
def analyze_pdf_async(pdf_id: str):
    """Background PDF analysis task"""
    pass

@celery_app.task
def generate_remediation_async(issue_id: str):
    """Background AI content generation"""
    pass
```

### 8. Monitoring & Logging

#### 8.1 Application Monitoring

```python
# Structured logging
import structlog

logger = structlog.get_logger()

class MonitoringService:
    def log_pdf_processing(self, pdf_id: str, status: str):
        """Log PDF processing events"""
        logger.info("PDF processing", pdf_id=pdf_id, status=status)
    
    def track_performance_metrics(self, operation: str, duration: float):
        """Track performance metrics"""
        logger.info("Performance metric", operation=operation, duration=duration)
```

#### 8.2 Health Checks

```python
# Health check endpoints
@app.get("/health")
async def health_check():
    """Application health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }

@app.get("/health/database")
async def database_health():
    """Database connectivity check"""
    pass

@app.get("/health/ai-services")
async def ai_services_health():
    """AI services availability check"""
    pass
```

### 9. Deployment Architecture

#### 9.1 Docker Configuration

```dockerfile
# Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```dockerfile
# Frontend Dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=0 /app/dist /usr/share/nginx/html
```

#### 9.2 Docker Compose

```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/a11yomatic
    depends_on:
      - db
      - redis

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=a11yomatic
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

### 10. Development Workflow

#### 10.1 Local Development Setup

```bash
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend setup
cd frontend
npm install
npm run dev

# Database setup
docker-compose up -d db redis
```

#### 10.2 Testing Strategy

```python
# Backend testing
pytest tests/
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

# Frontend testing
npm run test
npm run test:e2e
npm run test:coverage
```

This architecture provides a solid foundation for building a scalable, maintainable PDF accessibility remediation tool with modern web technologies and AI integration.
