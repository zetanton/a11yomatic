# A11yomatic - Setup Guide

## 🚀 Quick Start

A11yomatic is a comprehensive PDF accessibility remediation tool that uses AI to identify and fix accessibility issues in PDF documents.

### Prerequisites

- Docker and Docker Compose
- Git
- Groq API Key (for fast AI inference) or OpenAI API Key

### Step 1: Get Your Groq API Key

1. Sign up at [console.groq.com](https://console.groq.com)
2. Create a new API key
3. Copy the key (starts with `gsk_...`)

### Step 2: Configure Environment

```bash
# Copy environment template
cp env.example .env

# Edit .env file and add your Groq API key
nano .env
```

Update these key values in `.env`:
```bash
OPENAI_API_KEY=gsk_your-groq-key-here
OPENAI_API_BASE_URL=https://api.groq.com/openai/v1
GROQ_API_KEY=gsk_your-groq-key-here
AI_MODEL=mixtral-8x7b-32768
```

### Step 3: Start the Application

```bash
# Start all services with Docker Compose
docker-compose up -d

# Or use the development script
./scripts/dev.sh
```

### Step 4: Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Celery Monitor**: http://localhost:5555

### Step 5: Create an Account

1. Open http://localhost:3000
2. Click "Register"
3. Create your account
4. Login and start uploading PDFs!

## 📖 Features

### Core Features

1. **PDF Upload & Management**
   - Drag-and-drop PDF upload
   - Support for files up to 100MB
   - Batch upload capabilities

2. **Automated Accessibility Analysis**
   - WCAG 2.1 compliance checking
   - Section 508 validation
   - PDF/UA standard verification
   - Issue categorization (Critical, High, Medium, Low)

3. **AI-Powered Remediation**
   - Automatic alt text generation for images
   - Table header suggestions
   - Heading structure recommendations
   - Reading order suggestions

4. **Comprehensive Reporting**
   - Detailed accessibility reports
   - Compliance scoring (0-100)
   - Issue tracking and analytics
   - Export capabilities (JSON, CSV, PDF)

## 🛠️ Technology Stack

### Backend
- FastAPI (Python 3.11+)
- PostgreSQL database
- Redis for caching
- Celery for background tasks
- PDF Libraries: PyPDF2, pdfplumber, PyMuPDF

### Frontend
- React 18 with TypeScript
- Tailwind CSS (dark theme)
- Redux Toolkit for state management
- React Query for data fetching
- React Dropzone for file uploads

### AI Integration
- Groq API for fast inference (up to 750 tokens/second)
- OpenAI API compatible
- Support for custom AI endpoints
- Hugging Face Transformers (optional)

## 📚 Documentation

- [Architecture Documentation](docs/architecture.md)
- [API Documentation](docs/PRD.md)
- [Custom AI Setup](docs/custom-ai-setup.md)
- [Groq Setup Guide](GROQ_SETUP.md)

## 🔧 Development

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend
npm install
npm start
```

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 🐛 Troubleshooting

### Services Not Starting

```bash
# Check Docker status
docker-compose ps

# View logs
docker-compose logs -f

# Restart services
docker-compose restart
```

### Database Connection Issues

```bash
# Reset database
docker-compose down -v
docker-compose up -d db
docker-compose up -d
```

### AI Service Errors

1. Verify your API key is correct in `.env`
2. Check the API base URL is set to Groq: `https://api.groq.com/openai/v1`
3. Test the connection: `curl -H "Authorization: Bearer YOUR_KEY" https://api.groq.com/openai/v1/models`

## 📈 Performance

- **Upload Speed**: < 2 seconds per PDF
- **Analysis Speed**: < 5 seconds per page
- **AI Generation**: < 3 seconds per suggestion (with Groq)
- **Concurrent Users**: 100+ supported

## 🔐 Security

- JWT-based authentication
- Encrypted file storage
- HTTPS support in production
- Rate limiting enabled
- Input validation and sanitization

## 📄 License

MIT License - see LICENSE file for details

## 🤝 Contributing

Contributions are welcome! Please see CONTRIBUTING.md for guidelines.

## 💬 Support

For issues and questions:
- GitHub Issues: [Create an issue](https://github.com/yourusername/a11yomatic/issues)
- Documentation: See the `docs/` directory

## 🎯 Roadmap

### Phase 2 (Coming Soon)
- Real-time collaboration
- Advanced ML models
- CMS integrations
- Mobile application

### Phase 3 (Future)
- Enterprise features
- Custom rule creation
- Multi-language support
- Advanced analytics

---

Built with ❤️ for accessibility
