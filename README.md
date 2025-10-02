# A11yomatic - PDF Accessibility Remediation Tool

A comprehensive tool for identifying, analyzing, and remediating PDF accessibility issues using AI-powered content generation and modern web technologies.

## 🎯 Overview

A11yomatic is designed to help organizations ensure their PDF documents meet accessibility standards (WCAG 2.1, Section 508, PDF/UA) by providing automated analysis, remediation suggestions, and bulk processing capabilities.

## ✨ Key Features

- **Automated PDF Analysis**: Identify accessibility issues using free libraries
- **AI-Powered Remediation**: Generate accessible content using LLMs
- **Bulk Processing**: Handle multiple PDFs simultaneously
- **Interactive Dashboard**: Beautiful dark interface for managing remediation
- **Comprehensive Reports**: Detailed accessibility reports and progress tracking
- **Free & Open Source**: Built with free libraries and tools

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: React with TypeScript
- **PDF Processing**: PyPDF2, pdfplumber, pymupdf
- **AI Integration**: OpenAI API, Hugging Face Transformers
- **Database**: SQLite/PostgreSQL
- **Styling**: Tailwind CSS with dark theme
- **Deployment**: Docker containers

## 📁 Project Structure

```
a11yomatic/
├── backend/                 # FastAPI backend
├── frontend/               # React frontend
├── docs/                   # Documentation
├── tests/                  # Test suites
├── docker/                 # Docker configurations
└── scripts/               # Utility scripts
```

## 🚀 Quick Start

1. Clone the repository
2. Set up the development environment
3. Configure API keys
4. Run the application

## 📖 Documentation

- [Product Requirements Document](docs/PRD.md)
- [Technical Architecture](docs/architecture.md)
- [Custom AI Service Setup](docs/custom-ai-setup.md)
- [User Guide](docs/user-guide.md)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.
