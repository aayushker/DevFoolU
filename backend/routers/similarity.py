"""Router for similarity search operations"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging

from services.embedding import embedding_service
from services.mongodb import mongodb_client
from services.ai_intelligence import ai_intelligence_service
from core.config import settings

logger = logging.getLogger("DevFoolU.routers.similarity")

router = APIRouter()


def remove_embeddings(project: Dict) -> Dict:
    """Remove embeddings from project data before returning to client"""
    if project and "embeddingsOfData" in project:
        project_copy = project.copy()
        del project_copy["embeddingsOfData"]
        return project_copy
    return project


class SimilaritySearchRequest(BaseModel):
    """Request model for similarity search"""
    query: str  # Can be project name, description, or general query
    top_k: int = 5
    min_similarity: float = 0.3


class SimilaritySearchByURLRequest(BaseModel):
    """Request model for finding similar projects by URL"""
    url: str
    top_k: int = 5


class SimilarityResponse(BaseModel):
    """Response model for similarity search"""
    status: str
    message: str
    results: List[Dict]
    count: int
    ai_verdict: Optional[Dict] = None  # AI-powered analysis verdict


@router.post("/search", response_model=SimilarityResponse)
async def similarity_search(request: SimilaritySearchRequest):
    """
    Find similar projects based on a text query
    
    Args:
        query: Text description to search for
        top_k: Number of results to return
        min_similarity: Minimum similarity score (0-1)
    
    Returns:
        List of similar projects with similarity scores
    """
    try:
        logger.info(f"Similarity search query: '{request.query[:50]}...'")
        
        # Generate embedding for the query
        query_embedding = await embedding_service.generate_query_embedding(request.query)
        
        # Perform vector search
        results = await mongodb_client.vector_search(
            query_embedding,
            top_k=request.top_k
        )
        
        # Filter by minimum similarity
        filtered_results = [
            r for r in results 
            if r.get("similarity_score", 0) >= request.min_similarity
        ]
        
        # Remove embeddings from results
        filtered_results = [remove_embeddings(r) for r in filtered_results]
        
        # Generate AI verdict using RAG
        # Create a synthetic input project from the query
        query_project = {
            "nameOfProject": "Search Query",
            "descriptionOfProject": request.query,
            "technologiesUsedInProject": [],
            "tagsOfProject": []
        }
        ai_verdict = await ai_intelligence_service.generate_similarity_verdict(
            query_project,
            filtered_results
        )
        
        logger.info(f"Found {len(filtered_results)} similar projects")
        
        return SimilarityResponse(
            status="success",
            message=f"Found {len(filtered_results)} similar projects",
            results=filtered_results,
            count=len(filtered_results),
            ai_verdict=ai_verdict
        )
    
    except Exception as e:
        logger.error(f"Error in similarity search: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error performing similarity search: {str(e)}"
        )


@router.post("/search-by-url", response_model=SimilarityResponse)
async def similarity_search_by_url(request: SimilaritySearchByURLRequest):
    """
    Find similar projects based on an existing project URL
    
    Args:
        url: URL of the project to find similar projects for
        top_k: Number of results to return
    
    Returns:
        List of similar projects
    """
    try:
        logger.info(f"Finding similar projects for: {request.url}")
        
        # Get the project from database
        project = await mongodb_client.get_project_by_url(request.url)
        
        if not project:
            raise HTTPException(
                status_code=404,
                detail="Project not found in database"
            )
        
        # Check if project has embeddings
        if not project.get("embeddingsOfData"):
            raise HTTPException(
                status_code=400,
                detail="Project does not have embeddings. Please generate embeddings first."
            )
        
        # Perform vector search
        results = await mongodb_client.vector_search(
            project["embeddingsOfData"],
            top_k=request.top_k + 1  # Get one extra to filter out the current project
        )
        
        # Remove the current project from results
        filtered_results = [
            r for r in results 
            if r["urlOfProject"] != request.url
        ][:request.top_k]
        
        # Remove embeddings from results
        filtered_results = [remove_embeddings(r) for r in filtered_results]
        
        # Generate AI verdict using RAG
        input_project_clean = remove_embeddings(project)
        ai_verdict = await ai_intelligence_service.generate_similarity_verdict(
            input_project_clean,
            filtered_results
        )
        
        logger.info(f"Found {len(filtered_results)} similar projects")
        
        return SimilarityResponse(
            status="success",
            message=f"Found {len(filtered_results)} similar projects",
            results=filtered_results,
            count=len(filtered_results),
            ai_verdict=ai_verdict
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in similarity search by URL: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error performing similarity search: {str(e)}"
        )


@router.post("/find-by-project")
async def find_similar_by_project_data(project_data: Dict):
    """
    Find similar projects based on project data (without storing it)
    Useful for finding similar projects before scraping/storing
    """
    try:
        logger.info("Finding similar projects for provided project data")
        
        # Generate embedding for the provided project data
        embedding = await embedding_service.generate_project_embedding(project_data)
        
        # Perform vector search
        results = await mongodb_client.vector_search(embedding, top_k=5)
        
        # Remove embeddings from results
        results = [remove_embeddings(r) for r in results]
        
        # Generate AI verdict using RAG
        ai_verdict = await ai_intelligence_service.generate_similarity_verdict(
            project_data,
            results
        )
        
        return SimilarityResponse(
            status="success",
            message=f"Found {len(results)} similar projects",
            results=results,
            count=len(results),
            ai_verdict=ai_verdict
        )
    
    except Exception as e:
        logger.error(f"Error finding similar projects: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error finding similar projects: {str(e)}"
        )


@router.get("/stats")
async def get_similarity_stats():
    """Get statistics about the database for similarity search"""
    try:
        total_projects = await mongodb_client.get_total_projects()
        projects_with_embeddings = await mongodb_client.get_projects_with_embeddings_count()
        
        return {
            "status": "success",
            "total_projects": total_projects,
            "projects_with_embeddings": projects_with_embeddings,
            "projects_without_embeddings": total_projects - projects_with_embeddings,
            "embedding_dimension": settings.EMBEDDING_DIMENSION,
            "model": settings.EMBEDDING_MODEL_NAME
        }
    
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting statistics: {str(e)}"
        )
