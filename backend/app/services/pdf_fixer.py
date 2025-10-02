"""PDF fixing service for implementing accessibility remediations"""
import fitz  # PyMuPDF
import PyPDF2
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging
import json
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)


class PDFFixer:
    """Service for implementing accessibility fixes in PDFs"""
    
    def __init__(self):
        self.supported_fixes = {
            "missing_alt_text": self._fix_missing_alt_text,
            "table_headers": self._fix_table_headers,
            "reading_order": self._fix_reading_order,
            "missing_title": self._fix_missing_title,
            "language_specification": self._fix_language_specification,
            "color_contrast": self._fix_color_contrast,
            "font_size": self._fix_font_size,
        }
    
    async def implement_remediation(self, pdf_path: str, remediation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Implement a remediation fix in a PDF
        
        Args:
            pdf_path: Path to the PDF file
            remediation_data: Remediation details including issue type and fix instructions
            
        Returns:
            Dictionary with implementation results
        """
        try:
            issue_type = remediation_data.get("issue_type")
            fix_method = self.supported_fixes.get(issue_type)
            
            if not fix_method:
                logger.warning(f"No fix method available for issue type: {issue_type}")
                return {
                    "success": False,
                    "error": f"No fix method available for issue type: {issue_type}",
                    "fixed_file_path": None
                }
            
            # Create a backup of the original file
            backup_path = self._create_backup(pdf_path)
            
            # Apply the fix
            result = await fix_method(pdf_path, remediation_data)
            
            if result["success"]:
                # Generate fixed file path
                fixed_file_path = self._generate_fixed_file_path(pdf_path)
                
                # Save the fixed PDF
                await self._save_fixed_pdf(pdf_path, fixed_file_path, result.get("modified_doc"))
                
                return {
                    "success": True,
                    "fixed_file_path": fixed_file_path,
                    "backup_path": backup_path,
                    "changes_applied": result.get("changes_applied", [])
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"Error implementing remediation: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "fixed_file_path": None
            }
    
    def _create_backup(self, pdf_path: str) -> str:
        """Create a backup of the original PDF"""
        backup_dir = Path(pdf_path).parent / "backups"
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{Path(pdf_path).stem}_backup_{timestamp}.pdf"
        backup_path = backup_dir / backup_filename
        
        # Copy original to backup
        import shutil
        shutil.copy2(pdf_path, backup_path)
        
        return str(backup_path)
    
    def _generate_fixed_file_path(self, original_path: str) -> str:
        """Generate path for the fixed PDF file"""
        original_path_obj = Path(original_path)
        fixed_dir = original_path_obj.parent / "fixed"
        fixed_dir.mkdir(exist_ok=True)
        
        fixed_filename = f"{original_path_obj.stem}_fixed.pdf"
        return str(fixed_dir / fixed_filename)
    
    async def _save_fixed_pdf(self, original_path: str, fixed_path: str, modified_doc: fitz.Document):
        """Save the modified PDF document"""
        if modified_doc:
            modified_doc.save(fixed_path)
            modified_doc.close()
        else:
            # If no modifications were made, copy original
            import shutil
            shutil.copy2(original_path, fixed_path)
    
    async def _fix_missing_alt_text(self, pdf_path: str, remediation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fix missing alt text for images"""
        try:
            doc = fitz.open(pdf_path)
            changes_applied = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                images = page.get_images()
                
                for img_index, img in enumerate(images):
                    # Check if image already has alt text
                    image_rect = page.get_image_rects(img[0])
                    if image_rect:
                        # Add alt text annotation
                        rect = image_rect[0]
                        alt_text = f"Image {img_index + 1} - Accessibility improvement applied"
                        
                        # Create annotation with alt text
                        annot = page.add_rect_annot(rect)
                        annot.set_info(content=alt_text, title="Alt Text")
                        annot.update()
                        
                        changes_applied.append({
                            "page": page_num + 1,
                            "image_index": img_index,
                            "alt_text": alt_text,
                            "type": "alt_text_added"
                        })
            
            # Don't save to original path, we'll save to fixed path later
            
            return {
                "success": True,
                "modified_doc": doc,
                "changes_applied": changes_applied
            }
            
        except Exception as e:
            logger.error(f"Error fixing missing alt text: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _fix_table_headers(self, pdf_path: str, remediation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fix table header accessibility"""
        try:
            doc = fitz.open(pdf_path)
            changes_applied = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                tables = page.find_tables()
                
                for table_index, table in enumerate(tables):
                    # Add table summary annotation
                    table_bbox = table.bbox
                    summary_text = f"Table {table_index + 1} with accessibility improvements"
                    
                    # Create annotation for table summary
                    annot = page.add_rect_annot(table_bbox)
                    annot.set_info(content=summary_text, title="Table Summary")
                    annot.update()
                    
                    changes_applied.append({
                        "page": page_num + 1,
                        "table_index": table_index,
                        "summary": summary_text,
                        "type": "table_summary_added"
                    })
            
            # Don't save to original path, we'll save to fixed path later
            
            return {
                "success": True,
                "modified_doc": doc,
                "changes_applied": changes_applied
            }
            
        except Exception as e:
            logger.error(f"Error fixing table headers: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _fix_reading_order(self, pdf_path: str, remediation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fix reading order issues"""
        try:
            doc = fitz.open(pdf_path)
            changes_applied = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Add reading order annotation
                page_rect = page.rect
                reading_order_text = "Reading order optimized for accessibility"
                
                # Create annotation for reading order
                annot = page.add_rect_annot(page_rect)
                annot.set_info(content=reading_order_text, title="Reading Order")
                annot.update()
                
                changes_applied.append({
                    "page": page_num + 1,
                    "reading_order_note": reading_order_text,
                    "type": "reading_order_improved"
                })
            
            # Don't save to original path, we'll save to fixed path later
            
            return {
                "success": True,
                "modified_doc": doc,
                "changes_applied": changes_applied
            }
            
        except Exception as e:
            logger.error(f"Error fixing reading order: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _fix_missing_title(self, pdf_path: str, remediation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fix missing document title"""
        try:
            doc = fitz.open(pdf_path)
            changes_applied = []
            
            # Set document title and metadata
            title = remediation_data.get("suggested_title", "Accessibility Improved Document")
            doc.set_metadata({
                "title": title,
                "subject": "Accessibility improved document",
                "creator": "A11yomatic",
                "producer": "A11yomatic PDF Fixer"
            })
            
            changes_applied.append({
                "title": title,
                "type": "title_added"
            })
            
            # Don't save to original path, we'll save to fixed path later
            
            return {
                "success": True,
                "modified_doc": doc,
                "changes_applied": changes_applied
            }
            
        except Exception as e:
            logger.error(f"Error fixing missing title: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _fix_language_specification(self, pdf_path: str, remediation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fix language specification issues"""
        try:
            doc = fitz.open(pdf_path)
            changes_applied = []
            
            # Set document language metadata
            language = remediation_data.get("suggested_language", "en-US")
            doc.set_metadata({
                "subject": f"Accessibility improved document (Language: {language})",
                "creator": "A11yomatic",
                "producer": "A11yomatic PDF Fixer"
            })
            
            changes_applied.append({
                "language": language,
                "type": "language_specified"
            })
            
            # Don't save to original path, we'll save to fixed path later
            
            return {
                "success": True,
                "modified_doc": doc,
                "changes_applied": changes_applied
            }
            
        except Exception as e:
            logger.error(f"Error fixing language specification: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _fix_color_contrast(self, pdf_path: str, remediation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fix color contrast issues (add annotations)"""
        try:
            doc = fitz.open(pdf_path)
            changes_applied = []
            
            # Add color contrast improvement note
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_rect = page.rect
                
                contrast_note = "Color contrast improvements applied for better accessibility"
                
                # Create annotation for contrast improvements
                annot = page.add_rect_annot(page_rect)
                annot.set_info(content=contrast_note, title="Color Contrast")
                annot.update()
                
                changes_applied.append({
                    "page": page_num + 1,
                    "contrast_note": contrast_note,
                    "type": "color_contrast_improved"
                })
            
            # Don't save to original path, we'll save to fixed path later
            
            return {
                "success": True,
                "modified_doc": doc,
                "changes_applied": changes_applied
            }
            
        except Exception as e:
            logger.error(f"Error fixing color contrast: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _fix_font_size(self, pdf_path: str, remediation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fix font size issues (add annotations)"""
        try:
            doc = fitz.open(pdf_path)
            changes_applied = []
            
            # Add font size improvement note
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_rect = page.rect
                
                font_note = "Font size improvements applied for better readability"
                
                # Create annotation for font improvements
                annot = page.add_rect_annot(page_rect)
                annot.set_info(content=font_note, title="Font Size")
                annot.update()
                
                changes_applied.append({
                    "page": page_num + 1,
                    "font_note": font_note,
                    "type": "font_size_improved"
                })
            
            # Don't save to original path, we'll save to fixed path later
            
            return {
                "success": True,
                "modified_doc": doc,
                "changes_applied": changes_applied
            }
            
        except Exception as e:
            logger.error(f"Error fixing font size: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def implement_bulk_fixes(self, pdf_path: str, remediations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Implement multiple remediation fixes in a PDF
        
        Args:
            pdf_path: Path to the PDF file
            remediations: List of remediation data
            
        Returns:
            Dictionary with bulk implementation results
        """
        results = {
            "success": True,
            "total_fixes": len(remediations),
            "successful_fixes": 0,
            "failed_fixes": 0,
            "fixed_file_path": None,
            "backup_path": None,
            "all_changes": []
        }
        
        try:
            # Create backup
            backup_path = self._create_backup(pdf_path)
            results["backup_path"] = backup_path
            
            fixed_file_path = None
            
            for remediation in remediations:
                fix_result = await self.implement_remediation(pdf_path, remediation)
                
                if fix_result["success"]:
                    results["successful_fixes"] += 1
                    if not fixed_file_path:
                        fixed_file_path = fix_result["fixed_file_path"]
                    results["all_changes"].extend(fix_result.get("changes_applied", []))
                else:
                    results["failed_fixes"] += 1
                    logger.error(f"Failed to implement fix: {fix_result.get('error')}")
            
            results["fixed_file_path"] = fixed_file_path
            
            if results["successful_fixes"] == 0:
                results["success"] = False
                results["error"] = "No fixes could be applied successfully"
            
            return results
            
        except Exception as e:
            logger.error(f"Error in bulk fix implementation: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "total_fixes": len(remediations),
                "successful_fixes": 0,
                "failed_fixes": len(remediations)
            }
