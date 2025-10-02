"""AI service for content generation with support for OpenAI and Groq"""
import openai
from typing import Dict, List, Optional
import json
import asyncio
from app.core.config import settings
import structlog

logger = structlog.get_logger()


class AIService:
    """AI service supporting multiple providers including Groq for fast inference"""
    
    def __init__(self):
        """Initialize AI service with configured API settings"""
        self.api_key = settings.OPENAI_API_KEY or settings.GROQ_API_KEY
        self.api_base = settings.OPENAI_API_BASE_URL
        self.model = settings.AI_MODEL
        self.temperature = settings.AI_TEMPERATURE
        self.max_tokens = settings.AI_MAX_TOKENS
        
        # Configure OpenAI client
        openai.api_key = self.api_key
        openai.api_base = self.api_base
        
        logger.info(
            "AI service initialized",
            api_base=self.api_base,
            model=self.model
        )
    
    async def test_connection(self) -> bool:
        """Test AI service connection"""
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            logger.info("AI service connection test successful")
            return True
        except Exception as e:
            logger.error("AI service connection test failed", error=str(e))
            return False
    
    async def generate_alt_text(
        self,
        image_description: str,
        context: Optional[str] = None
    ) -> str:
        """
        Generate alternative text for images following WCAG guidelines
        
        Args:
            image_description: Description of the image
            context: Additional context about the image's purpose
            
        Returns:
            Generated alt text (under 125 characters)
        """
        try:
            prompt = f"Generate alt text for this image: {image_description}"
            if context:
                prompt += f"\nContext: {context}"
            
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an accessibility expert. Generate concise, descriptive alternative text for images that follows WCAG 2.1 guidelines. 
                        The alt text should be under 125 characters and describe the essential information in the image.
                        Focus on the content and function of the image, not decorative aspects."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=150,
                temperature=self.temperature
            )
            
            alt_text = response.choices[0].message.content.strip()
            logger.info(
                "Generated alt text",
                length=len(alt_text),
                model=self.model
            )
            return alt_text
            
        except Exception as e:
            logger.error("Failed to generate alt text", error=str(e))
            return "Image description unavailable (AI generation failed)"
    
    async def generate_heading_structure(self, content: str) -> List[Dict[str, str]]:
        """
        Generate proper heading hierarchy for content
        
        Args:
            content: Text content to analyze
            
        Returns:
            List of headings with their level and text
        """
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an accessibility expert. Analyze the content and suggest a proper heading hierarchy (H1, H2, H3, etc.) 
                        that follows WCAG guidelines. Return ONLY a JSON array of headings with their level and text.
                        Format: [{"level": "h1", "text": "Main Title"}, {"level": "h2", "text": "Section Title"}]"""
                    },
                    {
                        "role": "user",
                        "content": f"Analyze this content and suggest heading structure:\n\n{content[:2000]}"
                    }
                ],
                max_tokens=500,
                temperature=self.temperature
            )
            
            # Parse JSON response
            response_text = response.choices[0].message.content.strip()
            
            # Try to extract JSON from response
            if response_text.startswith('['):
                headings = json.loads(response_text)
            else:
                # Try to find JSON in the response
                import re
                json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
                if json_match:
                    headings = json.loads(json_match.group(0))
                else:
                    headings = []
            
            logger.info(
                "Generated heading structure",
                count=len(headings),
                model=self.model
            )
            return headings
            
        except Exception as e:
            logger.error("Failed to generate heading structure", error=str(e))
            return []
    
    async def improve_table_accessibility(
        self,
        table_data: Dict
    ) -> Dict[str, str]:
        """
        Generate accessible table structure with headers, caption, and summary
        
        Args:
            table_data: Table data to analyze
            
        Returns:
            Dictionary with headers, caption, and summary suggestions
        """
        try:
            table_str = json.dumps(table_data, indent=2)[:1500]
            
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an accessibility expert. Analyze the table data and suggest improvements for accessibility.
                        Provide: 1) Descriptive column headers, 2) A concise caption, 3) A brief summary.
                        Return as JSON: {"headers": ["Header1", "Header2"], "caption": "Table caption", "summary": "Brief summary"}"""
                    },
                    {
                        "role": "user",
                        "content": f"Improve this table for accessibility:\n{table_str}"
                    }
                ],
                max_tokens=300,
                temperature=self.temperature
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Try to parse JSON response
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                result = {
                    "headers": [],
                    "caption": "Data Table",
                    "summary": response_text[:200]
                }
            
            logger.info(
                "Generated table accessibility improvements",
                model=self.model
            )
            return result
            
        except Exception as e:
            logger.error("Failed to improve table accessibility", error=str(e))
            return {
                "headers": [],
                "caption": "Data Table",
                "summary": "Table accessibility analysis failed"
            }
    
    async def generate_reading_order_suggestion(
        self,
        page_structure: Dict
    ) -> List[Dict[str, any]]:
        """
        Generate reading order suggestions for page elements
        
        Args:
            page_structure: Structure of page elements
            
        Returns:
            Ordered list of elements with reading order
        """
        try:
            structure_str = json.dumps(page_structure, indent=2)[:1500]
            
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an accessibility expert. Analyze the page structure and suggest a logical reading order for screen readers.
                        Return as JSON array: [{"order": 1, "element": "heading", "description": "Main title"}, ...]"""
                    },
                    {
                        "role": "user",
                        "content": f"Suggest reading order for this page:\n{structure_str}"
                    }
                ],
                max_tokens=400,
                temperature=self.temperature
            )
            
            response_text = response.choices[0].message.content.strip()
            
            try:
                reading_order = json.loads(response_text)
            except json.JSONDecodeError:
                reading_order = []
            
            logger.info(
                "Generated reading order suggestions",
                count=len(reading_order),
                model=self.model
            )
            return reading_order
            
        except Exception as e:
            logger.error("Failed to generate reading order", error=str(e))
            return []
    
    async def generate_document_structure_suggestions(
        self,
        content: str
    ) -> Dict[str, any]:
        """
        Generate comprehensive document structure suggestions
        
        Args:
            content: Document content to analyze
            
        Returns:
            Dictionary with structure suggestions
        """
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an accessibility expert. Analyze the document content and suggest structural improvements for accessibility.
                        Include: headings, landmarks, lists, and other semantic structures.
                        Return as JSON."""
                    },
                    {
                        "role": "user",
                        "content": f"Analyze document structure:\n\n{content[:2000]}"
                    }
                ],
                max_tokens=500,
                temperature=self.temperature
            )
            
            response_text = response.choices[0].message.content.strip()
            
            try:
                suggestions = json.loads(response_text)
            except json.JSONDecodeError:
                suggestions = {"analysis": response_text}
            
            logger.info(
                "Generated document structure suggestions",
                model=self.model
            )
            return suggestions
            
        except Exception as e:
            logger.error("Failed to generate structure suggestions", error=str(e))
            return {"error": str(e)}


# Create singleton instance
ai_service = AIService()
