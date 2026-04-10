"""
Auth0 Authentication Router
Handles user authentication and profile management using Auth0
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict
from services.auth0 import get_current_user, get_current_user_optional
from core.logger import setup_logging
from core.config import settings

logger = setup_logging()

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get("/me")
async def get_user_profile(user: Dict = Depends(get_current_user)):
    """
    Get current authenticated user profile
    Requires valid Auth0 token
    """
    return {
        "user": {
            "sub": user.get("sub"),
            "email": user.get("email"),
            "name": user.get("name"),
            "nickname": user.get("nickname"),
            "picture": user.get("picture"),
            "email_verified": user.get("email_verified"),
        }
    }


@router.get("/verify")
async def verify_token(user: Dict = Depends(get_current_user)):
    """
    Verify if the provided token is valid
    Returns basic user information
    """
    return {
        "valid": True,
        "user_id": user.get("sub"),
        "email": user.get("email")
    }


@router.get("/config")
async def get_auth_config():
    """
    Get Auth0 configuration for frontend
    Returns public Auth0 configuration
    """
    return {
        "domain": settings.AUTH0_DOMAIN,
        "audience": settings.AUTH0_API_AUDIENCE,
        "issuer": settings.AUTH0_ISSUER
    }

