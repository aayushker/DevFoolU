"""Router for finding similar projects by URL (with auto-scraping if needed)"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Dict, List
import logging

from services.scraper import scraper_service
from services.embedding import embedding_service
from services.mongodb import mongodb_client

logger = logging.getLogger("DevFoolU.routers.scraper")

router = APIRouter()


class FindSimilarRequest(BaseModel):
    """Request model for finding similar projects"""
    url: HttpUrl


class FindSimilarResponse(BaseModel):
    """Response model for finding similar projects"""
    status: str
    message: str
    project: Dict
    similar_projects: List[Dict]
    was_scraped: bool = False  # Indicates if the project was newly scraped


def remove_embeddings(project: Dict) -> Dict:
    """Remove embeddings from project data before returning to client"""
    if project and "embeddingsOfData" in project:
        project_copy = project.copy()
        del project_copy["embeddingsOfData"]
        return project_copy
    return project


@router.post("/find-similar", response_model=FindSimilarResponse)
async def find_similar_projects(request: FindSimilarRequest):
    """
    Find similar projects for a given project URL
    
    Workflow:
    1. Check if project exists in database
    2. If exists: Get project data and perform vector similarity search
    3. If not exists: 
       - Scrape the project
       - Generate embeddings
       - Store in database
       - Perform vector similarity search
    4. Return project + top 5 similar projects (without embeddings)
    """
    try:
        url = str(request.url)
        logger.info(f"Finding similar projects for: {url}")
        
        # Step 1: Check if project exists in database
        project = await mongodb_client.get_project_by_url(url)
        was_scraped = False
        
        if project:
            # Project exists in database
            logger.info(f"Project found in database: {url}")
            
            # Check if it has embeddings
            if not project.get("embeddingsOfData") or len(project.get("embeddingsOfData", [])) == 0:
                logger.warning(f"Project exists but has no embeddings: {url}")
                raise HTTPException(
                    status_code=400,
                    detail="Project exists in database but has no embeddings. Please generate embeddings first using /api/bulk/generate-embeddings endpoint."
                )
        else:
            # Project doesn't exist - need to scrape it
            logger.info(f"Project not in database. Scraping: {url}")
            was_scraped = True
            
            # Scrape the project
            project_data = await scraper_service.scrape_single_project(url)
            
            if not project_data:
                raise HTTPException(
                    status_code=400,
                    detail="Failed to scrape project. Please check the URL and try again."
                )
            
            logger.info(f"Successfully scraped: {project_data.get('nameOfProject', 'Unknown')}")
            
            # Generate embeddings
            logger.info("Generating embeddings for scraped project...")
            embeddings = await embedding_service.generate_project_embedding(project_data)
            project_data["embeddingsOfData"] = embeddings
            
            # Store in database
            logger.info("Storing project in database...")
            try:
                project_id = await mongodb_client.insert_project(project_data)
                if project_id:
                    project_data["_id"] = project_id
                    logger.info(f"✅ Project stored with ID: {project_id}")
            except Exception as e:
                logger.error(f"Error storing project: {e}")
                # Continue even if storage fails
            
            project = project_data
        
        # Step 2: Perform vector similarity search
        logger.info("Performing vector similarity search...")
        similar_projects = await mongodb_client.vector_search(
            project["embeddingsOfData"],
            top_k=6  # Get 6, then filter out the current project
        )
        
        # Remove the current project from results and limit to top 5
        similar_projects = [
            p for p in similar_projects 
            if p.get("urlOfProject") != url
        ][:5]
        
        logger.info(f"Found {len(similar_projects)} similar projects")
        
        # Step 3: Remove embeddings from all projects before returning
        project_without_embeddings = remove_embeddings(project)
        similar_without_embeddings = [remove_embeddings(p) for p in similar_projects]
        
        return FindSimilarResponse(
            status="success",
            message=f"Found {len(similar_without_embeddings)} similar projects",
            project=project_without_embeddings,
            similar_projects=similar_without_embeddings,
            was_scraped=was_scraped
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error finding similar projects: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/scrape", response_model=FindSimilarResponse)
async def scrape_project(request: FindSimilarRequest):
    """
    Legacy endpoint - redirects to find-similar
    Kept for backward compatibility
    """
    return await find_similar_projects(request)


@router.get("/validate-url")
async def validate_url(url: str):
    """Validate if a URL is a valid Devfolio project URL"""
    try:
        if not url.startswith("https://devfolio.co/projects/"):
            return {
                "valid": False,
                "message": "URL must be a Devfolio project URL (https://devfolio.co/projects/...)"
            }
        
        return {
            "valid": True,
            "message": "Valid Devfolio project URL"
        }
    except Exception as e:
        return {
            "valid": False,
            "message": str(e)
        }
