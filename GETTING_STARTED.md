# Getting Started with A11yomatic

## 🎯 What is A11yomatic?

A11yomatic is a comprehensive PDF accessibility remediation tool that uses AI to automatically identify and suggest fixes for accessibility issues in PDF documents. It helps organizations comply with WCAG 2.1, Section 508, and PDF/UA standards.

## ✨ Key Features

- 📤 **Easy PDF Upload**: Drag-and-drop interface with batch processing
- 🔍 **Automated Analysis**: Detects accessibility issues using free PDF libraries
- 🤖 **AI-Powered Fixes**: Generates remediation suggestions using Groq's fast inference
- 📊 **Detailed Reports**: Comprehensive accessibility reports with compliance scoring
- 🎨 **Beautiful UI**: Modern dark-themed interface built with React and Tailwind CSS

## 🚀 Quick Start (5 Minutes)

### 1. Prerequisites Check

Make sure you have:
- ✅ Docker and Docker Compose installed
- ✅ A Groq API key (free at [console.groq.com](https://console.groq.com))
- ✅ At least 4GB of available RAM
- ✅ Ports 3000, 5432, 6379, and 8000 available

### 2. Get Your Groq API Key

Groq provides ultra-fast AI inference (up to 750 tokens/second) perfect for development:

1. Go to [console.groq.com](https://console.groq.com)
2. Sign up/login with your email
3. Click "API Keys" in the sidebar
4. Create a new key and copy it (starts with `gsk_...`)

### 3. Clone and Configure

```bash
# Navigate to the project directory
cd /workspace

# Configure your API key
nano .env

# Find these lines and update with your Groq key:
OPENAI_API_KEY=gsk_your-key-here
GROQ_API_KEY=gsk_your-key-here
```

### 4. Start the Application

```bash
# Start all services
docker-compose up -d

# Watch the logs
docker-compose logs -f backend
```

Wait about 30 seconds for all services to initialize.

### 5. Access and Use

1. **Open the app**: http://localhost:3000
2. **Register**: Create a new account
3. **Upload a PDF**: Drag and drop any PDF document
4. **View Analysis**: See accessibility issues and AI-generated fixes!

### 6. Explore the Features

- **Dashboard**: View your analytics and statistics
- **My PDFs**: Manage all uploaded documents
- **Analysis Results**: See detailed accessibility reports
- **API Docs**: http://localhost:8000/docs for API exploration

## 📋 What Gets Analyzed?

The tool checks for:

1. **Missing Alt Text** (WCAG 1.1.1)
   - Images without descriptive text
   - AI generates appropriate alt text

2. **Table Accessibility** (WCAG 1.3.1)
   - Tables without headers
   - Complex table structures
   - AI suggests headers and captions

3. **Document Structure** (WCAG 1.3.1)
   - Missing heading hierarchy
   - AI recommends proper H1-H6 structure

4. **Reading Order** (WCAG 1.3.2)
   - Logical content flow
   - Screen reader compatibility

5. **Color Contrast** (WCAG 1.4.3)
   - Text visibility issues
   - Contrast ratio verification

6. **OCR Detection** (WCAG 1.1.1)
   - Image-only pages
   - Missing text layers

## 🎨 Technology Stack

### Backend (Python)
- **FastAPI**: High-performance async API framework
- **PostgreSQL**: Reliable data storage
- **Redis**: Fast caching layer
- **PyPDF2**: PDF metadata extraction
- **pdfplumber**: Advanced text and table extraction
- **PyMuPDF**: Detailed PDF structure analysis

### Frontend (React)
- **React 18**: Modern component-based UI
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Beautiful dark-themed design
- **Redux Toolkit**: State management
- **React Query**: Smart data fetching

### AI Integration
- **Groq API**: Ultra-fast inference (750 tokens/sec)
- **Models**: Mixtral-8x7b-32768 (recommended)
- **Fallback**: OpenAI API compatible
- **Local**: Hugging Face Transformers (optional)

## 🔧 Architecture

```
┌─────────────────────────────────────────┐
│           Frontend (React)              │
│     http://localhost:3000              │
└──────────────┬──────────────────────────┘
               │ API Calls
               ▼
┌─────────────────────────────────────────┐
│        Backend (FastAPI)                │
│     http://localhost:8000              │
└──────┬──────────────────────────────────┘
       │
       ├──► PostgreSQL (Database)
       ├──► Redis (Cache)
       ├──► Groq AI (Inference)
       └──► PDF Processing (PyPDF2, etc.)
```

## 📊 Performance Benchmarks

With Groq API:
- PDF Upload: < 2 seconds
- Analysis: < 5 seconds per page
- AI Generation: < 3 seconds per issue
- Dashboard Load: < 1 second

## 🐛 Common Issues

### "Connection refused" errors

```bash
# Check if services are running
docker-compose ps

# Restart services
docker-compose restart
```

### "Invalid API key" errors

```bash
# Verify your Groq key in .env
cat .env | grep GROQ_API_KEY

# Test the key
curl -H "Authorization: Bearer YOUR_KEY" \
  https://api.groq.com/openai/v1/models
```

### Database connection issues

```bash
# Reset database
docker-compose down -v
docker-compose up -d
```

### Frontend not loading

```bash
# Check frontend logs
docker-compose logs frontend

# Rebuild frontend
docker-compose up -d --build frontend
```

## 📚 Next Steps

1. **Upload Test PDFs**: Try different types of documents
2. **Explore API**: Visit http://localhost:8000/docs
3. **View Analytics**: Check the dashboard for insights
4. **Generate Reports**: Export accessibility reports
5. **Read Documentation**: Explore the `docs/` folder

## 🔐 Security Notes

For production deployment:
- Change the SECRET_KEY in .env
- Use strong database passwords
- Enable HTTPS
- Set DEBUG=false
- Configure proper CORS settings
- Use environment-specific .env files

## 💡 Tips

1. **Use Groq for Development**: It's fast and has a generous free tier
2. **Batch Processing**: Upload multiple PDFs at once
3. **Filter Issues**: Use severity filters to prioritize
4. **Export Reports**: Share results with your team
5. **Monitor Progress**: Check the Flower dashboard at http://localhost:5555

## 🎓 Learn More

- [Architecture Guide](docs/architecture.md)
- [API Documentation](docs/PRD.md)
- [Custom AI Setup](docs/custom-ai-setup.md)
- [Groq API Guide](GROQ_SETUP.md)

## 🆘 Need Help?

- Check the troubleshooting section in [README_SETUP.md](README_SETUP.md)
- Review the API docs at http://localhost:8000/docs
- Check Docker logs: `docker-compose logs -f`
- Verify health endpoints:
  - http://localhost:8000/health
  - http://localhost:8000/health/database
  - http://localhost:8000/health/ai-services

## 🚀 Ready to Start?

```bash
# Make sure you're in the project directory
cd /workspace

# Start the application
docker-compose up -d

# Watch it come online
docker-compose logs -f

# Open your browser
# http://localhost:3000
```

Happy analyzing! 🎉
