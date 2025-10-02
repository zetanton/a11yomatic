# A11yomatic - PDF Accessibility Remediation Tool

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-500000.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.11+-500000.svg)
![React](https://img.shields.io/badge/react-18.2+-500000.svg)
![Texas A&M](https://img.shields.io/badge/Texas%20A%26M-University-500000.svg)

A comprehensive tool for identifying, analyzing, and remediating PDF accessibility issues using AI-powered content generation and modern web technologies.

**Developed at Texas A&M University**

[Quick Start](#-quick-start) • [Features](#-key-features) • [Documentation](#-documentation) • [Architecture](#-architecture)

</div>

---

## 🎯 Overview

A11yomatic is designed to help organizations ensure their PDF documents meet accessibility standards (WCAG 2.1, Section 508, PDF/UA) by providing automated analysis, remediation suggestions, and bulk processing capabilities.

### Why A11yomatic?

- **🤖 AI-Powered**: Uses advanced AI models (Groq/OpenAI) for intelligent content generation
- **🚀 Fast**: Automated analysis saves hours of manual work
- **📊 Comprehensive**: Checks multiple accessibility standards
- **🎨 Beautiful UI**: Texas A&M branded interface with Aggie Maroon theme
- **🆓 Free & Open Source**: Built with free tools and libraries

## ✨ Key Features

### PDF Analysis
- **Automated WCAG 2.1 compliance checking**
- **Section 508 validation**
- **PDF/UA standard support**
- **Real-time issue detection**
- **Severity classification** (Critical, High, Medium, Low)

### AI-Powered Remediation
- **Alt text generation** for images
- **Heading structure** suggestions
- **Table accessibility** improvements
- **Reading order** recommendations
- **Color contrast** analysis

### User Experience
- **Drag-and-drop** PDF upload
- **Real-time progress** tracking
- **Interactive dashboard**
- **Detailed reports** with export
- **Bulk processing** support

## 🚀 Quick Start

### Prerequisites

```bash
# Required
- Docker & Docker Compose
- AI API Key (Groq recommended for development)

# Optional
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)
```

### Installation

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd a11yomatic

# 2. Set up environment
cp .env.example .env
# Edit .env with your API keys (see GROQ_SETUP.md)

# 3. Start the application
chmod +x scripts/dev.sh
./scripts/dev.sh

# 4. Access the application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Get Your AI API Key

#### Groq (Recommended - Fast & Free Tier)
1. Sign up at [console.groq.com](https://console.groq.com)
2. Create API key (starts with `gsk_`)
3. Add to `.env`: `GROQ_API_KEY=gsk_your-key-here`
4. Set: `OPENAI_API_BASE_URL=https://api.groq.com/openai/v1`

#### OpenAI
1. Sign up at [platform.openai.com](https://platform.openai.com)
2. Create API key (starts with `sk-`)
3. Add to `.env`: `OPENAI_API_KEY=sk-your-key-here`

See [GROQ_SETUP.md](GROQ_SETUP.md) for detailed instructions.

## 🛠️ Tech Stack

### Backend
- **FastAPI** - High-performance Python framework
- **PostgreSQL** - Relational database
- **Redis** - Caching and session management
- **PyPDF2, pdfplumber, PyMuPDF** - PDF processing
- **OpenAI/Groq API** - AI content generation

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first styling
- **Redux Toolkit** - State management
- **React Query** - Data fetching

### Infrastructure
- **Docker & Docker Compose** - Containerization
- **Nginx** - Web server
- **Celery** - Background tasks

## 📁 Project Structure

```
a11yomatic/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/v1/         # API endpoints
│   │   ├── core/           # Configuration & security
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   └── main.py         # FastAPI app
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── services/      # API services
│   │   ├── store/         # Redux store
│   │   └── App.tsx
│   ├── Dockerfile
│   └── package.json
├── docs/                  # Documentation
├── scripts/               # Utility scripts
├── docker-compose.yml     # Docker orchestration
├── .env.example          # Environment template
└── README.md
```

## 📖 Documentation

- **[Quick Start Guide](QUICKSTART.md)** - Get up and running in 5 minutes
- **[Groq Setup](GROQ_SETUP.md)** - Fast AI inference setup
- **[Architecture](docs/architecture.md)** - System design and components
- **[Implementation Plan](docs/implementation-plan.md)** - Development roadmap
- **[User Guide](docs/user-guide.md)** - Complete user manual
- **[Tech Stack Details](docs/tech-stack.md)** - Technology choices
- **[Custom AI Setup](docs/custom-ai-setup.md)** - Advanced AI configuration

## 🔧 Development

### Local Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r ../requirements.txt
uvicorn app.main:app --reload
```

### Local Frontend Development

```bash
cd frontend
npm install
npm start
```

### Run Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

## 🎯 Usage

### 1. Register an Account
Navigate to http://localhost:3000 and create an account.

### 2. Upload a PDF
- Click "Upload PDF" in the navigation
- Drag & drop or select your PDF file
- Wait for automatic analysis to complete

### 3. Review Results
- View overall accessibility score
- See categorized issues by severity
- Check WCAG criteria violations

### 4. Generate Fixes
- Click "Generate Fix" for any issue
- Review AI-powered remediation suggestions
- Approve and apply fixes

### 5. Export Reports
- Generate comprehensive reports
- Export as JSON for integration
- Track progress over time

## 📊 API Documentation

Once running, visit http://localhost:8000/docs for interactive API documentation powered by Swagger UI.

### Key Endpoints

```
Authentication
POST /api/v1/auth/register    - Register new user
POST /api/v1/auth/login        - Login

PDF Management
POST /api/v1/pdfs/upload       - Upload PDF
GET  /api/v1/pdfs/             - List PDFs
GET  /api/v1/pdfs/{id}         - Get PDF details

Analysis
POST /api/v1/analysis/{id}/analyze  - Start analysis
GET  /api/v1/analysis/{id}          - Get results

Remediation
POST /api/v1/remediation/{issue_id} - Generate fix
PUT  /api/v1/remediation/{issue_id}/approve - Approve fix

Reports
GET  /api/v1/reports/{id}           - Get report
GET  /api/v1/reports/analytics      - Get analytics
```

## 🔒 Security

- JWT-based authentication
- Password hashing with bcrypt
- Input validation and sanitization
- CORS configuration
- API rate limiting
- Secure file upload handling

## 🚧 Troubleshooting

### Backend Issues

```bash
# Check logs
docker-compose logs backend

# Rebuild container
docker-compose build backend
docker-compose up -d backend
```

### Frontend Issues

```bash
# Check logs
docker-compose logs frontend

# Rebuild container
docker-compose build frontend
docker-compose up -d frontend
```

### Database Issues

```bash
# Reset database
docker-compose down -v
docker-compose up -d
```

### AI Service Issues

```bash
# Test connection
./scripts/test-ai.sh

# Verify API key
grep GROQ_API_KEY .env

# Check API base URL
grep OPENAI_API_BASE_URL .env
```

## 🤝 Contributing

We welcome contributions! Please see our Contributing Guide for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Developed at **Texas A&M University**
- Built with [FastAPI](https://fastapi.tiangolo.com/)
- UI powered by [React](https://react.dev/) and [Tailwind CSS](https://tailwindcss.com/)
- Follows [Texas A&M Web Branding Guidelines](https://brandguide.tamu.edu/web/)
- PDF processing with [PyPDF2](https://pypdf2.readthedocs.io/), [pdfplumber](https://github.com/jsvine/pdfplumber), and [PyMuPDF](https://pymupdf.readthedocs.io/)
- AI by [Groq](https://groq.com/) / [OpenAI](https://openai.com/)

## 📞 Support

- **Documentation**: Check the [docs](docs/) folder
- **Issues**: Open an issue on GitHub
- **Questions**: See [QUICKSTART.md](QUICKSTART.md)
- **Texas A&M Resources**: [www.tamu.edu](https://www.tamu.edu)

---

<div align="center">

**[⬆ back to top](#a11yomatic---pdf-accessibility-remediation-tool)**

Made with ❤️ for accessibility at Texas A&M University

</div>
