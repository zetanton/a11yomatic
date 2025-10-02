# Technology Stack
## A11yomatic - PDF Accessibility Remediation Tool

### 1. Backend Technologies

#### 1.1 Core Framework
**FastAPI (Python 3.11+)**
- **Why FastAPI**: High-performance async framework with automatic API documentation
- **Key Features**: Type hints, automatic validation, WebSocket support
- **Performance**: One of the fastest Python frameworks available
- **Documentation**: Built-in OpenAPI/Swagger documentation

```python
# Example FastAPI endpoint
from fastapi import FastAPI, UploadFile, File
from typing import List

app = FastAPI(title="A11yomatic API", version="1.0.0")

@app.post("/api/v1/pdfs/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload PDF for accessibility analysis"""
    return {"message": "PDF uploaded successfully", "file_id": "uuid"}
```

#### 1.2 PDF Processing Libraries

**PyPDF2**
- **Purpose**: Basic PDF manipulation and metadata extraction
- **Use Case**: PDF structure analysis, page counting, text extraction
- **License**: Free (BSD-style)
- **Installation**: `pip install PyPDF2`

```python
import PyPDF2

def extract_pdf_metadata(pdf_path: str):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        metadata = reader.metadata
        num_pages = len(reader.pages)
        return {"metadata": metadata, "pages": num_pages}
```

**pdfplumber**
- **Purpose**: Advanced text and table extraction
- **Use Case**: Content analysis, table structure detection
- **License**: Free (MIT)
- **Installation**: `pip install pdfplumber`

```python
import pdfplumber

def extract_tables_and_text(pdf_path: str):
    with pdfplumber.open(pdf_path) as pdf:
        content = []
        for page in pdf.pages:
            text = page.extract_text()
            tables = page.extract_tables()
            content.append({"text": text, "tables": tables})
        return content
```

**PyMuPDF (fitz)**
- **Purpose**: Advanced PDF analysis and manipulation
- **Use Case**: Image extraction, detailed structure analysis
- **License**: Free (GNU AGPL)
- **Installation**: `pip install PyMuPDF`

```python
import fitz  # PyMuPDF

def analyze_pdf_structure(pdf_path: str):
    doc = fitz.open(pdf_path)
    structure = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        images = page.get_images()
        blocks = page.get_text("dict")
        structure.append({
            "page": page_num,
            "images": len(images),
            "text_blocks": blocks
        })
    return structure
```

#### 1.3 AI Integration

**OpenAI API (Configurable)**
- **Purpose**: Content generation for accessibility improvements
- **Models**: GPT-4, GPT-3.5-turbo (or custom models)
- **Use Cases**: Alt text generation, content restructuring
- **Cost**: Pay-per-use pricing model
- **Custom Support**: Configurable API base URL for custom AI services

**Groq API (Fast Inference)**
- **Purpose**: High-speed content generation for development
- **Models**: Llama 2, Mixtral, Gemma (via Groq)
- **Use Cases**: Fast alt text generation, rapid prototyping
- **Benefits**: Up to 750 tokens/second, cost-effective
- **API**: OpenAI-compatible endpoint

```python
import openai
from app.core.config import settings

class AIContentGenerator:
    def __init__(self):
        # Configure with custom base URL
        openai.api_base = settings.OPENAI_API_BASE_URL
        openai.api_key = settings.OPENAI_API_KEY
    
    async def generate_alt_text(self, image_description: str) -> str:
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[{
                "role": "system",
                "content": "Generate concise, descriptive alternative text for images"
            }, {
                "role": "user",
                "content": f"Describe this image: {image_description}"
            }],
            api_base=settings.OPENAI_API_BASE_URL,
            api_key=settings.OPENAI_API_KEY
        )
        return response.choices[0].message.content
```

**Hugging Face Transformers**
- **Purpose**: Local AI models for privacy-sensitive documents
- **Models**: BERT, T5, specialized accessibility models
- **Use Cases**: Content analysis, text classification
- **License**: Free (Apache 2.0)

```python
from transformers import pipeline

class LocalAIService:
    def __init__(self):
        self.text_classifier = pipeline(
            "text-classification",
            model="microsoft/DialoGPT-medium"
        )
    
    def classify_accessibility_issue(self, text: str) -> dict:
        result = self.text_classifier(text)
        return result
```

#### 1.4 Database & Storage

**PostgreSQL**
- **Purpose**: Primary database for application data
- **Features**: JSON support, full-text search, ACID compliance
- **License**: Free (PostgreSQL License)
- **Use Cases**: User data, PDF metadata, analysis results

```python
from sqlalchemy import create_engine, Column, String, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class PDFDocument(Base):
    __tablename__ = "pdf_documents"
    
    id = Column(String, primary_key=True)
    filename = Column(String, nullable=False)
    metadata = Column(JSON)
```

**Redis**
- **Purpose**: Caching and session management
- **Features**: In-memory storage, pub/sub, clustering
- **License**: Free (BSD)
- **Use Cases**: Session storage, analysis result caching

```python
import redis

class CacheService:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
    
    async def cache_analysis_result(self, pdf_id: str, result: dict):
        await self.redis_client.setex(
            f"analysis:{pdf_id}", 
            3600,  # 1 hour TTL
            json.dumps(result)
        )
```

### 2. Frontend Technologies

#### 2.1 Core Framework
**React 18 with TypeScript**
- **Why React**: Component-based architecture, large ecosystem
- **TypeScript**: Type safety, better developer experience
- **Features**: Hooks, Context API, Suspense, Concurrent features

```typescript
// Example React component
import React, { useState, useEffect } from 'react';

interface PDFUploadProps {
  onUpload: (file: File) => void;
  maxSize: number;
}

const PDFUpload: React.FC<PDFUploadProps> = ({ onUpload, maxSize }) => {
  const [dragActive, setDragActive] = useState(false);
  
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const files = Array.from(e.dataTransfer.files);
    files.forEach(file => onUpload(file));
  };
  
  return (
    <div 
      className="upload-area"
      onDrop={handleDrop}
      onDragOver={(e) => e.preventDefault()}
    >
      Drop PDF files here
    </div>
  );
};
```

#### 2.2 State Management
**Redux Toolkit**
- **Purpose**: Predictable state management
- **Features**: Redux DevTools, middleware, RTK Query
- **Benefits**: Time-travel debugging, middleware ecosystem

```typescript
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

interface PDFState {
  documents: PDFDocument[];
  loading: boolean;
  error: string | null;
}

const pdfSlice = createSlice({
  name: 'pdfs',
  initialState: {
    documents: [],
    loading: false,
    error: null
  } as PDFState,
  reducers: {
    addDocument: (state, action) => {
      state.documents.push(action.payload);
    }
  }
});
```

#### 2.3 Styling & UI
**Tailwind CSS**
- **Purpose**: Utility-first CSS framework
- **Features**: Dark mode support, responsive design, custom themes
- **Benefits**: Rapid development, consistent design system

```typescript
// Dark theme configuration
const theme = {
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          500: '#3b82f6',
          900: '#1e3a8a',
        },
        dark: {
          100: '#1f2937',
          200: '#111827',
          300: '#0f172a',
        }
      }
    }
  }
}
```

**Headless UI**
- **Purpose**: Accessible, unstyled UI components
- **Features**: Built-in accessibility, keyboard navigation
- **Components**: Modal, Dropdown, Tabs, Dialog

```typescript
import { Dialog, Transition } from '@headlessui/react';

const RemediationModal: React.FC = () => {
  return (
    <Transition appear show={isOpen} as={Fragment}>
      <Dialog onClose={closeModal} className="relative z-50">
        <div className="fixed inset-0 bg-black/30" />
        <div className="fixed inset-0 flex items-center justify-center">
          <Dialog.Panel className="bg-white dark:bg-gray-800 rounded-lg p-6">
            {/* Modal content */}
          </Dialog.Panel>
        </div>
      </Dialog>
    </Transition>
  );
};
```

#### 2.4 Data Fetching
**React Query (TanStack Query)**
- **Purpose**: Server state management and caching
- **Features**: Background refetching, optimistic updates, error handling
- **Benefits**: Reduces boilerplate, improves UX

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

const usePDFAnalysis = (pdfId: string) => {
  return useQuery({
    queryKey: ['pdf-analysis', pdfId],
    queryFn: () => fetchAnalysis(pdfId),
    enabled: !!pdfId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

const useRemediationMutation = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: applyRemediation,
    onSuccess: () => {
      queryClient.invalidateQueries(['pdf-analysis']);
    }
  });
};
```

### 3. Development Tools

#### 3.1 Code Quality
**ESLint + Prettier**
- **Purpose**: Code linting and formatting
- **Configuration**: TypeScript support, React rules, accessibility rules
- **Integration**: VS Code extensions, pre-commit hooks

```json
// .eslintrc.json
{
  "extends": [
    "@typescript-eslint/recommended",
    "plugin:react/recommended",
    "plugin:jsx-a11y/recommended"
  ],
  "rules": {
    "jsx-a11y/alt-text": "error",
    "jsx-a11y/aria-role": "error"
  }
}
```

**Black (Python)**
- **Purpose**: Python code formatting
- **Configuration**: Line length, string quotes, import sorting

```toml
# pyproject.toml
[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'
```

#### 3.2 Testing
**Jest + React Testing Library**
- **Purpose**: Frontend unit and integration testing
- **Features**: Snapshot testing, mocking, accessibility testing

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';

test('PDF upload component is accessible', async () => {
  render(<PDFUpload onUpload={mockUpload} maxSize={1000000} />);
  
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

**Pytest**
- **Purpose**: Backend testing
- **Features**: Fixtures, parametrization, coverage reporting

```python
import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def client():
    return TestClient(app)

def test_pdf_upload(client):
    with open("test.pdf", "rb") as f:
        response = client.post("/api/v1/pdfs/upload", files={"file": f})
    assert response.status_code == 200
```

#### 3.3 Build & Deployment
**Docker**
- **Purpose**: Containerization and deployment
- **Features**: Multi-stage builds, layer caching, security scanning

```dockerfile
# Multi-stage build for frontend
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
```

**GitHub Actions**
- **Purpose**: CI/CD pipeline
- **Features**: Automated testing, security scanning, deployment

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          npm test
          pytest tests/
```

### 4. Free & Open Source Alternatives

#### 4.1 AI Services
**Local LLM Options**
- **Ollama**: Run LLMs locally (Llama 2, Code Llama)
- **GPT4All**: Free, open-source alternative to ChatGPT
- **Hugging Face Hub**: Free model hosting and inference

```python
# Using Ollama for local AI
import requests

def generate_content_local(prompt: str) -> str:
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama2",
            "prompt": prompt,
            "stream": False
        }
    )
    return response.json()["response"]
```

#### 4.2 PDF Processing Alternatives
**pdf2image + Tesseract**
- **Purpose**: OCR for scanned PDFs
- **License**: Free (Apache 2.0)
- **Use Case**: Text extraction from image-based PDFs

```python
from pdf2image import convert_from_path
import pytesseract

def ocr_pdf_pages(pdf_path: str):
    images = convert_from_path(pdf_path)
    text_content = []
    for image in images:
        text = pytesseract.image_to_string(image)
        text_content.append(text)
    return text_content
```

### 5. Performance Considerations

#### 5.1 Backend Optimization
- **Async Processing**: FastAPI async/await for I/O operations
- **Connection Pooling**: Database connection pooling
- **Caching**: Redis for frequently accessed data
- **Background Tasks**: Celery for long-running processes

#### 5.2 Frontend Optimization
- **Code Splitting**: Lazy loading of components
- **Bundle Optimization**: Tree shaking, minification
- **Caching**: Service workers for offline functionality
- **Image Optimization**: WebP format, lazy loading

### 6. Security Considerations

#### 6.1 Authentication
- **JWT Tokens**: Stateless authentication
- **OAuth2**: Third-party authentication
- **Rate Limiting**: API request throttling

#### 6.2 Data Protection
- **File Encryption**: Encrypt uploaded PDFs
- **Input Validation**: Sanitize all user inputs
- **CORS Configuration**: Restrict cross-origin requests
- **HTTPS**: SSL/TLS encryption in transit

This technology stack provides a solid foundation for building a modern, scalable PDF accessibility remediation tool using free and open-source technologies.
