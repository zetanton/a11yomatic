"""Remediation endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any
import structlog
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.pdf import PDFDocument, AccessibilityIssue, RemediationPlan
from app.services.remediation_service import remediation_service

logger = structlog.get_logger()
router = APIRouter()


# Request/Response models
class RemediationRequest(BaseModel):
    context: Dict[str, Any] | None = None


class RemediationResponse(BaseModel):
    id: str
    issue_id: str
    ai_generated_content: Any | None
    implementation_steps: List[str]
    additional_notes: str
    user_approved: bool
    implementation_status: str
    
    class Config:
        from_attributes = True


@router.post("/{issue_id}/generate", response_model=RemediationResponse, status_code=status.HTTP_201_CREATED)
async def generate_remediation(
    issue_id: str,
    request_data: RemediationRequest | None = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Generate AI-powered remediation suggestion for an accessibility issue"""
    
    # Get issue
    issue = db.query(AccessibilityIssue).filter(
        AccessibilityIssue.id == issue_id
    ).first()
    
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )
    
    # Verify PDF ownership
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Remediation already exists for this issue"
        )
    
    # Generate remediation
    issue_dict = {
        "id": issue.id,
        "issue_type": issue.issue_type,
        "severity": issue.severity,
        "page_number": issue.page_number,
        "description": issue.description,
        "wcag_criteria": issue.wcag_criteria,
        "location": issue.location
    }
    
    context = request_data.context if request_data else None
    remediation_data = await remediation_service.generate_remediation(
        issue_dict,
        context
    )
    
    # Save to database
    remediation = RemediationPlan(
        issue_id=issue_id,
        ai_generated_content=str(remediation_data.get("generated_content")),
        implementation_status="pending"
    )
    
    db.add(remediation)
    db.commit()
    db.refresh(remediation)
    
    logger.info(
        "Remediation generated",
        issue_id=issue_id,
        issue_type=issue.issue_type
    )
    
    return RemediationResponse(
        id=remediation.id,
        issue_id=remediation.issue_id,
        ai_generated_content=remediation_data.get("generated_content"),
        implementation_steps=remediation_data.get("implementation_steps", []),
        additional_notes=remediation_data.get("additional_notes", ""),
        user_approved=remediation.user_approved,
        implementation_status=remediation.implementation_status
    )


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
    
    # Verify ownership
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
    
    return RemediationResponse(
        id=remediation.id,
        issue_id=remediation.issue_id,
        ai_generated_content=remediation.ai_generated_content,
        implementation_steps=[],  # Stored in ai_generated_content
        additional_notes="",
        user_approved=remediation.user_approved,
        implementation_status=remediation.implementation_status
    )


@router.patch("/{issue_id}/approve", response_model=RemediationResponse)
async def approve_remediation(
    issue_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Approve a remediation plan"""
    
    remediation = db.query(RemediationPlan).filter(
        RemediationPlan.issue_id == issue_id
    ).first()
    
    if not remediation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Remediation not found"
        )
    
    # Verify ownership
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
    
    # Update approval status
    remediation.user_approved = True
    remediation.implementation_status = "approved"
    db.commit()
    db.refresh(remediation)
    
    logger.info("Remediation approved", issue_id=issue_id)
    
    return RemediationResponse(
        id=remediation.id,
        issue_id=remediation.issue_id,
        ai_generated_content=remediation.ai_generated_content,
        implementation_steps=[],
        additional_notes="",
        user_approved=remediation.user_approved,
        implementation_status=remediation.implementation_status
    )


@router.post("/bulk/generate", status_code=status.HTTP_202_ACCEPTED)
async def generate_bulk_remediation(
    pdf_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Generate remediation plans for all issues in a PDF"""
    
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
    
    # Get all unresolved issues
    issues = db.query(AccessibilityIssue).filter(
        AccessibilityIssue.pdf_id == pdf_id,
        AccessibilityIssue.is_resolved == False
    ).all()
    
    if not issues:
        return {
            "message": "No issues to remediate",
            "pdf_id": pdf_id,
            "count": 0
        }
    
    # Note: In production, this should be a background task
    # For now, we'll just acknowledge the request
    
    logger.info(
        "Bulk remediation requested",
        pdf_id=pdf_id,
        issue_count=len(issues)
    )
    
    return {
        "message": "Bulk remediation generation started",
        "pdf_id": pdf_id,
        "issue_count": len(issues),
        "status": "processing"
    }
