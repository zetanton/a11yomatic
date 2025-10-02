# UI/UX Design System
## A11yomatic - PDF Accessibility Remediation Tool

### 1. Design Philosophy

**Core Principles:**
- **Accessibility First**: Every component designed with WCAG 2.1 AA compliance
- **Dark Theme**: Modern, professional dark interface
- **Intuitive Workflow**: Clear user journey from upload to remediation
- **Visual Hierarchy**: Clear information architecture
- **Responsive Design**: Seamless experience across all devices

### 2. Color Palette

#### 2.1 Dark Theme Colors
```css
:root {
  /* Primary Colors */
  --primary-50: #f0f9ff;
  --primary-100: #e0f2fe;
  --primary-500: #0ea5e9;
  --primary-600: #0284c7;
  --primary-700: #0369a1;
  --primary-900: #0c4a6e;

  /* Dark Theme Base */
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

  /* Semantic Colors */
  --success-500: #10b981;
  --warning-500: #f59e0b;
  --error-500: #ef4444;
  --info-500: #3b82f6;

  /* Background Colors */
  --bg-primary: #0f172a;
  --bg-secondary: #1e293b;
  --bg-tertiary: #334155;
  --bg-card: #1e293b;
  --bg-hover: #334155;

  /* Text Colors */
  --text-primary: #f8fafc;
  --text-secondary: #cbd5e1;
  --text-muted: #94a3b8;
  --text-disabled: #64748b;
}
```

#### 2.2 Accessibility Considerations
- **High Contrast**: Minimum 4.5:1 contrast ratio for normal text
- **Color Independence**: Information not conveyed by color alone
- **Focus Indicators**: Clear focus states for keyboard navigation
- **Text Scaling**: Support for 200% zoom without horizontal scrolling

### 3. Typography

#### 3.1 Font Stack
```css
/* Primary Font - Inter (Accessible, modern) */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Monospace Font - JetBrains Mono (Code, technical content) */
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
  --font-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
}
```

#### 3.2 Typography Scale
```css
/* Headings */
.text-h1 { font-size: 2.5rem; font-weight: 700; line-height: 1.2; }
.text-h2 { font-size: 2rem; font-weight: 600; line-height: 1.3; }
.text-h3 { font-size: 1.5rem; font-weight: 600; line-height: 1.4; }
.text-h4 { font-size: 1.25rem; font-weight: 500; line-height: 1.4; }

/* Body Text */
.text-body-lg { font-size: 1.125rem; font-weight: 400; line-height: 1.6; }
.text-body { font-size: 1rem; font-weight: 400; line-height: 1.6; }
.text-body-sm { font-size: 0.875rem; font-weight: 400; line-height: 1.5; }

/* Labels and Captions */
.text-label { font-size: 0.875rem; font-weight: 500; line-height: 1.4; }
.text-caption { font-size: 0.75rem; font-weight: 400; line-height: 1.4; }
```

### 4. Component Library

#### 4.1 Buttons
```css
/* Primary Button */
.btn-primary {
  background: linear-gradient(135deg, var(--primary-600), var(--primary-700));
  color: var(--text-primary);
  border: none;
  border-radius: 0.5rem;
  padding: 0.75rem 1.5rem;
  font-weight: 500;
  transition: all 0.2s ease;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
}

.btn-primary:hover {
  background: linear-gradient(135deg, var(--primary-700), var(--primary-800));
  transform: translateY(-1px);
  box-shadow: 0 6px 8px -1px rgba(0, 0, 0, 0.4);
}

.btn-primary:focus {
  outline: 2px solid var(--primary-500);
  outline-offset: 2px;
}

/* Secondary Button */
.btn-secondary {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid var(--dark-600);
  border-radius: 0.5rem;
  padding: 0.75rem 1.5rem;
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background: var(--bg-hover);
  border-color: var(--dark-500);
}
```

#### 4.2 Cards
```css
.card {
  background: var(--bg-card);
  border: 1px solid var(--dark-600);
  border-radius: 0.75rem;
  padding: 1.5rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
  transition: all 0.2s ease;
}

.card:hover {
  border-color: var(--dark-500);
  box-shadow: 0 8px 12px -1px rgba(0, 0, 0, 0.3);
}

.card-header {
  border-bottom: 1px solid var(--dark-600);
  padding-bottom: 1rem;
  margin-bottom: 1rem;
}

.card-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}
```

#### 4.3 Form Elements
```css
/* Input Fields */
.input {
  background: var(--bg-secondary);
  border: 1px solid var(--dark-600);
  border-radius: 0.5rem;
  padding: 0.75rem 1rem;
  color: var(--text-primary);
  font-size: 1rem;
  transition: all 0.2s ease;
  width: 100%;
}

.input:focus {
  outline: none;
  border-color: var(--primary-500);
  box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.1);
}

.input::placeholder {
  color: var(--text-muted);
}

/* File Upload Area */
.upload-area {
  border: 2px dashed var(--dark-600);
  border-radius: 0.75rem;
  padding: 3rem 2rem;
  text-align: center;
  background: var(--bg-secondary);
  transition: all 0.2s ease;
  cursor: pointer;
}

.upload-area:hover,
.upload-area.drag-active {
  border-color: var(--primary-500);
  background: rgba(14, 165, 233, 0.05);
}
```

### 5. Layout System

#### 5.1 Grid System
```css
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.grid {
  display: grid;
  gap: 1.5rem;
}

.grid-cols-1 { grid-template-columns: repeat(1, 1fr); }
.grid-cols-2 { grid-template-columns: repeat(2, 1fr); }
.grid-cols-3 { grid-template-columns: repeat(3, 1fr); }
.grid-cols-4 { grid-template-columns: repeat(4, 1fr); }

@media (max-width: 768px) {
  .grid-cols-2,
  .grid-cols-3,
  .grid-cols-4 {
    grid-template-columns: 1fr;
  }
}
```

#### 5.2 Spacing Scale
```css
:root {
  --space-1: 0.25rem;   /* 4px */
  --space-2: 0.5rem;    /* 8px */
  --space-3: 0.75rem;   /* 12px */
  --space-4: 1rem;      /* 16px */
  --space-6: 1.5rem;    /* 24px */
  --space-8: 2rem;      /* 32px */
  --space-12: 3rem;     /* 48px */
  --space-16: 4rem;     /* 64px */
}
```

### 6. Key UI Components

#### 6.1 Dashboard Layout
```typescript
// Dashboard Component Structure
const Dashboard = () => {
  return (
    <div className="min-h-screen bg-dark-900">
      {/* Header */}
      <Header />
      
      {/* Main Content */}
      <div className="flex">
        {/* Sidebar */}
        <Sidebar />
        
        {/* Main Area */}
        <main className="flex-1 p-6">
          {/* Quick Stats */}
          <StatsGrid />
          
          {/* Recent Activity */}
          <RecentActivity />
          
          {/* Quick Actions */}
          <QuickActions />
        </main>
      </div>
    </div>
  );
};
```

#### 6.2 PDF Upload Interface
```typescript
const PDFUpload = () => {
  const [dragActive, setDragActive] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  
  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-h1 mb-4">Upload PDFs for Analysis</h1>
        <p className="text-body-lg text-text-secondary">
          Drag and drop your PDF files or click to browse
        </p>
      </div>
      
      <div 
        className={`upload-area ${dragActive ? 'drag-active' : ''}`}
        onDragEnter={() => setDragActive(true)}
        onDragLeave={() => setDragActive(false)}
        onDrop={handleDrop}
      >
        <div className="text-center">
          <UploadIcon className="w-12 h-12 mx-auto mb-4 text-primary-500" />
          <p className="text-body text-text-secondary mb-2">
            Drop PDF files here or click to browse
          </p>
          <p className="text-caption text-text-muted">
            Maximum file size: 100MB per file
          </p>
        </div>
      </div>
      
      {uploadProgress > 0 && (
        <div className="mt-6">
          <ProgressBar value={uploadProgress} />
        </div>
      )}
    </div>
  );
};
```

#### 6.3 Analysis Results Viewer
```typescript
const AnalysisResults = ({ pdfId }: { pdfId: string }) => {
  const { data: analysis, isLoading } = usePDFAnalysis(pdfId);
  
  if (isLoading) {
    return <AnalysisSkeleton />;
  }
  
  return (
    <div className="space-y-6">
      {/* Summary Card */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-h3">Analysis Summary</h2>
          <Badge variant={analysis.overallScore > 80 ? 'success' : 'warning'}>
            Score: {analysis.overallScore}/100
          </Badge>
        </div>
        
        <div className="grid grid-cols-4 gap-4">
          <StatCard 
            title="Total Issues" 
            value={analysis.totalIssues}
            icon={<AlertTriangleIcon />}
          />
          <StatCard 
            title="Critical" 
            value={analysis.criticalIssues}
            icon={<XCircleIcon />}
            variant="error"
          />
          <StatCard 
            title="Warnings" 
            value={analysis.warnings}
            icon={<AlertCircleIcon />}
            variant="warning"
          />
          <StatCard 
            title="Suggestions" 
            value={analysis.suggestions}
            icon={<InfoIcon />}
            variant="info"
          />
        </div>
      </div>
      
      {/* Issues List */}
      <div className="card">
        <h3 className="text-h4 mb-4">Accessibility Issues</h3>
        <IssuesList issues={analysis.issues} />
      </div>
    </div>
  );
};
```

#### 6.4 Remediation Editor
```typescript
const RemediationEditor = ({ issue }: { issue: AccessibilityIssue }) => {
  const [content, setContent] = useState(issue.suggestedContent);
  const [isGenerating, setIsGenerating] = useState(false);
  
  const generateContent = async () => {
    setIsGenerating(true);
    try {
      const newContent = await aiService.generateContent(issue);
      setContent(newContent);
    } finally {
      setIsGenerating(false);
    }
  };
  
  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-h4">{issue.title}</h3>
        <div className="flex gap-2">
          <Button 
            variant="secondary" 
            onClick={generateContent}
            disabled={isGenerating}
          >
            {isGenerating ? 'Generating...' : 'Generate with AI'}
          </Button>
          <Button variant="primary">Apply Changes</Button>
        </div>
      </div>
      
      <div className="space-y-4">
        <div>
          <label className="text-label block mb-2">Issue Description</label>
          <p className="text-body-sm text-text-secondary">{issue.description}</p>
        </div>
        
        <div>
          <label className="text-label block mb-2">Suggested Content</label>
          <textarea
            className="input min-h-[120px]"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Enter accessible content..."
          />
        </div>
        
        <div className="flex items-center gap-4">
          <Badge variant="info">WCAG: {issue.wcagCriteria}</Badge>
          <Badge variant={issue.severity === 'critical' ? 'error' : 'warning'}>
            {issue.severity}
          </Badge>
        </div>
      </div>
    </div>
  );
};
```

### 7. Responsive Design

#### 7.1 Breakpoints
```css
/* Mobile First Approach */
@media (min-width: 640px) { /* sm */ }
@media (min-width: 768px) { /* md */ }
@media (min-width: 1024px) { /* lg */ }
@media (min-width: 1280px) { /* xl */ }
@media (min-width: 1536px) { /* 2xl */ }
```

#### 7.2 Mobile Navigation
```typescript
const MobileNavigation = () => {
  const [isOpen, setIsOpen] = useState(false);
  
  return (
    <>
      {/* Mobile Menu Button */}
      <button 
        className="md:hidden p-2"
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Toggle menu"
      >
        <MenuIcon className="w-6 h-6" />
      </button>
      
      {/* Mobile Menu */}
      {isOpen && (
        <div className="md:hidden absolute top-full left-0 right-0 bg-dark-800 border-t border-dark-600">
          <nav className="p-4 space-y-2">
            <NavLink href="/dashboard">Dashboard</NavLink>
            <NavLink href="/pdfs">PDFs</NavLink>
            <NavLink href="/reports">Reports</NavLink>
          </nav>
        </div>
      )}
    </>
  );
};
```

### 8. Accessibility Features

#### 8.1 Keyboard Navigation
```css
/* Focus indicators */
.focus-visible {
  outline: 2px solid var(--primary-500);
  outline-offset: 2px;
}

/* Skip links */
.skip-link {
  position: absolute;
  top: -40px;
  left: 6px;
  background: var(--primary-600);
  color: white;
  padding: 8px;
  text-decoration: none;
  z-index: 1000;
}

.skip-link:focus {
  top: 6px;
}
```

#### 8.2 Screen Reader Support
```typescript
// ARIA labels and descriptions
const AccessibleButton = ({ children, onClick, ariaLabel }) => {
  return (
    <button
      onClick={onClick}
      aria-label={ariaLabel}
      className="btn-primary"
    >
      {children}
    </button>
  );
};

// Live regions for dynamic content
const LiveRegion = ({ message }) => {
  return (
    <div 
      role="status" 
      aria-live="polite" 
      className="sr-only"
    >
      {message}
    </div>
  );
};
```

### 9. Animation & Transitions

#### 9.1 Micro-interactions
```css
/* Smooth transitions */
.transition {
  transition: all 0.2s ease;
}

/* Hover effects */
.hover-lift:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 12px -1px rgba(0, 0, 0, 0.3);
}

/* Loading animations */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
```

### 10. Dark Theme Implementation

#### 10.1 Theme Toggle
```typescript
const ThemeToggle = () => {
  const [isDark, setIsDark] = useState(true);
  
  useEffect(() => {
    document.documentElement.classList.toggle('dark', isDark);
  }, [isDark]);
  
  return (
    <button
      onClick={() => setIsDark(!isDark)}
      className="p-2 rounded-lg bg-dark-800 hover:bg-dark-700"
      aria-label={`Switch to ${isDark ? 'light' : 'dark'} theme`}
    >
      {isDark ? <SunIcon className="w-5 h-5" /> : <MoonIcon className="w-5 h-5" />}
    </button>
  );
};
```

This design system provides a comprehensive foundation for building a beautiful, accessible, and modern dark-themed interface for the PDF accessibility remediation tool.
