"""Remediation endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
import logging

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.pdf import AccessibilityIssue, RemediationPlan, PDFDocument
from app.services.ai_service import AIService

router = APIRouter()
logger = logging.getLogger(__name__)


class RemediationResponse(BaseModel):
    id: str
    issue_id: str
    ai_generated_content: str | None
    user_approved: bool
    implementation_status: str
    
    class Config:
        from_attributes = True


class RemediationRequest(BaseModel):
    approved: bool = False


@router.post("/{issue_id}", response_model=RemediationResponse, status_code=status.HTTP_201_CREATED)
async def generate_remediation(
    issue_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Generate AI-powered remediation suggestion for an issue"""
    # Get issue
    issue = db.query(AccessibilityIssue).filter(
        AccessibilityIssue.id == issue_id
    ).first()
    
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )
    
    # Verify user owns the PDF
    pdf = db.query(PDFDocument).filter(
        PDFDocument.id == issue.pdf_id,
        PDFDocument.user_id == current_user["user_id"]
    ).first()
    
    if not pdf:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Check if remediation already exists
    existing = db.query(RemediationPlan).filter(
        RemediationPlan.issue_id == issue_id
    ).first()
    
    if existing:
        return existing
    
    # Generate remediation suggestion
    ai_service = AIService()
    
    issue_data = {
        "type": issue.issue_type,
        "severity": issue.severity,
        "description": issue.description,
        "wcag_criteria": issue.wcag_criteria
    }
    
    suggestion = await ai_service.generate_remediation_suggestion(issue_data)
    
    # Create remediation plan
    remediation = RemediationPlan(
        issue_id=issue_id,
        ai_generated_content=suggestion,
        user_approved=False,
        implementation_status="pending"
    )
    
    db.add(remediation)
    db.commit()
    db.refresh(remediation)
    
    logger.info(f"Remediation generated for issue: {issue_id}")
    
    return remediation


@router.get("/{issue_id}", response_model=RemediationResponse)
async def get_remediation(
    issue_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get remediation plan for an issue"""
    # Get remediation
    remediation = db.query(RemediationPlan).filter(
        RemediationPlan.issue_id == issue_id
    ).first()
    
    if not remediation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Remediation not found"
        )
    
    # Verify access
    issue = db.query(AccessibilityIssue).filter(
        AccessibilityIssue.id == issue_id
    ).first()
    
    pdf = db.query(PDFDocument).filter(
        PDFDocument.id == issue.pdf_id,
        PDFDocument.user_id == current_user["user_id"]
    ).first()
    
    if not pdf:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return remediation


@router.put("/{issue_id}/approve", response_model=RemediationResponse)
async def approve_remediation(
    issue_id: str,
    request: RemediationRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Approve or reject a remediation suggestion"""
    # Get remediation
    remediation = db.query(RemediationPlan).filter(
        RemediationPlan.issue_id == issue_id
    ).first()
    
    if not remediation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Remediation not found"
        )
    
    # Update approval status
    remediation.user_approved = request.approved
    remediation.implementation_status = "approved" if request.approved else "rejected"
    
    db.commit()
    db.refresh(remediation)
    
    logger.info(f"Remediation {'approved' if request.approved else 'rejected'}: {issue_id}")
    
    return remediation


@router.post("/bulk/{pdf_id}", status_code=status.HTTP_200_OK)
async def bulk_remediate_pdf(
    pdf_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Generate and approve remediations for ALL issues in a PDF"""
    # Verify user owns the PDF
    pdf = db.query(PDFDocument).filter(
        PDFDocument.id == pdf_id,
        PDFDocument.user_id == current_user["user_id"]
    ).first()
    
    if not pdf:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Get all issues for this PDF
    issues = db.query(AccessibilityIssue).filter(
        AccessibilityIssue.pdf_id == pdf_id
    ).all()
    
    if not issues:
        return {"message": "No issues found", "count": 0}
    
    ai_service = AIService()
    fixed_count = 0
    
    for issue in issues:
        try:
            # Check if remediation already exists
            existing = db.query(RemediationPlan).filter(
                RemediationPlan.issue_id == issue.id
            ).first()
            
            if existing:
                # Just approve it if not already approved
                if not existing.user_approved:
                    existing.user_approved = True
                    existing.implementation_status = "approved"
                    fixed_count += 1
            else:
                # Generate remediation
                issue_data = {
                    "type": issue.issue_type,
                    "severity": issue.severity,
                    "description": issue.description,
                    "wcag_criteria": issue.wcag_criteria
                }
                
                suggestion = await ai_service.generate_remediation_suggestion(issue_data)
                
                # Create and approve remediation
                remediation = RemediationPlan(
                    issue_id=issue.id,
                    ai_generated_content=suggestion,
                    user_approved=True,
                    implementation_status="approved"
                )
                
                db.add(remediation)
                fixed_count += 1
        
        except Exception as e:
            logger.error(f"Error creating remediation for issue {issue.id}: {str(e)}")
            continue
    
    db.commit()
    
    logger.info(f"Bulk remediation completed for PDF {pdf_id}: {fixed_count} issues")
    
    return {
        "message": f"Successfully created {fixed_count} remediations",
        "count": fixed_count,
        "total_issues": len(issues)
    }


