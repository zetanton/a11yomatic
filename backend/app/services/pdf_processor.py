"""PDF processing service using free libraries: PyPDF2, pdfplumber, and PyMuPDF"""
import PyPDF2
import pdfplumber
import fitz  # PyMuPDF
from typing import Dict, List, Any, Optional
import os
from pathlib import Path
import structlog

logger = structlog.get_logger()


class PDFProcessor:
    """PDF processing and accessibility analysis service"""
    
    def __init__(self):
        """Initialize PDF processor"""
        self.supported_extensions = ['.pdf']
    
    async def analyze_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Comprehensive PDF accessibility analysis
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary with analysis results and detected issues
        """
        logger.info("Starting PDF analysis", pdf_path=pdf_path)
        
        issues = []
        metadata = {}
        
        try:
            # Extract metadata and basic info
            metadata = await self.extract_metadata(pdf_path)
            
            # Analyze with pdfplumber for content analysis
            content_issues = await self._analyze_content(pdf_path)
            issues.extend(content_issues)
            
            # Analyze with PyMuPDF for structure
            structure_issues = await self._analyze_structure(pdf_path)
            issues.extend(structure_issues)
            
            # Calculate overall score
            overall_score = self._calculate_accessibility_score(issues, metadata)
            
            # Categorize issues by severity
            issue_counts = self._categorize_issues(issues)
            
            result = {
                "total_issues": len(issues),
                "critical_issues": issue_counts['critical'],
                "high_issues": issue_counts['high'],
                "medium_issues": issue_counts['medium'],
                "low_issues": issue_counts['low'],
                "overall_score": overall_score,
                "issues": issues,
                "metadata": metadata,
                "wcag_compliance_level": self._determine_wcag_level(overall_score)
            }
            
            logger.info(
                "PDF analysis completed",
                total_issues=len(issues),
                score=overall_score
            )
            
            return result
            
        except Exception as e:
            logger.error("PDF analysis failed", error=str(e))
            raise
    
    async def extract_metadata(self, pdf_path: str) -> Dict[str, Any]:
        """Extract PDF metadata using PyPDF2"""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                metadata = {
                    "page_count": len(reader.pages),
                    "has_metadata": reader.metadata is not None,
                    "title": reader.metadata.get('/Title', '') if reader.metadata else '',
                    "author": reader.metadata.get('/Author', '') if reader.metadata else '',
                    "subject": reader.metadata.get('/Subject', '') if reader.metadata else '',
                    "is_encrypted": reader.is_encrypted,
                }
                
                # Check if PDF is tagged (accessibility feature)
                if reader.metadata:
                    metadata["is_tagged"] = '/MarkInfo' in str(reader.metadata)
                else:
                    metadata["is_tagged"] = False
                
                logger.info("Extracted PDF metadata", metadata=metadata)
                return metadata
                
        except Exception as e:
            logger.error("Failed to extract metadata", error=str(e))
            return {"error": str(e)}
    
    async def extract_content(self, pdf_path: str) -> Dict[str, Any]:
        """Extract text, tables, and images from PDF"""
        content = {
            "pages": [],
            "total_text_length": 0,
            "total_tables": 0,
            "total_images": 0
        }
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    # Extract text
                    text = page.extract_text() or ""
                    
                    # Extract tables
                    tables = page.extract_tables() or []
                    
                    # Get page dimensions
                    width = page.width
                    height = page.height
                    
                    page_content = {
                        "page_number": page_num + 1,
                        "text": text,
                        "text_length": len(text),
                        "tables": tables,
                        "table_count": len(tables),
                        "dimensions": {"width": width, "height": height}
                    }
                    
                    content["pages"].append(page_content)
                    content["total_text_length"] += len(text)
                    content["total_tables"] += len(tables)
            
            # Extract images using PyMuPDF
            doc = fitz.open(pdf_path)
            for page_num in range(len(doc)):
                page = doc[page_num]
                images = page.get_images()
                content["pages"][page_num]["image_count"] = len(images)
                content["total_images"] += len(images)
            
            doc.close()
            
            logger.info(
                "Extracted PDF content",
                pages=len(content["pages"]),
                total_images=content["total_images"]
            )
            
            return content
            
        except Exception as e:
            logger.error("Failed to extract content", error=str(e))
            return content
    
    async def _analyze_content(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Analyze PDF content for accessibility issues using pdfplumber"""
        issues = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    # Check for text content
                    text = page.extract_text()
                    if not text or len(text.strip()) < 10:
                        issues.append({
                            "issue_type": "missing_text",
                            "severity": "critical",
                            "page_number": page_num + 1,
                            "description": "Page appears to be image-only or has insufficient text. This makes it inaccessible to screen readers.",
                            "wcag_criteria": "1.1.1",
                            "location": {"page": page_num + 1}
                        })
                    
                    # Check for tables without headers
                    tables = page.extract_tables()
                    for table_idx, table in enumerate(tables):
                        if not self._has_table_headers(table):
                            issues.append({
                                "issue_type": "table_missing_headers",
                                "severity": "high",
                                "page_number": page_num + 1,
                                "description": f"Table {table_idx + 1} is missing proper headers. Tables need clear headers for accessibility.",
                                "wcag_criteria": "1.3.1",
                                "location": {"page": page_num + 1, "table": table_idx + 1}
                            })
                        
                        # Check for complex tables
                        if len(table) > 10 and len(table[0]) > 5:
                            issues.append({
                                "issue_type": "complex_table",
                                "severity": "medium",
                                "page_number": page_num + 1,
                                "description": f"Table {table_idx + 1} is complex and may need additional structure for accessibility.",
                                "wcag_criteria": "1.3.1",
                                "location": {"page": page_num + 1, "table": table_idx + 1}
                            })
            
        except Exception as e:
            logger.error("Content analysis failed", error=str(e))
        
        return issues
    
    async def _analyze_structure(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Analyze PDF structure for accessibility issues using PyMuPDF"""
        issues = []
        
        try:
            doc = fitz.open(pdf_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Check for images without alt text
                images = page.get_images()
                for img_index, img in enumerate(images):
                    issues.append({
                        "issue_type": "missing_alt_text",
                        "severity": "high",
                        "page_number": page_num + 1,
                        "description": f"Image {img_index + 1} is missing alternative text. All images must have descriptive alt text.",
                        "wcag_criteria": "1.1.1",
                        "location": {"page": page_num + 1, "image": img_index + 1}
                    })
                
                # Check for heading structure
                text_blocks = page.get_text("dict")
                if text_blocks and "blocks" in text_blocks:
                    has_headings = False
                    for block in text_blocks["blocks"]:
                        if block.get("type") == 0:  # Text block
                            # Check for font size variations that might indicate headings
                            lines = block.get("lines", [])
                            if lines:
                                has_headings = True
                                break
                    
                    if not has_headings and page_num == 0:
                        issues.append({
                            "issue_type": "missing_heading_structure",
                            "severity": "medium",
                            "page_number": page_num + 1,
                            "description": "Document may be missing proper heading structure. Headings help organize content.",
                            "wcag_criteria": "1.3.1",
                            "location": {"page": page_num + 1}
                        })
                
                # Check for text color contrast
                # Note: This is a simplified check; real contrast checking is more complex
                if len(images) > 0 and page.get_text():
                    issues.append({
                        "issue_type": "potential_contrast_issue",
                        "severity": "low",
                        "page_number": page_num + 1,
                        "description": "Page contains text and images. Verify color contrast meets WCAG requirements (4.5:1 for normal text).",
                        "wcag_criteria": "1.4.3",
                        "location": {"page": page_num + 1}
                    })
            
            doc.close()
            
        except Exception as e:
            logger.error("Structure analysis failed", error=str(e))
        
        return issues
    
    def _has_table_headers(self, table: List[List[str]]) -> bool:
        """Check if table has proper headers"""
        if not table or len(table) < 2:
            return False
        
        # Check if first row looks like headers (non-empty cells)
        first_row = table[0]
        if not first_row:
            return False
        
        # Count non-empty cells in first row
        non_empty = sum(1 for cell in first_row if cell and str(cell).strip())
        
        # Should have at least 50% non-empty cells
        return non_empty >= len(first_row) * 0.5
    
    def _calculate_accessibility_score(
        self,
        issues: List[Dict[str, Any]],
        metadata: Dict[str, Any]
    ) -> int:
        """
        Calculate overall accessibility score (0-100)
        
        Higher score = more accessible
        """
        base_score = 100
        
        # Deduct points based on severity
        severity_penalties = {
            "critical": 15,
            "high": 10,
            "medium": 5,
            "low": 2
        }
        
        for issue in issues:
            severity = issue.get("severity", "low")
            penalty = severity_penalties.get(severity, 2)
            base_score -= penalty
        
        # Bonus points for good practices
        if metadata.get("is_tagged"):
            base_score += 10
        
        if metadata.get("title"):
            base_score += 5
        
        # Ensure score is between 0 and 100
        return max(0, min(100, base_score))
    
    def _categorize_issues(self, issues: List[Dict[str, Any]]) -> Dict[str, int]:
        """Categorize issues by severity"""
        counts = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }
        
        for issue in issues:
            severity = issue.get("severity", "low")
            if severity in counts:
                counts[severity] += 1
        
        return counts
    
    def _determine_wcag_level(self, score: int) -> str:
        """Determine WCAG compliance level based on score"""
        if score >= 90:
            return "AAA"
        elif score >= 75:
            return "AA"
        elif score >= 60:
            return "A"
        else:
            return "Non-compliant"
    
    async def validate_pdf(self, file_path: str) -> bool:
        """Validate if file is a valid PDF"""
        try:
            if not os.path.exists(file_path):
                return False
            
            # Check file extension
            if Path(file_path).suffix.lower() not in self.supported_extensions:
                return False
            
            # Try to open with PyPDF2
            with open(file_path, 'rb') as file:
                PyPDF2.PdfReader(file)
            
            return True
            
        except Exception as e:
            logger.error("PDF validation failed", error=str(e))
            return False


# Create singleton instance
pdf_processor = PDFProcessor()
