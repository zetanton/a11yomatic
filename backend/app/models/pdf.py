"""PDF document models"""
from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base


class PDFDocument(Base):
    """PDF document model"""
    __tablename__ = "pdf_documents"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow)
    processing_status = Column(String, default="pending")  # pending, processing, completed, failed
    metadata = Column(JSON)
    
    # Relationships
    user = relationship("User", back_populates="pdf_documents")
    issues = relationship("AccessibilityIssue", back_populates="pdf", cascade="all, delete-orphan")
    reports = relationship("AnalysisReport", back_populates="pdf", cascade="all, delete-orphan")


class AccessibilityIssue(Base):
    """Accessibility issue model"""
    __tablename__ = "accessibility_issues"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    pdf_id = Column(String, ForeignKey("pdf_documents.id"))
    issue_type = Column(String, nullable=False)  # missing_alt_text, table_headers, reading_order, etc.
    severity = Column(String, nullable=False)  # critical, high, medium, low
    page_number = Column(Integer)
    description = Column(Text, nullable=False)
    wcag_criteria = Column(String)  # e.g., "1.1.1", "1.3.1"
    location = Column(JSON)  # Coordinates or location details
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    pdf = relationship("PDFDocument", back_populates="issues")
    remediation = relationship("RemediationPlan", back_populates="issue", uselist=False, cascade="all, delete-orphan")


class RemediationPlan(Base):
    """Remediation plan model"""
    __tablename__ = "remediation_plans"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    issue_id = Column(String, ForeignKey("accessibility_issues.id"), unique=True)
    ai_generated_content = Column(Text)
    user_approved = Column(Boolean, default=False)
    implementation_status = Column(String, default="pending")  # pending, applied, rejected
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    issue = relationship("AccessibilityIssue", back_populates="remediation")


class AnalysisReport(Base):
    """Analysis report model"""
    __tablename__ = "analysis_reports"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    pdf_id = Column(String, ForeignKey("pdf_documents.id"))
    overall_score = Column(Integer)  # 0-100 accessibility score
    total_issues = Column(Integer)
    critical_issues = Column(Integer)
    high_issues = Column(Integer)
    medium_issues = Column(Integer)
    low_issues = Column(Integer)
    report_data = Column(JSON)  # Detailed report data
    generated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    pdf = relationship("PDFDocument", back_populates="reports")


