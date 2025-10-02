"""Reporting endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime
import structlog
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.pdf import PDFDocument, AnalysisReport, AccessibilityIssue

logger = structlog.get_logger()
router = APIRouter()


# Response models
class ReportResponse(BaseModel):
    id: str
    pdf_id: str
    pdf_filename: str
    overall_score: int
    total_issues: int
    critical_issues: int
    high_issues: int
    medium_issues: int
    low_issues: int
    wcag_compliance_level: str
    generated_at: str
    
    class Config:
        from_attributes = True


class AnalyticsResponse(BaseModel):
    total_pdfs: int
    total_issues: int
    average_score: float
    compliance_distribution: Dict[str, int]
    severity_distribution: Dict[str, int]


@router.get("/{pdf_id}", response_model=ReportResponse)
async def get_report(
    pdf_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get detailed accessibility report for a PDF"""
    
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
            detail="No report found for this PDF"
        )
    
    return ReportResponse(
        id=report.id,
        pdf_id=report.pdf_id,
        pdf_filename=pdf.filename,
        overall_score=report.overall_score,
        total_issues=report.total_issues,
        critical_issues=report.critical_issues,
        high_issues=report.high_issues,
        medium_issues=report.medium_issues,
        low_issues=report.low_issues,
        wcag_compliance_level=report.wcag_compliance_level,
        generated_at=report.generated_at.isoformat()
    )


@router.get("/analytics/summary", response_model=AnalyticsResponse)
async def get_analytics(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get analytics summary for user's PDFs"""
    
    # Get user's PDFs
    pdfs = db.query(PDFDocument).filter(
        PDFDocument.user_id == current_user["user_id"]
    ).all()
    
    pdf_ids = [pdf.id for pdf in pdfs]
    
    # Get reports
    reports = db.query(AnalysisReport).filter(
        AnalysisReport.pdf_id.in_(pdf_ids)
    ).all()
    
    # Get issues
    issues = db.query(AccessibilityIssue).filter(
        AccessibilityIssue.pdf_id.in_(pdf_ids)
    ).all()
    
    # Calculate metrics
    total_pdfs = len(pdfs)
    total_issues = len(issues)
    average_score = sum(r.overall_score for r in reports) / len(reports) if reports else 0
    
    # Compliance distribution
    compliance_dist = {}
    for report in reports:
        level = report.wcag_compliance_level
        compliance_dist[level] = compliance_dist.get(level, 0) + 1
    
    # Severity distribution
    severity_dist = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0
    }
    for issue in issues:
        if issue.severity in severity_dist:
            severity_dist[issue.severity] += 1
    
    return AnalyticsResponse(
        total_pdfs=total_pdfs,
        total_issues=total_issues,
        average_score=round(average_score, 2),
        compliance_distribution=compliance_dist,
        severity_distribution=severity_dist
    )


@router.post("/{pdf_id}/export")
async def export_report(
    pdf_id: str,
    format: str = "json",  # json, csv, pdf
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Export accessibility report"""
    
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
    
    # Get report and issues
    report = db.query(AnalysisReport).filter(
        AnalysisReport.pdf_id == pdf_id
    ).order_by(AnalysisReport.generated_at.desc()).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No report found"
        )
    
    issues = db.query(AccessibilityIssue).filter(
        AccessibilityIssue.pdf_id == pdf_id
    ).all()
    
    # For now, return JSON format
    # In production, implement CSV and PDF export
    export_data = {
        "pdf_filename": pdf.filename,
        "report_date": report.generated_at.isoformat(),
        "overall_score": report.overall_score,
        "wcag_compliance_level": report.wcag_compliance_level,
        "summary": {
            "total_issues": report.total_issues,
            "critical": report.critical_issues,
            "high": report.high_issues,
            "medium": report.medium_issues,
            "low": report.low_issues
        },
        "issues": [
            {
                "type": issue.issue_type,
                "severity": issue.severity,
                "page": issue.page_number,
                "description": issue.description,
                "wcag_criteria": issue.wcag_criteria
            }
            for issue in issues
        ]
    }
    
    logger.info("Report exported", pdf_id=pdf_id, format=format)
    
    return export_data
