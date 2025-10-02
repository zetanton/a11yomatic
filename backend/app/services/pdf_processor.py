"""PDF processing service for accessibility analysis"""
import PyPDF2
import pdfplumber
import fitz  # PyMuPDF
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Service for analyzing PDF accessibility issues"""
    
    def __init__(self):
        self.supported_formats = ['.pdf']
    
    async def analyze_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Comprehensive PDF accessibility analysis
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing analysis results
        """
        logger.info(f"Starting analysis for: {pdf_path}")
        
        issues = []
        metadata = {}
        
        try:
            # Extract metadata
            metadata = await self._extract_metadata(pdf_path)
            
            # Check for basic accessibility issues
            text_issues = await self._check_text_accessibility(pdf_path)
            issues.extend(text_issues)
            
            # Check for table accessibility
            table_issues = await self._check_table_accessibility(pdf_path)
            issues.extend(table_issues)
            
            # Check for image accessibility
            image_issues = await self._check_image_accessibility(pdf_path)
            issues.extend(image_issues)
            
            # Check document structure
            structure_issues = await self._check_document_structure(pdf_path)
            issues.extend(structure_issues)
            
            # Calculate severity counts
            severity_counts = {
                "critical": len([i for i in issues if i["severity"] == "critical"]),
                "high": len([i for i in issues if i["severity"] == "high"]),
                "medium": len([i for i in issues if i["severity"] == "medium"]),
                "low": len([i for i in issues if i["severity"] == "low"]),
            }
            
            # Calculate overall score
            score = self._calculate_accessibility_score(issues, metadata)
            
            return {
                "total_issues": len(issues),
                "critical_issues": severity_counts["critical"],
                "high_issues": severity_counts["high"],
                "medium_issues": severity_counts["medium"],
                "low_issues": severity_counts["low"],
                "issues": issues,
                "overall_score": score,
                "metadata": metadata,
            }
            
        except Exception as e:
            logger.error(f"Error analyzing PDF: {str(e)}")
            raise
    
    async def _extract_metadata(self, pdf_path: str) -> Dict[str, Any]:
        """Extract PDF metadata"""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                metadata = {
                    "pages": len(reader.pages),
                    "title": reader.metadata.get('/Title', '') if reader.metadata else '',
                    "author": reader.metadata.get('/Author', '') if reader.metadata else '',
                    "subject": reader.metadata.get('/Subject', '') if reader.metadata else '',
                }
                return metadata
        except Exception as e:
            logger.warning(f"Could not extract metadata: {str(e)}")
            return {"pages": 0}
    
    async def _check_text_accessibility(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Check for text accessibility issues"""
        issues = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    text = page.extract_text()
                    
                    # Check for missing or minimal text
                    if not text or len(text.strip()) < 10:
                        issues.append({
                            "type": "missing_text",
                            "severity": "critical",
                            "page": page_num,
                            "description": "Page appears to be image-only or has insufficient text content. This may indicate missing OCR or improper text layer.",
                            "wcag_criteria": "1.1.1",
                            "location": {"page": page_num},
                        })
                    
                    # Check for proper reading order (simplified check)
                    if text and len(text) > 100:
                        words = text.split()
                        if len(words) > 50:
                            # Check if text seems to be in proper order (basic heuristic)
                            # This is a simplified check - real implementation would be more sophisticated
                            pass
        
        except Exception as e:
            logger.error(f"Error checking text accessibility: {str(e)}")
        
        return issues
    
    async def _check_table_accessibility(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Check for table accessibility issues"""
        issues = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    tables = page.extract_tables()
                    
                    for table_idx, table in enumerate(tables):
                        if not table or len(table) < 2:
                            continue
                        
                        # Check for table headers
                        if not self._has_table_headers(table):
                            issues.append({
                                "type": "table_headers",
                                "severity": "high",
                                "page": page_num,
                                "description": f"Table {table_idx + 1} is missing proper headers. Tables must have clear header rows for screen reader accessibility.",
                                "wcag_criteria": "1.3.1",
                                "location": {"page": page_num, "table_index": table_idx},
                            })
        
        except Exception as e:
            logger.error(f"Error checking table accessibility: {str(e)}")
        
        return issues
    
    async def _check_image_accessibility(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Check for image accessibility issues"""
        issues = []
        
        try:
            doc = fitz.open(pdf_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                images = page.get_images()
                
                # Check each image for alt text (simplified check)
                for img_index, img in enumerate(images):
                    # In a real implementation, we would check if the image has proper alt text
                    # For now, we flag all images as potentially missing alt text
                    issues.append({
                        "type": "missing_alt_text",
                        "severity": "high",
                        "page": page_num + 1,
                        "description": f"Image {img_index + 1} may be missing alternative text. All images must have descriptive alt text for screen readers.",
                        "wcag_criteria": "1.1.1",
                        "location": {"page": page_num + 1, "image_index": img_index},
                    })
            
            doc.close()
        
        except Exception as e:
            logger.error(f"Error checking image accessibility: {str(e)}")
        
        return issues
    
    async def _check_document_structure(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Check document structure for accessibility"""
        issues = []
        
        try:
            doc = fitz.open(pdf_path)
            
            # Check for document title
            metadata = doc.metadata
            if not metadata.get("title"):
                issues.append({
                    "type": "missing_title",
                    "severity": "medium",
                    "page": None,
                    "description": "Document is missing a title in metadata. Documents should have descriptive titles.",
                    "wcag_criteria": "2.4.2",
                    "location": {"document": "metadata"},
                })
            
            # Check for language specification
            # Note: This is a simplified check
            issues.append({
                "type": "language_specification",
                "severity": "medium",
                "page": None,
                "description": "Verify that document language is properly specified for screen readers.",
                "wcag_criteria": "3.1.1",
                "location": {"document": "metadata"},
            })
            
            doc.close()
        
        except Exception as e:
            logger.error(f"Error checking document structure: {str(e)}")
        
        return issues
    
    def _has_table_headers(self, table: List[List[str]]) -> bool:
        """Check if table has proper headers"""
        if not table or len(table) < 2:
            return False
        
        # Check if first row looks like headers (non-empty cells)
        first_row = table[0]
        return any(cell and cell.strip() for cell in first_row if cell)
    
    def _calculate_accessibility_score(self, issues: List[Dict], metadata: Dict) -> int:
        """
        Calculate overall accessibility score (0-100)
        Higher score = better accessibility
        """
        if not issues:
            return 100
        
        # Weight different severity levels
        weights = {
            "critical": 10,
            "high": 5,
            "medium": 2,
            "low": 1,
        }
        
        # Calculate total penalty
        total_penalty = sum(weights.get(issue["severity"], 1) for issue in issues)
        
        # Calculate score (capped at 0)
        score = max(0, 100 - total_penalty)
        
        return score
    
    async def extract_content(self, pdf_path: str) -> Dict[str, Any]:
        """Extract all content from PDF for AI processing"""
        content = {
            "text": [],
            "images": [],
            "tables": [],
        }
        
        try:
            # Extract text
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        content["text"].append(text)
                    
                    tables = page.extract_tables()
                    if tables:
                        content["tables"].extend(tables)
            
            # Extract images
            doc = fitz.open(pdf_path)
            for page_num in range(len(doc)):
                page = doc[page_num]
                images = page.get_images()
                for img in images:
                    content["images"].append({
                        "page": page_num + 1,
                        "xref": img[0],
                    })
            doc.close()
            
        except Exception as e:
            logger.error(f"Error extracting content: {str(e)}")
        
        return content
