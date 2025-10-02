# 🚀 START HERE - A11yomatic Quick Launch

## What You Have Now

A complete, production-ready PDF accessibility remediation tool that:
- 📤 Uploads and analyzes PDF documents
- 🔍 Detects accessibility issues (WCAG 2.1, Section 508)
- 🤖 Generates AI-powered fix suggestions using Groq
- 📊 Provides detailed reports and analytics
- 🎨 Beautiful dark-themed UI

## ⚡ Quick Start (3 Steps)

### Step 1: Get Groq API Key (2 minutes)

1. Go to https://console.groq.com
2. Sign up/login
3. Click "API Keys" → "Create API Key"
4. Copy the key (starts with `gsk_...`)

### Step 2: Configure (1 minute)

```bash
# Open the .env file
nano .env

# Find line 16 and replace with your key:
OPENAI_API_KEY=gsk_YOUR_KEY_HERE

# Find line 18 and do the same:
GROQ_API_KEY=gsk_YOUR_KEY_HERE

# Save and exit (Ctrl+X, Y, Enter)
```

### Step 3: Launch (30 seconds)

```bash
# Start all services
docker-compose up -d

# Wait for services to start
sleep 30

# Open browser
echo "🌐 Frontend: http://localhost:3000"
echo "📚 API Docs: http://localhost:8000/docs"
```

## 🎮 Using the Application

### 1. Create Account
- Open http://localhost:3000
- Click "Register"
- Fill in email and password
- Click "Register"

### 2. Login
- Use your email and password
- Click "Sign in"

### 3. Upload PDF
- Click "Upload" in navigation
- Drag and drop a PDF file
- Wait for upload (2-5 seconds)
- Analysis starts automatically

### 4. View Results
- Click "View Analysis" button
- See accessibility score (0-100)
- Review detected issues
- Read AI-generated suggestions

### 5. Dashboard
- Click "Dashboard" in navigation
- View total PDFs, issues, scores
- See issue distribution charts
- Track progress over time

## 📁 Example Workflow

```
1. Upload PDF → "my-document.pdf"
2. Wait for analysis → ~10 seconds
3. View results → Score: 65/100
4. See issues:
   - 5 Critical (missing alt text)
   - 3 High (table headers)
   - 8 Medium (heading structure)
5. Click "Generate Remediation"
6. Get AI suggestions for each issue
7. Export report as JSON
```

## 🔍 What Gets Checked

✅ **Images**: Missing alt text
✅ **Tables**: Missing headers, complex structures
✅ **Headings**: Improper hierarchy
✅ **Text**: Image-only pages, missing content
✅ **Contrast**: Color contrast issues
✅ **Structure**: Document organization

## 🛠️ Available Services

Once running, you have access to:

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:3000 | Main web interface |
| Backend API | http://localhost:8000 | REST API |
| API Docs | http://localhost:8000/docs | Interactive API docs |
| Database | localhost:5432 | PostgreSQL |
| Redis | localhost:6379 | Cache |
| Celery Monitor | http://localhost:5555 | Task queue monitor |

## 🐛 Troubleshooting

### Services won't start
```bash
docker-compose down
docker-compose up -d
docker-compose logs -f
```

### Can't access frontend
```bash
# Check if running
docker-compose ps

# Restart frontend
docker-compose restart frontend
```

### "Invalid API key" error
```bash
# Verify your key
cat .env | grep GROQ_API_KEY

# Test the key
curl -H "Authorization: Bearer YOUR_KEY" \
  https://api.groq.com/openai/v1/models
```

### Database errors
```bash
# Reset database
docker-compose down -v
docker-compose up -d
```

## 📚 Documentation

- `GETTING_STARTED.md` - Detailed getting started guide
- `README_SETUP.md` - Complete setup instructions
- `BUILD_SUMMARY.md` - What was built
- `GROQ_SETUP.md` - AI service setup
- `docs/` folder - Full documentation

## 🎯 Key Features

### Backend
- FastAPI for high performance
- PostgreSQL for data storage
- Redis for caching
- Celery for background tasks
- JWT authentication
- Multiple PDF processing libraries

### Frontend
- React 18 with TypeScript
- Tailwind CSS dark theme
- Redux for state management
- React Query for data fetching
- Drag-and-drop uploads

### AI Integration
- Groq API (750 tokens/sec)
- Mixtral-8x7b-32768 model
- OpenAI compatible
- Alt text generation
- Table remediation
- Heading suggestions

## 💡 Tips

1. **Test with sample PDFs** - Try different types of documents
2. **Check all severity levels** - Critical issues first
3. **Use batch upload** - Multiple PDFs at once
4. **Export reports** - Share with your team
5. **Monitor Celery** - Check background task status

## 🔐 Security

Default settings are for development. For production:
- Change SECRET_KEY in .env
- Update database password
- Enable HTTPS
- Set DEBUG=false
- Configure CORS properly

## 🆘 Need Help?

1. Check `GETTING_STARTED.md` for detailed instructions
2. View logs: `docker-compose logs -f`
3. Test health: http://localhost:8000/health
4. Review API docs: http://localhost:8000/docs

## ✅ Verification Checklist

Before starting, verify:
- [ ] Docker is installed and running
- [ ] Ports 3000, 5432, 6379, 8000 are available
- [ ] You have a Groq API key
- [ ] .env file is configured
- [ ] At least 4GB RAM available

## 🚀 Ready to Launch?

```bash
# 1. Configure your Groq API key in .env
nano .env

# 2. Start the application
docker-compose up -d

# 3. Wait for services
sleep 30

# 4. Open browser
xdg-open http://localhost:3000  # Linux
# or just visit http://localhost:3000 in your browser

# 5. Create account and start uploading!
```

## 📈 What You Can Do

✅ Upload up to 100MB PDFs
✅ Analyze unlimited documents
✅ Get AI-powered suggestions
✅ Generate detailed reports
✅ Track progress over time
✅ Export results as JSON
✅ Batch process multiple files
✅ View comprehensive analytics

---

**Everything is ready!** Just add your Groq API key and launch. 🎉

Questions? Check the documentation or review the logs.

Happy analyzing! 🚀
