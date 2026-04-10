"""
Auth0 Authentication Service
Handles JWT token verification and user authentication using Auth0
"""

from typing import Optional, Dict
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import httpx
from functools import lru_cache
from core.config import settings
from core.logger import setup_logging

logger = setup_logging()

security = HTTPBearer()


class Auth0Service:
    """Auth0 authentication service"""
    
    def __init__(self):
        self.domain = settings.AUTH0_DOMAIN
        self.api_audience = settings.AUTH0_API_AUDIENCE
        self.issuer = settings.AUTH0_ISSUER
        self.algorithms = settings.AUTH0_ALGORITHMS
        self._jwks_cache: Optional[Dict] = None
    
    async def get_jwks(self) -> Dict:
        """Fetch JWKS from Auth0"""
        if self._jwks_cache:
            return self._jwks_cache
        
        jwks_url = f"https://{self.domain}/.well-known/jwks.json"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(jwks_url, timeout=10.0)
                response.raise_for_status()
                self._jwks_cache = response.json()
                return self._jwks_cache
        except Exception as e:
            logger.error(f"Failed to fetch JWKS: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Unable to verify authentication"
            )
    
    async def verify_token(self, token: str) -> Dict:
        """Verify and decode Auth0 JWT token"""
        try:
            # Get JWKS
            jwks = await self.get_jwks()
            
            # Get the key ID from the token header
            unverified_header = jwt.get_unverified_header(token)
            rsa_key = {}
            
            # Find the matching key
            for key in jwks["keys"]:
                if key["kid"] == unverified_header["kid"]:
                    rsa_key = {
                        "kty": key["kty"],
                        "kid": key["kid"],
                        "use": key["use"],
                        "n": key["n"],
                        "e": key["e"]
                    }
                    break
            
            if not rsa_key:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Unable to find appropriate key"
                )
            
            # Verify and decode the token
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=[self.algorithms],
                audience=self.api_audience,
                issuer=self.issuer
            )
            
            return payload
            
        except JWTError as e:
            logger.error(f"JWT verification failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    async def get_current_user(
        self,
        credentials: HTTPAuthorizationCredentials = Security(security)
    ) -> Dict:
        """
        Dependency to get current authenticated user from token
        Use this in your protected endpoints
        """
        token = credentials.credentials
        payload = await self.verify_token(token)
        return payload


# Create a singleton instance
auth0_service = Auth0Service()


# Dependency function for FastAPI routes
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> Dict:
    """
    FastAPI dependency to get current authenticated user
    
    Usage in routes:
        @router.get("/protected")
        async def protected_route(user: Dict = Depends(get_current_user)):
            return {"user": user}
    """
    return await auth0_service.get_current_user(credentials)


# Optional: Dependency for optional authentication
async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
) -> Optional[Dict]:
    """
    Optional authentication - returns None if no token provided
    
    Usage in routes:
        @router.get("/optional-auth")
        async def optional_route(user: Optional[Dict] = Depends(get_current_user_optional)):
            if user:
                return {"message": "Authenticated", "user": user}
            return {"message": "Anonymous access"}
    """
    if not credentials:
        return None
    
    try:
        return await auth0_service.get_current_user(credentials)
    except HTTPException:
        return None
