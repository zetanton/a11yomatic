"""Remediation endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
import logging
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.pdf import AccessibilityIssue, RemediationPlan, PDFDocument
from app.services.ai_service import AIService
from app.services.pdf_fixer import PDFFixer

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


class BulkRemediationRequest(BaseModel):
    pdf_ids: Optional[List[str]] = None  # If None, process all user PDFs
    issue_types: Optional[List[str]] = None  # Filter by issue types
    severities: Optional[List[str]] = None  # Filter by severities


class BulkApprovalRequest(BaseModel):
    remediation_ids: List[str]
    approved: bool = True


class BulkRemediationResponse(BaseModel):
    total_processed: int
    successful: int
    failed: int
    remediation_ids: List[str]


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


@router.post("/bulk/generate", response_model=BulkRemediationResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_bulk_remediations(
    request: BulkRemediationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Generate AI-powered remediation suggestions for multiple issues"""
    
    # Build query for issues
    query = db.query(AccessibilityIssue).join(PDFDocument).filter(
        PDFDocument.user_id == current_user["user_id"]
    )
    
    # Filter by PDF IDs if provided
    if request.pdf_ids:
        query = query.filter(AccessibilityIssue.pdf_id.in_(request.pdf_ids))
    
    # Filter by issue types if provided
    if request.issue_types:
        query = query.filter(AccessibilityIssue.issue_type.in_(request.issue_types))
    
    # Filter by severities if provided
    if request.severities:
        query = query.filter(AccessibilityIssue.severity.in_(request.severities))
    
    # Exclude issues that already have remediations
    existing_remediations = db.query(RemediationPlan.issue_id).subquery()
    query = query.filter(~AccessibilityIssue.id.in_(existing_remediations))
    
    issues = query.all()
    
    if not issues:
        return BulkRemediationResponse(
            total_processed=0,
            successful=0,
            failed=0,
            remediation_ids=[]
        )
    
    # Start background task for bulk generation
    background_tasks.add_task(
        process_bulk_remediations,
        [issue.id for issue in issues],
        current_user["user_id"]
    )
    
    logger.info(f"Started bulk remediation generation for {len(issues)} issues")
    
    return BulkRemediationResponse(
        total_processed=len(issues),
        successful=0,  # Will be updated by background task
        failed=0,      # Will be updated by background task
        remediation_ids=[]
    )


async def process_bulk_remediations(issue_ids: List[str], user_id: str):
    """Background task to process bulk remediation generation"""
    from app.core.database import SessionLocal
    
    db = SessionLocal()
    ai_service = AIService()
    
    successful = 0
    failed = 0
    remediation_ids = []
    
    try:
        for issue_id in issue_ids:
            try:
                # Get issue
                issue = db.query(AccessibilityIssue).filter(
                    AccessibilityIssue.id == issue_id
                ).first()
                
                if not issue:
                    failed += 1
                    continue
                
                # Verify user owns the PDF
                pdf = db.query(PDFDocument).filter(
                    PDFDocument.id == issue.pdf_id,
                    PDFDocument.user_id == user_id
                ).first()
                
                if not pdf:
                    failed += 1
                    continue
                
                # Check if remediation already exists
                existing = db.query(RemediationPlan).filter(
                    RemediationPlan.issue_id == issue_id
                ).first()
                
                if existing:
                    remediation_ids.append(existing.id)
                    successful += 1
                    continue
                
                # Generate remediation suggestion
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
                
                remediation_ids.append(remediation.id)
                successful += 1
                
            except Exception as e:
                logger.error(f"Error generating remediation for issue {issue_id}: {str(e)}")
                failed += 1
                
    finally:
        db.close()
    
    logger.info(f"Bulk remediation generation completed: {successful} successful, {failed} failed")


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
    remediation.implementation_status = "pending_implementation" if request.approved else "rejected"
    
    db.commit()
    db.refresh(remediation)
    
    logger.info(f"Remediation {'approved' if request.approved else 'rejected'}: {issue_id}")
    
    return remediation


@router.put("/bulk/approve", response_model=BulkRemediationResponse)
async def approve_bulk_remediations(
    request: BulkApprovalRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Approve or reject multiple remediation suggestions"""
    
    # Get all remediations and verify user access
    remediations = db.query(RemediationPlan).join(AccessibilityIssue).join(PDFDocument).filter(
        RemediationPlan.id.in_(request.remediation_ids),
        PDFDocument.user_id == current_user["user_id"]
    ).all()
    
    if not remediations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No remediations found or access denied"
        )
    
    # Start background task for bulk approval and implementation
    background_tasks.add_task(
        process_bulk_approvals,
        [remediation.id for remediation in remediations],
        request.approved,
        current_user["user_id"]
    )
    
    logger.info(f"Started bulk approval for {len(remediations)} remediations")
    
    return BulkRemediationResponse(
        total_processed=len(remediations),
        successful=0,  # Will be updated by background task
        failed=0,      # Will be updated by background task
        remediation_ids=[r.id for r in remediations]
    )


async def process_bulk_approvals(remediation_ids: List[str], approved: bool, user_id: str):
    """Background task to process bulk approvals and implementations"""
    from app.core.database import SessionLocal
    
    db = SessionLocal()
    successful = 0
    failed = 0
    
    try:
        for remediation_id in remediation_ids:
            try:
                # Get remediation
                remediation = db.query(RemediationPlan).filter(
                    RemediationPlan.id == remediation_id
                ).first()
                
                if not remediation:
                    failed += 1
                    continue
                
                # Update approval status
                remediation.user_approved = approved
                remediation.implementation_status = "approved" if approved else "rejected"
                
                # If approved, mark for implementation
                if approved:
                    remediation.implementation_status = "pending_implementation"
                
                db.commit()
                successful += 1
                
            except Exception as e:
                logger.error(f"Error approving remediation {remediation_id}: {str(e)}")
                failed += 1
                
    finally:
        db.close()
    
    logger.info(f"Bulk approval completed: {successful} successful, {failed} failed")


@router.get("/bulk/status")
async def get_bulk_status(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get status of all remediations for user's PDFs"""
    
    # Get all remediations for user's PDFs
    remediations = db.query(RemediationPlan).join(AccessibilityIssue).join(PDFDocument).filter(
        PDFDocument.user_id == current_user["user_id"]
    ).all()
    
    status_counts = {
        "pending": 0,
        "approved": 0,
        "rejected": 0,
        "pending_implementation": 0,
        "implemented": 0
    }
    
    for remediation in remediations:
        status = remediation.implementation_status or "pending"
        if status in status_counts:
            status_counts[status] += 1
    
    return {
        "total_remediations": len(remediations),
        "status_breakdown": status_counts
    }


@router.post("/bulk/implement", response_model=BulkRemediationResponse, status_code=status.HTTP_202_ACCEPTED)
async def implement_bulk_remediations(
    request: BulkRemediationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Implement approved remediations for multiple PDFs"""
    
    # Get approved remediations for user's PDFs
    query = db.query(RemediationPlan).join(AccessibilityIssue).join(PDFDocument).filter(
        PDFDocument.user_id == current_user["user_id"],
        RemediationPlan.user_approved == True,
        RemediationPlan.implementation_status == "pending_implementation"
    )
    
    # Filter by PDF IDs if provided
    if request.pdf_ids:
        query = query.filter(AccessibilityIssue.pdf_id.in_(request.pdf_ids))
    
    # Filter by issue types if provided
    if request.issue_types:
        query = query.filter(AccessibilityIssue.issue_type.in_(request.issue_types))
    
    # Filter by severities if provided
    if request.severities:
        query = query.filter(AccessibilityIssue.severity.in_(request.severities))
    
    remediations = query.all()
    
    if not remediations:
        return BulkRemediationResponse(
            total_processed=0,
            successful=0,
            failed=0,
            remediation_ids=[]
        )
    
    # Start background task for implementation
    background_tasks.add_task(
        process_bulk_implementations,
        [remediation.id for remediation in remediations],
        current_user["user_id"]
    )
    
    logger.info(f"Started bulk implementation for {len(remediations)} remediations")
    
    return BulkRemediationResponse(
        total_processed=len(remediations),
        successful=0,  # Will be updated by background task
        failed=0,      # Will be updated by background task
        remediation_ids=[r.id for r in remediations]
    )


async def process_bulk_implementations(remediation_ids: List[str], user_id: str):
    """Background task to implement approved remediations"""
    from app.core.database import SessionLocal
    
    db = SessionLocal()
    pdf_fixer = PDFFixer()
    successful = 0
    failed = 0
    
    try:
        # Group remediations by PDF
        pdf_remediations = {}
        
        for remediation_id in remediation_ids:
            remediation = db.query(RemediationPlan).filter(
                RemediationPlan.id == remediation_id
            ).first()
            
            if not remediation:
                failed += 1
                continue
            
            issue = db.query(AccessibilityIssue).filter(
                AccessibilityIssue.id == remediation.issue_id
            ).first()
            
            if not issue:
                failed += 1
                continue
            
            pdf_id = issue.pdf_id
            
            if pdf_id not in pdf_remediations:
                pdf_remediations[pdf_id] = []
            
            pdf_remediations[pdf_id].append({
                "remediation_id": remediation_id,
                "issue_type": issue.issue_type,
                "severity": issue.severity,
                "description": issue.description,
                "wcag_criteria": issue.wcag_criteria,
                "ai_content": remediation.ai_generated_content
            })
        
        # Process each PDF
        for pdf_id, remediations in pdf_remediations.items():
            try:
                pdf = db.query(PDFDocument).filter(
                    PDFDocument.id == pdf_id,
                    PDFDocument.user_id == user_id
                ).first()
                
                if not pdf:
                    failed += len(remediations)
                    continue
                
                # Implement fixes for this PDF
                result = await pdf_fixer.implement_bulk_fixes(pdf.file_path, remediations)
                
                if result["success"]:
                    successful += result["successful_fixes"]
                    failed += result["failed_fixes"]
                    
                    # Update remediation statuses
                    for remediation_data in remediations:
                        remediation = db.query(RemediationPlan).filter(
                            RemediationPlan.id == remediation_data["remediation_id"]
                        ).first()
                        
                        if remediation:
                            remediation.implementation_status = "implemented"
                            remediation.updated_at = datetime.utcnow()
                    
                    # Update PDF with fixed version if available
                    if result["fixed_file_path"]:
                        pdf.file_path = result["fixed_file_path"]
                    
                    db.commit()
                else:
                    failed += len(remediations)
                    logger.error(f"Failed to implement fixes for PDF {pdf_id}: {result.get('error')}")
                
            except Exception as e:
                logger.error(f"Error implementing fixes for PDF {pdf_id}: {str(e)}")
                failed += len(remediations)
                
    finally:
        db.close()
    
    logger.info(f"Bulk implementation completed: {successful} successful, {failed} failed")


