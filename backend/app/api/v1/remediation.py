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


