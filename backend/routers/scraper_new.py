"""Router for finding similar projects by URL"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Dict, List
import logging

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
    1. Get the project from database by URL
    2. Check if it has embeddings
    3. Perform vector similarity search
    4. Return project data + top 5 similar projects (without embeddings)
    """
    try:
        url = str(request.url)
        logger.info(f"Finding similar projects for: {url}")
        
        # Step 1: Get project from database
        project = await mongodb_client.get_project_by_url(url)
        
        if not project:
            raise HTTPException(
                status_code=404,
                detail=f"Project not found in database: {url}"
            )
        
        # Step 2: Check if project has embeddings
        if not project.get("embeddingsOfData") or len(project.get("embeddingsOfData", [])) == 0:
            raise HTTPException(
                status_code=400,
                detail="Project does not have embeddings. Please generate embeddings first."
            )
        
        # Step 3: Find similar projects using vector search
        logger.info("Performing vector similarity search...")
        similar_projects = await mongodb_client.vector_search(
            project["embeddingsOfData"],
            top_k=6  # Get 6, then filter out the current project
        )
        
        # Remove the current project from results and limit to top 5
        similar_projects = [
            p for p in similar_projects 
            if p["urlOfProject"] != url
        ][:5]
        
        logger.info(f"Found {len(similar_projects)} similar projects")
        
        # Step 4: Remove embeddings from all projects before returning
        project_without_embeddings = remove_embeddings(project)
        similar_without_embeddings = [remove_embeddings(p) for p in similar_projects]
        
        return FindSimilarResponse(
            status="success",
            message=f"Found {len(similar_without_embeddings)} similar projects",
            project=project_without_embeddings,
            similar_projects=similar_without_embeddings
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error finding similar projects: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


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


@router.get("/check-exists")
async def check_project_exists(url: str):
    """Check if a project exists in the database"""
    try:
        exists = await mongodb_client.project_exists(url)
        
        if exists:
            project = await mongodb_client.get_project_by_url(url)
            has_embeddings = bool(project.get("embeddingsOfData"))
            
            return {
                "exists": True,
                "has_embeddings": has_embeddings,
                "message": "Project found in database"
            }
        else:
            return {
                "exists": False,
                "has_embeddings": False,
                "message": "Project not found in database"
            }
    
    except Exception as e:
        logger.error(f"Error checking project existence: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error checking project: {str(e)}"
        )
