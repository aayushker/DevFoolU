"""
Example: Protected Scraper Endpoint
Shows how to add user tracking to scraped projects
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Optional
from pydantic import BaseModel, HttpUrl
from datetime import datetime

from services.auth0 import get_current_user, get_current_user_optional
from services.scraper import scraper_service
from services.mongodb import mongodb_client

router = APIRouter()


class ScrapeRequest(BaseModel):
    url: HttpUrl


@router.post("/scrape-authenticated")
async def scrape_with_user_tracking(
    request: ScrapeRequest,
    user: Dict = Depends(get_current_user)
):
    """
    Scrape a project and associate it with the authenticated user
    Requires authentication
    """
    try:
        # Get user information
        user_id = user.get("sub")
        user_email = user.get("email")
        
        # Scrape the project
        project_data = await scraper_service.scrape_project(str(request.url))
        
        # Add user tracking information
        project_data["scraped_by"] = {
            "user_id": user_id,
            "email": user_email,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Save to database with user association
        result = await mongodb_client.save_project(project_data)
        
        return {
            "status": "success",
            "message": "Project scraped and saved",
            "project": project_data,
            "user": {
                "id": user_id,
                "email": user_email
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scrape-optional-auth")
async def scrape_with_optional_tracking(
    request: ScrapeRequest,
    user: Optional[Dict] = Depends(get_current_user_optional)
):
    """
    Scrape a project with optional user tracking
    Works for both authenticated and anonymous users
    """
    try:
        # Scrape the project
        project_data = await scraper_service.scrape_project(str(request.url))
        
        # Add user tracking if authenticated
        if user:
            project_data["scraped_by"] = {
                "user_id": user.get("sub"),
                "email": user.get("email"),
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            project_data["scraped_by"] = {
                "anonymous": True,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Save to database
        result = await mongodb_client.save_project(project_data)
        
        response = {
            "status": "success",
            "message": "Project scraped and saved",
            "project": project_data
        }
        
        if user:
            response["user"] = {
                "id": user.get("sub"),
                "email": user.get("email")
            }
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/my-scrapes")
async def get_user_scrapes(user: Dict = Depends(get_current_user)):
    """
    Get all projects scraped by the authenticated user
    Requires authentication
    """
    user_id = user.get("sub")
    
    # Query database for user's scrapes
    projects = await mongodb_client.find_projects({
        "scraped_by.user_id": user_id
    })
    
    return {
        "status": "success",
        "count": len(projects),
        "projects": projects,
        "user": {
            "id": user_id,
            "email": user.get("email")
        }
    }


@router.get("/scrape-history")
async def get_scrape_history(
    limit: int = 10,
    user: Optional[Dict] = Depends(get_current_user_optional)
):
    """
    Get scrape history - personalized if authenticated, general if not
    Works for both authenticated and anonymous users
    """
    if user:
        # Get user-specific history
        user_id = user.get("sub")
        projects = await mongodb_client.find_projects(
            {"scraped_by.user_id": user_id},
            limit=limit,
            sort=[("scraped_by.timestamp", -1)]
        )
        return {
            "status": "success",
            "type": "personalized",
            "count": len(projects),
            "projects": projects,
            "user": {
                "id": user_id,
                "email": user.get("email")
            }
        }
    else:
        # Get general recent scrapes
        projects = await mongodb_client.find_projects(
            {},
            limit=limit,
            sort=[("created_at", -1)]
        )
        return {
            "status": "success",
            "type": "general",
            "count": len(projects),
            "projects": projects
        }
