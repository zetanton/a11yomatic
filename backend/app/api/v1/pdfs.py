"""PDF management endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from pathlib import Path
import shutil
import logging

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models.pdf import PDFDocument
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)


class PDFResponse(BaseModel):
    id: str
    filename: str
    file_size: int
    upload_date: datetime
    processing_status: str
    
    class Config:
        from_attributes = True


@router.post("/upload", response_model=PDFResponse, status_code=status.HTTP_201_CREATED)
async def upload_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Upload a PDF file for analysis"""
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
    
    # Validate file size
    file_size = 0
    content = await file.read()
    file_size = len(content)
    
    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE} bytes"
        )
    
    # Save file
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Create PDF document record
    pdf_doc = PDFDocument(
        user_id=current_user["user_id"],
        filename=file.filename,
        file_path="",  # Will be set after saving
        file_size=file_size,
        processing_status="pending"
    )
    
    db.add(pdf_doc)
    db.commit()
    db.refresh(pdf_doc)
    
    # Save file with PDF ID as name
    file_path = upload_dir / f"{pdf_doc.id}.pdf"
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Update file path
    pdf_doc.file_path = str(file_path)
    db.commit()
    db.refresh(pdf_doc)
    
    logger.info(f"PDF uploaded: {pdf_doc.id} - {file.filename}")
    
    return pdf_doc


@router.get("/", response_model=List[PDFResponse])
async def list_pdfs(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    """List user's PDF documents"""
    pdfs = db.query(PDFDocument).filter(
        PDFDocument.user_id == current_user["user_id"]
    ).offset(skip).limit(limit).all()
    
    return pdfs


@router.get("/{pdf_id}", response_model=PDFResponse)
async def get_pdf(
    pdf_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get PDF document details"""
    pdf = db.query(PDFDocument).filter(
        PDFDocument.id == pdf_id,
        PDFDocument.user_id == current_user["user_id"]
    ).first()
    
    if not pdf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF not found"
        )
    
    return pdf


@router.delete("/{pdf_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pdf(
    pdf_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a PDF document"""
    pdf = db.query(PDFDocument).filter(
        PDFDocument.id == pdf_id,
        PDFDocument.user_id == current_user["user_id"]
    ).first()
    
    if not pdf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF not found"
        )
    
    # Delete file
    try:
        Path(pdf.file_path).unlink(missing_ok=True)
    except Exception as e:
        logger.error(f"Error deleting file: {str(e)}")
    
    # Delete database record
    db.delete(pdf)
    db.commit()
    
    logger.info(f"PDF deleted: {pdf_id}")
    
    return None


