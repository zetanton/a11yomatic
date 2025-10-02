"""AI service for content generation and accessibility improvements"""
import openai
from typing import Dict, List, Optional
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class AIService:
    """Service for AI-powered content generation"""
    
    def __init__(self):
        # Configure OpenAI client (works with Groq and custom endpoints)
        self.api_key = settings.GROQ_API_KEY or settings.OPENAI_API_KEY
        self.api_base = settings.OPENAI_API_BASE_URL
        
        if self.api_key:
            openai.api_key = self.api_key
            openai.api_base = self.api_base
            logger.info(f"AI Service initialized with base URL: {self.api_base}")
        else:
            logger.warning("No AI API key configured. AI features will be limited.")
    
    async def test_connection(self) -> bool:
        """Test connection to AI service"""
        if not self.api_key:
            logger.error("No API key configured")
            return False
        
        try:
            response = await openai.ChatCompletion.acreate(
                model="mixtral-8x7b-32768" if "groq" in self.api_base.lower() else "gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=5
            )
            logger.info("AI service connection successful")
            return True
        except Exception as e:
            logger.error(f"AI service connection failed: {str(e)}")
            return False
    
    async def generate_alt_text(self, context: Dict[str, Any]) -> str:
        """
        Generate alternative text for images
        
        Args:
            context: Dictionary with image context (page content, surrounding text, etc.)
            
        Returns:
            Generated alt text
        """
        if not self.api_key:
            return "Alternative text generation unavailable - no AI service configured"
        
        try:
            # Determine model based on API base
            model = "mixtral-8x7b-32768" if "groq" in self.api_base.lower() else "gpt-4"
            
            prompt = self._build_alt_text_prompt(context)
            
            response = await openai.ChatCompletion.acreate(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an accessibility expert. Generate concise, descriptive alternative text for images that follows WCAG 2.1 guidelines.
                        
Rules:
- Keep alt text under 125 characters
- Describe the essential information conveyed by the image
- Don't start with "Image of" or "Picture of"
- Be specific and descriptive
- Focus on the content and function of the image"""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=150,
                temperature=0.3
            )
            
            alt_text = response.choices[0].message.content.strip()
            logger.info(f"Generated alt text: {alt_text[:50]}...")
            return alt_text
            
        except Exception as e:
            logger.error(f"Error generating alt text: {str(e)}")
            return "Error generating alternative text. Please add manually."
    
    async def generate_heading_structure(self, content: str) -> List[Dict[str, str]]:
        """
        Generate proper heading structure for content
        
        Args:
            content: Text content to analyze
            
        Returns:
            List of headings with levels and text
        """
        if not self.api_key:
            return []
        
        try:
            model = "mixtral-8x7b-32768" if "groq" in self.api_base.lower() else "gpt-4"
            
            response = await openai.ChatCompletion.acreate(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an accessibility expert. Analyze the content and suggest a proper heading hierarchy (H1, H2, H3, etc.) that follows WCAG guidelines.
                        
Return a JSON array of headings with this structure:
[
  {"level": "h1", "text": "Main heading"},
  {"level": "h2", "text": "Subheading"},
  ...
]

Rules:
- Only one H1 per document
- Don't skip heading levels
- Headings should be descriptive and hierarchical"""
                    },
                    {
                        "role": "user",
                        "content": f"Analyze this content and suggest heading structure:\n\n{content[:2000]}"
                    }
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            import json
            headings = json.loads(response.choices[0].message.content)
            logger.info(f"Generated {len(headings)} heading suggestions")
            return headings
            
        except Exception as e:
            logger.error(f"Error generating heading structure: {str(e)}")
            return []
    
    async def improve_table_accessibility(self, table_data: List[List[str]]) -> Dict[str, Any]:
        """
        Generate accessible table structure
        
        Args:
            table_data: Table data as list of rows
            
        Returns:
            Dictionary with improved table structure
        """
        if not self.api_key or not table_data:
            return {
                "headers": [],
                "caption": "",
                "summary": ""
            }
        
        try:
            model = "mixtral-8x7b-32768" if "groq" in self.api_base.lower() else "gpt-4"
            
            # Convert table to string representation
            table_str = "\n".join([" | ".join(row) for row in table_data[:5]])  # First 5 rows
            
            response = await openai.ChatCompletion.acreate(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an accessibility expert. Analyze the table and suggest improvements for accessibility.

Return a JSON object with:
{
  "headers": ["header1", "header2", ...],
  "caption": "Brief table caption",
  "summary": "Detailed table summary"
}"""
                    },
                    {
                        "role": "user",
                        "content": f"Improve this table for accessibility:\n\n{table_str}"
                    }
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            import json
            improvements = json.loads(response.choices[0].message.content)
            logger.info("Generated table accessibility improvements")
            return improvements
            
        except Exception as e:
            logger.error(f"Error improving table accessibility: {str(e)}")
            return {
                "headers": [],
                "caption": "Error generating caption",
                "summary": "Error generating summary"
            }
    
    async def generate_remediation_suggestion(self, issue: Dict[str, Any]) -> str:
        """
        Generate specific remediation suggestions for an accessibility issue
        
        Args:
            issue: Accessibility issue details
            
        Returns:
            Remediation suggestion
        """
        if not self.api_key:
            return "Please configure AI service to get remediation suggestions"
        
        try:
            model = "mixtral-8x7b-32768" if "groq" in self.api_base.lower() else "gpt-4"
            
            response = await openai.ChatCompletion.acreate(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an accessibility expert. Provide specific, actionable remediation suggestions for PDF accessibility issues.
                        
Focus on:
- Practical steps to fix the issue
- WCAG 2.1 compliance
- Best practices
- Tools or techniques that can help"""
                    },
                    {
                        "role": "user",
                        "content": f"""Issue Type: {issue.get('type', 'Unknown')}
Severity: {issue.get('severity', 'Unknown')}
Description: {issue.get('description', 'No description')}
WCAG Criteria: {issue.get('wcag_criteria', 'Not specified')}

Provide a detailed remediation suggestion:"""
                    }
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            suggestion = response.choices[0].message.content.strip()
            logger.info("Generated remediation suggestion")
            return suggestion
            
        except Exception as e:
            logger.error(f"Error generating remediation suggestion: {str(e)}")
            return "Error generating suggestion. Please review WCAG guidelines manually."
    
    def _build_alt_text_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for alt text generation"""
        page_num = context.get("page", "unknown")
        surrounding_text = context.get("surrounding_text", "")
        image_index = context.get("image_index", 0)
        
        prompt = f"""Image {image_index + 1} on page {page_num}

Context from surrounding text:
{surrounding_text[:500] if surrounding_text else 'No surrounding text available'}

Generate appropriate alternative text for this image based on the context."""
        
        return prompt


