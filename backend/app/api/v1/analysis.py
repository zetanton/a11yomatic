"""Accessibility analysis endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any
import structlog
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.pdf import PDFDocument, AccessibilityIssue, AnalysisReport
from app.services.pdf_processor import pdf_processor

logger = structlog.get_logger()
router = APIRouter()


# Response models
class IssueResponse(BaseModel):
    id: str
    issue_type: str
    severity: str
    page_number: int | None
    description: str
    wcag_criteria: str | None
    is_resolved: bool
    
    class Config:
        from_attributes = True


class AnalysisResultResponse(BaseModel):
    pdf_id: str
    overall_score: int
    total_issues: int
    critical_issues: int
    high_issues: int
    medium_issues: int
    low_issues: int
    wcag_compliance_level: str
    issues: List[IssueResponse]


async def analyze_pdf_task(pdf_id: str, db: Session):
    """Background task to analyze PDF"""
    try:
        # Get PDF document
        pdf = db.query(PDFDocument).filter(PDFDocument.id == pdf_id).first()
        if not pdf:
            logger.error("PDF not found for analysis", pdf_id=pdf_id)
            return
        
        # Update status
        pdf.processing_status = "analyzing"
        db.commit()
        
        # Run analysis
        analysis_result = await pdf_processor.analyze_pdf(pdf.file_path)
        
        # Save issues to database
        for issue_data in analysis_result.get("issues", []):
            issue = AccessibilityIssue(
                pdf_id=pdf_id,
                issue_type=issue_data["issue_type"],
                severity=issue_data["severity"],
                page_number=issue_data.get("page_number"),
                description=issue_data["description"],
                wcag_criteria=issue_data.get("wcag_criteria"),
                location=issue_data.get("location")
            )
            db.add(issue)
        
        # Create analysis report
        report = AnalysisReport(
            pdf_id=pdf_id,
            overall_score=analysis_result["overall_score"],
            total_issues=analysis_result["total_issues"],
            critical_issues=analysis_result["critical_issues"],
            high_issues=analysis_result["high_issues"],
            medium_issues=analysis_result["medium_issues"],
            low_issues=analysis_result["low_issues"],
            wcag_compliance_level=analysis_result["wcag_compliance_level"],
            report_data=analysis_result
        )
        db.add(report)
        
        # Update PDF status
        pdf.processing_status = "completed"
        db.commit()
        
        logger.info(
            "PDF analysis completed",
            pdf_id=pdf_id,
            total_issues=analysis_result["total_issues"],
            score=analysis_result["overall_score"]
        )
        
    except Exception as e:
        logger.error("PDF analysis failed", pdf_id=pdf_id, error=str(e))
        pdf = db.query(PDFDocument).filter(PDFDocument.id == pdf_id).first()
        if pdf:
            pdf.processing_status = "failed"
            db.commit()


@router.post("/{pdf_id}/analyze", status_code=status.HTTP_202_ACCEPTED)
async def start_analysis(
    pdf_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Start accessibility analysis for a PDF"""
    
    # Verify PDF ownership
    pdf = db.query(PDFDocument).filter(
        PDFDocument.id == pdf_id,
        PDFDocument.user_id == current_user["user_id"]
    ).first()
    
    if not pdf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF not found"
        )
    
    if pdf.processing_status == "analyzing":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Analysis already in progress"
        )
    
    # Start analysis in background
    background_tasks.add_task(analyze_pdf_task, pdf_id, db)
    
    logger.info("Analysis started", pdf_id=pdf_id)
    
    return {
        "message": "Analysis started",
        "pdf_id": pdf_id,
        "status": "processing"
    }


@router.get("/{pdf_id}", response_model=AnalysisResultResponse)
async def get_analysis(
    pdf_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get analysis results for a PDF"""
    
    # Verify PDF ownership
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
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No analysis report found. Please run analysis first."
        )
    
    # Get issues
    issues = db.query(AccessibilityIssue).filter(
        AccessibilityIssue.pdf_id == pdf_id
    ).all()
    
    return AnalysisResultResponse(
        pdf_id=pdf_id,
        overall_score=report.overall_score,
        total_issues=report.total_issues,
        critical_issues=report.critical_issues,
        high_issues=report.high_issues,
        medium_issues=report.medium_issues,
        low_issues=report.low_issues,
        wcag_compliance_level=report.wcag_compliance_level,
        issues=[
            IssueResponse(
                id=issue.id,
                issue_type=issue.issue_type,
                severity=issue.severity,
                page_number=issue.page_number,
                description=issue.description,
                wcag_criteria=issue.wcag_criteria,
                is_resolved=issue.is_resolved
            )
            for issue in issues
        ]
    )


@router.get("/{pdf_id}/issues", response_model=List[IssueResponse])
async def get_issues(
    pdf_id: str,
    severity: str | None = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get accessibility issues for a PDF"""
    
    # Verify PDF ownership
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
    
    return [
        IssueResponse(
            id=issue.id,
            issue_type=issue.issue_type,
            severity=issue.severity,
            page_number=issue.page_number,
            description=issue.description,
            wcag_criteria=issue.wcag_criteria,
            is_resolved=issue.is_resolved
        )
        for issue in issues
    ]
