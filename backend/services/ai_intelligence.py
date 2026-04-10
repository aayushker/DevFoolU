"""AI Intelligence Service using Google Gemini for project similarity analysis"""

import logging
from typing import List, Dict, Optional
import google.generativeai as genai
from core.config import settings

logger = logging.getLogger("DevFoolU.services.ai_intelligence")


class AIIntelligenceService:
    """Service for AI-powered analysis using Gemini"""
    
    def __init__(self):
        """Initialize Gemini AI service"""
        self.model = None
        self._initialize_gemini()
    
    def _initialize_gemini(self):
        """Initialize Gemini API"""
        try:
            if not settings.GEMINI_API_KEY:
                logger.warning("GEMINI_API_KEY not set. AI intelligence features will be disabled.")
                return
            
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
            logger.info(f"Gemini AI initialized with model: {settings.GEMINI_MODEL}")
        except Exception as e:
            logger.error(f"Error initializing Gemini AI: {e}")
            self.model = None
    
    def _create_analysis_prompt(
        self, 
        input_project: Dict, 
        similar_projects: List[Dict]
    ) -> str:
        """Create a structured prompt for Gemini analysis"""
        
        # Extract key information from input project
        input_info = f"""Input Project:
- Name: {input_project.get('nameOfProject', 'Unknown')}
- Description: {input_project.get('descriptionOfProject', 'No description')}
- Technologies: {', '.join(input_project.get('technologiesUsedInProject', []))}
- Tags: {', '.join(input_project.get('tagsOfProject', []))}
"""
        
        # Extract key information from similar projects
        similar_info = "Top Similar Projects Found:\n"
        for idx, proj in enumerate(similar_projects[:5], 1):
            similarity_score = proj.get('similarity_score', 0) * 100
            similar_info += f"""\n{idx}. {proj.get('nameOfProject', 'Unknown')} (Similarity: {similarity_score:.1f}%)
   - Description: {proj.get('descriptionOfProject', 'No description')[:100]}...
   - Technologies: {', '.join(proj.get('technologiesUsedInProject', [])[:5])}
   - Tags: {', '.join(proj.get('tagsOfProject', [])[:5])}
"""
        
        prompt = f"""{input_info}

{similar_info}

Task: Analyze the similarity between the input project and the top 5 similar projects found. Provide a concise verdict (maximum 150 words) in bullet points covering:

1. Overall Similarity Assessment: Rate the similarity quality (Excellent/Good/Moderate/Poor)
2. Key Similarities: What makes these projects similar?
3. Technology Overlap: Common technologies and frameworks used
DO NOT SAY "I don't know", "Here's an analysis of the similarity between Dbuz and the listed projects:".
Format your response as clear, concise bullet points. Be direct and insightful."""
        
        return prompt
    
    async def generate_similarity_verdict(
        self, 
        input_project: Dict, 
        similar_projects: List[Dict]
    ) -> Optional[Dict]:
        """
        Generate AI verdict on project similarity analysis
        
        Args:
            input_project: The input project being analyzed
            similar_projects: List of similar projects found
        
        Returns:
            Dict containing AI verdict or None if service unavailable
        """
        if not self.model:
            logger.warning("Gemini AI not initialized. Skipping AI verdict.")
            return None
        
        if not similar_projects:
            return {
                "verdict": "• No similar projects found in the database.\n• Consider expanding the search criteria or checking if the project is unique.",
                "model": settings.GEMINI_MODEL,
                "status": "no_results"
            }
        
        try:
            prompt = self._create_analysis_prompt(input_project, similar_projects)
            
            logger.info("Generating AI verdict for similarity analysis...")
            
            # Generate content with Gemini
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=settings.GEMINI_MAX_OUTPUT_TOKENS,
                    temperature=settings.GEMINI_TEMPERATURE,
                )
            )
            
            verdict_text = response.text.strip()
            
            logger.info("AI verdict generated successfully")
            
            return {
                "verdict": verdict_text,
                "model": settings.GEMINI_MODEL,
                "status": "success",
                "projects_analyzed": len(similar_projects)
            }
        
        except Exception as e:
            logger.error(f"Error generating AI verdict: {e}", exc_info=True)
            return {
                "verdict": "• AI analysis temporarily unavailable.\n• Please review the similarity scores manually.",
                "model": settings.GEMINI_MODEL,
                "status": "error",
                "error": str(e)
            }
    
    def is_available(self) -> bool:
        """Check if AI service is available"""
        return self.model is not None


# Global AI intelligence service instance
ai_intelligence_service = AIIntelligenceService()
