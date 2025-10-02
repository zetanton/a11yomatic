"""Reporting endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel
import logging
import json

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.pdf import PDFDocument, AnalysisReport, AccessibilityIssue

router = APIRouter()
logger = logging.getLogger(__name__)


class ReportSummary(BaseModel):
    pdf_id: str
    filename: str
    overall_score: int
    total_issues: int
    critical_issues: int
    high_issues: int
    medium_issues: int
    low_issues: int
    generated_at: str
    
    class Config:
        from_attributes = True


@router.get("/{pdf_id}", response_model=ReportSummary)
async def get_report(
    pdf_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get accessibility report for a PDF"""
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
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No analysis report found. Please analyze the PDF first."
        )
    
    return {
        "pdf_id": pdf_id,
        "filename": pdf.filename,
        "overall_score": report.overall_score,
        "total_issues": report.total_issues,
        "critical_issues": report.critical_issues,
        "high_issues": report.high_issues,
        "medium_issues": report.medium_issues,
        "low_issues": report.low_issues,
        "generated_at": str(report.generated_at),
    }


@router.get("/{pdf_id}/export/json")
async def export_report_json(
    pdf_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Export report as JSON"""
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
    
    # Get report and issues
    report = db.query(AnalysisReport).filter(
        AnalysisReport.pdf_id == pdf_id
    ).order_by(AnalysisReport.generated_at.desc()).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No analysis report found"
        )
    
    issues = db.query(AccessibilityIssue).filter(
        AccessibilityIssue.pdf_id == pdf_id
    ).all()
    
    # Build export data
    export_data = {
        "pdf": {
            "id": pdf.id,
            "filename": pdf.filename,
            "upload_date": str(pdf.upload_date),
        },
        "report": {
            "overall_score": report.overall_score,
            "total_issues": report.total_issues,
            "critical_issues": report.critical_issues,
            "high_issues": report.high_issues,
            "medium_issues": report.medium_issues,
            "low_issues": report.low_issues,
            "generated_at": str(report.generated_at),
        },
        "issues": [
            {
                "type": issue.issue_type,
                "severity": issue.severity,
                "page": issue.page_number,
                "description": issue.description,
                "wcag_criteria": issue.wcag_criteria,
            }
            for issue in issues
        ]
    }
    
    # Return JSON response
    return Response(
        content=json.dumps(export_data, indent=2),
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename={pdf.filename}_report.json"
        }
    )


@router.get("/analytics", response_model=Dict[str, Any])
async def get_analytics(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get analytics data for user's PDFs"""
    # Get all user's PDFs
    pdfs = db.query(PDFDocument).filter(
        PDFDocument.user_id == current_user["user_id"]
    ).all()
    
    # Get all reports
    pdf_ids = [pdf.id for pdf in pdfs]
    reports = db.query(AnalysisReport).filter(
        AnalysisReport.pdf_id.in_(pdf_ids)
    ).all()
    
    # Calculate analytics
    total_pdfs = len(pdfs)
    total_issues = sum(report.total_issues for report in reports)
    avg_score = sum(report.overall_score for report in reports) / len(reports) if reports else 0
    
    # Issue breakdown
    issue_breakdown = {
        "critical": sum(report.critical_issues for report in reports),
        "high": sum(report.high_issues for report in reports),
        "medium": sum(report.medium_issues for report in reports),
        "low": sum(report.low_issues for report in reports),
    }
    
    return {
        "total_pdfs": total_pdfs,
        "total_issues": total_issues,
        "average_score": round(avg_score, 2),
        "issue_breakdown": issue_breakdown,
    }


