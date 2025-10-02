# A11yomatic - Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Prerequisites

- Docker and Docker Compose installed
- An AI API key (Groq or OpenAI)

### Step 1: Get Your AI API Key

#### Option A: Groq (Recommended for Development)
1. Sign up at [console.groq.com](https://console.groq.com)
2. Create an API key
3. Copy your key (starts with `gsk_...`)

#### Option B: OpenAI
1. Sign up at [platform.openai.com](https://platform.openai.com)
2. Create an API key
3. Copy your key (starts with `sk-...`)

### Step 2: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your API key
nano .env

# For Groq:
GROQ_API_KEY=gsk_your-key-here
OPENAI_API_BASE_URL=https://api.groq.com/openai/v1

# For OpenAI:
OPENAI_API_KEY=sk-your-key-here
OPENAI_API_BASE_URL=https://api.openai.com/v1
```

### Step 3: Start the Application

```bash
# Make script executable
chmod +x scripts/dev.sh

# Run setup script
./scripts/dev.sh
```

### Step 4: Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### Step 5: Test Your Setup

```bash
# Test AI connection
./scripts/test-ai.sh
```

## 📖 Using A11yomatic

### 1. Create an Account
- Go to http://localhost:3000
- Click "Register here"
- Fill in your details

### 2. Upload a PDF
- Click "Upload PDF" in the navigation
- Drag & drop your PDF or click to browse
- Wait for the analysis to complete

### 3. Review Results
- View your accessibility score
- See detailed issues by severity
- Get AI-powered remediation suggestions

### 4. Apply Fixes
- Click "Generate Fix" for any issue
- Review the AI-generated suggestion
- Approve to apply the remediation

## 🛠️ Development

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Restart Services
```bash
docker-compose restart
```

### Stop Services
```bash
docker-compose down
```

### Clean Up
```bash
# Stop and remove all containers, volumes
docker-compose down -v

# Remove uploaded files
rm -rf uploads/*
```

## 📚 Key Features

### PDF Analysis
- Automated WCAG 2.1 compliance checking
- Section 508 validation
- Image accessibility (alt text detection)
- Table structure analysis
- Document structure validation

### AI-Powered Remediation
- Alt text generation for images
- Heading structure suggestions
- Table accessibility improvements
- Content reorganization recommendations

### Reporting
- Comprehensive accessibility reports
- Issue severity classification
- Export to JSON format
- Analytics dashboard

## 🔧 Troubleshooting

### Backend won't start
```bash
# Check logs
docker-compose logs backend

# Common issues:
# - Database connection: Check DATABASE_URL in .env
# - Missing dependencies: Rebuild container
docker-compose build backend
```

### Frontend won't start
```bash
# Check logs
docker-compose logs frontend

# Rebuild if needed
docker-compose build frontend
```

### AI service not working
```bash
# Verify API key is set
grep GROQ_API_KEY .env

# Test connection
./scripts/test-ai.sh

# Check API base URL matches your provider
```

### Database issues
```bash
# Reset database
docker-compose down -v
docker-compose up -d
```

## 📖 Additional Resources

- [Full Documentation](docs/user-guide.md)
- [Architecture Overview](docs/architecture.md)
- [Custom AI Setup](docs/custom-ai-setup.md)
- [Groq Setup Guide](GROQ_SETUP.md)

## 🤝 Support

For issues or questions:
1. Check the [troubleshooting section](#-troubleshooting)
2. Review the documentation
3. Check Docker logs for error messages

## 🎉 Success!

You're now ready to start analyzing and remediating PDF accessibility issues with A11yomatic!
