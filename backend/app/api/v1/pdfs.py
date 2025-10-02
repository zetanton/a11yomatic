"""PDF management endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
import os
import shutil
from pathlib import Path
import structlog
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models.pdf import PDFDocument
from app.services.pdf_processor import pdf_processor

logger = structlog.get_logger()
router = APIRouter()


# Response models
class PDFResponse(BaseModel):
    id: str
    filename: str
    file_size: int
    page_count: int | None
    upload_date: str
    processing_status: str
    
    class Config:
        from_attributes = True


class PDFListResponse(BaseModel):
    total: int
    pdfs: List[PDFResponse]


@router.post("/upload", response_model=PDFResponse, status_code=status.HTTP_201_CREATED)
async def upload_pdf(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Upload a PDF file for accessibility analysis"""
    
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
    
    # Check file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum limit of {settings.MAX_FILE_SIZE} bytes"
        )
    
    # Create upload directory if it doesn't exist
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    import uuid
    file_id = str(uuid.uuid4())
    file_path = upload_dir / f"{file_id}_{file.filename}"
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        logger.error("Failed to save uploaded file", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save file"
        )
    
    # Validate PDF
    is_valid = await pdf_processor.validate_pdf(str(file_path))
    if not is_valid:
        os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid PDF file"
        )
    
    # Extract basic metadata
    metadata = await pdf_processor.extract_metadata(str(file_path))
    
    # Create database record
    pdf_doc = PDFDocument(
        id=file_id,
        user_id=current_user["user_id"],
        filename=file.filename,
        file_path=str(file_path),
        file_size=file_size,
        page_count=metadata.get("page_count"),
        processing_status="uploaded",
        metadata=metadata
    )
    
    db.add(pdf_doc)
    db.commit()
    db.refresh(pdf_doc)
    
    logger.info(
        "PDF uploaded",
        pdf_id=pdf_doc.id,
        filename=file.filename,
        file_size=file_size
    )
    
    return PDFResponse(
        id=pdf_doc.id,
        filename=pdf_doc.filename,
        file_size=pdf_doc.file_size,
        page_count=pdf_doc.page_count,
        upload_date=pdf_doc.upload_date.isoformat(),
        processing_status=pdf_doc.processing_status
    )


@router.get("", response_model=PDFListResponse)
async def list_pdfs(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List user's uploaded PDFs"""
    
    # Get total count
    total = db.query(PDFDocument).filter(
        PDFDocument.user_id == current_user["user_id"]
    ).count()
    
    # Get PDFs
    pdfs = db.query(PDFDocument).filter(
        PDFDocument.user_id == current_user["user_id"]
    ).order_by(PDFDocument.upload_date.desc()).offset(skip).limit(limit).all()
    
    return PDFListResponse(
        total=total,
        pdfs=[
            PDFResponse(
                id=pdf.id,
                filename=pdf.filename,
                file_size=pdf.file_size,
                page_count=pdf.page_count,
                upload_date=pdf.upload_date.isoformat(),
                processing_status=pdf.processing_status
            )
            for pdf in pdfs
        ]
    )


@router.get("/{pdf_id}", response_model=PDFResponse)
async def get_pdf(
    pdf_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get PDF details"""
    
    pdf = db.query(PDFDocument).filter(
        PDFDocument.id == pdf_id,
        PDFDocument.user_id == current_user["user_id"]
    ).first()
    
    if not pdf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF not found"
        )
    
    return PDFResponse(
        id=pdf.id,
        filename=pdf.filename,
        file_size=pdf.file_size,
        page_count=pdf.page_count,
        upload_date=pdf.upload_date.isoformat(),
        processing_status=pdf.processing_status
    )


@router.delete("/{pdf_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pdf(
    pdf_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a PDF"""
    
    pdf = db.query(PDFDocument).filter(
        PDFDocument.id == pdf_id,
        PDFDocument.user_id == current_user["user_id"]
    ).first()
    
    if not pdf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF not found"
        )
    
    # Delete file from storage
    try:
        if os.path.exists(pdf.file_path):
            os.remove(pdf.file_path)
    except Exception as e:
        logger.error("Failed to delete PDF file", error=str(e))
    
    # Delete from database (cascades to issues, reports, etc.)
    db.delete(pdf)
    db.commit()
    
    logger.info("PDF deleted", pdf_id=pdf_id)
    
    return None
