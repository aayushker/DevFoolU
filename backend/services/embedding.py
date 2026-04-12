"""Embedding service for generating vector embeddings"""

from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor

from core.config import settings

logger = logging.getLogger("DevFoolU.embedding")


class EmbeddingService:
    """Service for generating embeddings using sentence-transformers"""
    
    def __init__(self):
        self.model: Optional[SentenceTransformer] = None
        self._ready = False
        self._executor = ThreadPoolExecutor(max_workers=4)
    
    async def initialize(self):
        """Initialize the embedding model"""
        try:
            logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL_NAME}")
            
            # Load model in executor to avoid blocking
            loop = asyncio.get_event_loop()
            self.model = await loop.run_in_executor(
                self._executor,
                SentenceTransformer,
                settings.EMBEDDING_MODEL_NAME
            )
            
            self._ready = True
            logger.info(f"✅ Embedding model loaded (dimension: {self.model.get_sentence_embedding_dimension()})")
            
        except Exception as e:
            logger.error(f"❌ Failed to load embedding model: {e}")
            raise
    
    def is_ready(self) -> bool:
        """Check if model is ready"""
        return self._ready and self.model is not None
    
    def _create_combined_text(self, project: Dict) -> str:
        """
        Combine all relevant fields from a project into a single text for embedding
        """
        parts = []
        
        # Add project name
        if project.get('nameOfProject'):
            parts.append(f"Project: {project['nameOfProject']}")
        
        # Add description
        if project.get('descriptionOfProject'):
            parts.append(f"Description: {project['descriptionOfProject']}")

        # Add short tagline if available
        if project.get('tagLine'):
            parts.append(f"Tagline: {project['tagLine']}")
        
        # Add problem solved
        if project.get('problemSolved'):
            parts.append(f"Problem: {project['problemSolved']}")
        
        # Add challenges faced
        if project.get('challengesFaced'):
            parts.append(f"Challenges: {project['challengesFaced']}")
        
        # Add technologies
        if project.get('technologiesUsed'):
            if isinstance(project['technologiesUsed'], list):
                tech_str = ", ".join(project['technologiesUsed'])
                if tech_str:
                    parts.append(f"Technologies: {tech_str}")
            elif isinstance(project['technologiesUsed'], str):
                parts.append(f"Technologies: {project['technologiesUsed']}")

        # Add tags for additional topical signals
        if project.get('tagsOfProject') and isinstance(project.get('tagsOfProject'), list):
            tag_str = ", ".join([str(tag).strip() for tag in project['tagsOfProject'] if str(tag).strip()])
            if tag_str:
                parts.append(f"Tags: {tag_str}")

        # Add condensed page narrative as a fallback signal for sparse explicit sections
        if project.get('rawContentOfProject'):
            raw_text = str(project['rawContentOfProject']).strip()
            if raw_text:
                parts.append(f"Narrative: {raw_text[:2500]}")
        
        # Combine all parts
        combined = " | ".join(parts)
        
        # Fallback if empty
        if not combined.strip():
            combined = project.get('nameOfProject', project.get('urlOfProject', 'Unknown Project'))
        
        return combined
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        """
        if not self.is_ready():
            raise Exception("Embedding model not initialized")
        
        try:
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                self._executor,
                self.model.encode,
                text
            )
            return embedding.tolist()
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    async def generate_project_embedding(self, project: Dict) -> List[float]:
        """
        Generate embedding for a project by combining its fields
        """
        try:
            combined_text = self._create_combined_text(project)
            logger.debug(f"Generating embedding for: {project.get('nameOfProject', 'Unknown')[:50]}...")
            
            embedding = await self.generate_embedding(combined_text)
            logger.debug(f"✅ Generated {len(embedding)}-dim embedding")
            
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating project embedding: {e}")
            raise
    
    async def generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batch (more efficient)
        """
        if not self.is_ready():
            raise Exception("Embedding model not initialized")
        
        try:
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                self._executor,
                self.model.encode,
                texts
            )
            return [emb.tolist() for emb in embeddings]
            
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise

    async def generate_embeddings_for_projects(self, projects: List[Dict]) -> List[List[float]]:
        """Generate embeddings for multiple projects in one batch call."""
        texts = [self._create_combined_text(project) for project in projects]
        return await self.generate_batch_embeddings(texts)
    
    async def generate_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding for a search query
        """
        return await self.generate_embedding(query)
    
    def cleanup(self):
        """Cleanup resources"""
        self._executor.shutdown(wait=True)


# Global embedding service instance
embedding_service = EmbeddingService()
