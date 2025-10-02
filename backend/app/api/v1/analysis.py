"""Analysis endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel
import logging

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.pdf import PDFDocument, AccessibilityIssue, AnalysisReport
from app.services.pdf_processor import PDFProcessor

router = APIRouter()
logger = logging.getLogger(__name__)


class IssueResponse(BaseModel):
    id: str
    issue_type: str
    severity: str
    page_number: int | None
    description: str
    wcag_criteria: str | None
    
    class Config:
        from_attributes = True


class AnalysisReportResponse(BaseModel):
    id: str
    overall_score: int
    total_issues: int
    critical_issues: int
    high_issues: int
    medium_issues: int
    low_issues: int
    
    class Config:
        from_attributes = True


class AnalysisResult(BaseModel):
    pdf_id: str
    status: str
    report: AnalysisReportResponse | None = None
    issues: List[IssueResponse] = []


async def process_pdf_analysis(pdf_id: str, db: Session):
    """Background task to process PDF analysis"""
    try:
        pdf = db.query(PDFDocument).filter(PDFDocument.id == pdf_id).first()
        if not pdf:
            logger.error(f"PDF not found: {pdf_id}")
            return
        
        # Update status
        pdf.processing_status = "processing"
        db.commit()
        
        # Analyze PDF
        processor = PDFProcessor()
        analysis_result = await processor.analyze_pdf(pdf.file_path)
        
        # Create analysis report
        report = AnalysisReport(
            pdf_id=pdf_id,
            overall_score=analysis_result["overall_score"],
            total_issues=analysis_result["total_issues"],
            critical_issues=analysis_result["critical_issues"],
            high_issues=analysis_result["high_issues"],
            medium_issues=analysis_result["medium_issues"],
            low_issues=analysis_result["low_issues"],
            report_data=analysis_result,
        )
        db.add(report)
        
        # Create issue records
        for issue_data in analysis_result["issues"]:
            issue = AccessibilityIssue(
                pdf_id=pdf_id,
                issue_type=issue_data["type"],
                severity=issue_data["severity"],
                page_number=issue_data.get("page"),
                description=issue_data["description"],
                wcag_criteria=issue_data.get("wcag_criteria"),
                location=issue_data.get("location"),
            )
            db.add(issue)
        
        # Update PDF status
        pdf.processing_status = "completed"
        db.commit()
        
        logger.info(f"Analysis completed for PDF: {pdf_id}")
        
    except Exception as e:
        logger.error(f"Error analyzing PDF {pdf_id}: {str(e)}")
        pdf = db.query(PDFDocument).filter(PDFDocument.id == pdf_id).first()
        if pdf:
            pdf.processing_status = "failed"
            db.commit()


@router.post("/{pdf_id}/analyze", status_code=status.HTTP_202_ACCEPTED)
async def analyze_pdf(
    pdf_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Start PDF accessibility analysis"""
    # Check if PDF exists
    pdf = db.query(PDFDocument).filter(
        PDFDocument.id == pdf_id,
        PDFDocument.user_id == current_user["user_id"]
    ).first()
    
    if not pdf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF not found"
        )
    
    # Start background analysis
    background_tasks.add_task(process_pdf_analysis, pdf_id, db)
    
    return {
        "message": "Analysis started",
        "pdf_id": pdf_id,
        "status": "processing"
    }


@router.get("/{pdf_id}", response_model=AnalysisResult)
async def get_analysis(
    pdf_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get analysis results for a PDF"""
    # Check if PDF exists
    pdf = db.query(PDFDocument).filter(
        PDFDocument.id == pdf_id,
        PDFDocument.user_id == current_user["user_id"]
    ).first()
    
    if not pdf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF not found"
        )
    
    # Get latest report
    report = db.query(AnalysisReport).filter(
        AnalysisReport.pdf_id == pdf_id
    ).order_by(AnalysisReport.generated_at.desc()).first()
    
    # Get issues
    issues = db.query(AccessibilityIssue).filter(
        AccessibilityIssue.pdf_id == pdf_id
    ).all()
    
    return {
        "pdf_id": pdf_id,
        "status": pdf.processing_status,
        "report": report,
        "issues": issues
    }


@router.get("/{pdf_id}/issues", response_model=List[IssueResponse])
async def get_issues(
    pdf_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    severity: str | None = None
):
    """Get accessibility issues for a PDF"""
    # Check if PDF exists
    pdf = db.query(PDFDocument).filter(
        PDFDocument.id == pdf_id,
        PDFDocument.user_id == current_user["user_id"]
    ).first()
    
    if not pdf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF not found"
        )
    
    # Query issues
    query = db.query(AccessibilityIssue).filter(AccessibilityIssue.pdf_id == pdf_id)
    
    if severity:
        query = query.filter(AccessibilityIssue.severity == severity)
    
    issues = query.all()
    
    return issues
