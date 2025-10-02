"""PDF document and analysis models"""
from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base


class PDFDocument(Base):
    """PDF document model"""
    __tablename__ = "pdf_documents"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    page_count = Column(Integer)
    upload_date = Column(DateTime, default=datetime.utcnow)
    processing_status = Column(String, default="pending")  # pending, processing, completed, failed
    metadata = Column(JSON)
    
    # Relationships
    user = relationship("User", back_populates="pdf_documents")
    issues = relationship("AccessibilityIssue", back_populates="pdf", cascade="all, delete-orphan")
    reports = relationship("AnalysisReport", back_populates="pdf", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<PDFDocument {self.filename}>"


class AccessibilityIssue(Base):
    """Accessibility issue detected in PDF"""
    __tablename__ = "accessibility_issues"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    pdf_id = Column(String, ForeignKey("pdf_documents.id"), nullable=False)
    issue_type = Column(String, nullable=False)  # missing_alt_text, table_headers, heading_structure, etc.
    severity = Column(String, nullable=False)  # critical, high, medium, low
    page_number = Column(Integer)
    description = Column(Text, nullable=False)
    wcag_criteria = Column(String)  # WCAG 2.1 criterion (e.g., "1.1.1", "1.3.1")
    location = Column(JSON)  # Detailed location information
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    pdf = relationship("PDFDocument", back_populates="issues")
    remediation = relationship(
        "RemediationPlan",
        back_populates="issue",
        uselist=False,
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<AccessibilityIssue {self.issue_type} ({self.severity})>"


class RemediationPlan(Base):
    """AI-generated remediation plan for an accessibility issue"""
    __tablename__ = "remediation_plans"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    issue_id = Column(String, ForeignKey("accessibility_issues.id"), nullable=False, unique=True)
    ai_generated_content = Column(Text)
    user_modified_content = Column(Text)
    user_approved = Column(Boolean, default=False)
    implementation_status = Column(String, default="pending")  # pending, in_progress, completed, rejected
    implementation_notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    issue = relationship("AccessibilityIssue", back_populates="remediation")
    
    def __repr__(self):
        return f"<RemediationPlan for issue {self.issue_id}>"


class AnalysisReport(Base):
    """Comprehensive analysis report for a PDF"""
    __tablename__ = "analysis_reports"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    pdf_id = Column(String, ForeignKey("pdf_documents.id"), nullable=False)
    overall_score = Column(Integer)  # 0-100 accessibility score
    total_issues = Column(Integer, default=0)
    critical_issues = Column(Integer, default=0)
    high_issues = Column(Integer, default=0)
    medium_issues = Column(Integer, default=0)
    low_issues = Column(Integer, default=0)
    wcag_compliance_level = Column(String)  # A, AA, AAA, or None
    report_data = Column(JSON)  # Detailed report information
    generated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    pdf = relationship("PDFDocument", back_populates="reports")
    
    def __repr__(self):
        return f"<AnalysisReport for PDF {self.pdf_id}>"
