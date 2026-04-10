"""MongoDB service for database operations"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo.server_api import ServerApi
from typing import List, Dict, Optional, Any
import logging
from datetime import datetime

from core.config import settings

logger = logging.getLogger("DevFoolU.mongodb")


class MongoDBClient:
    """MongoDB client for async operations"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
        self.collection: Optional[AsyncIOMotorCollection] = None
        self._connected = False
    
    async def connect(self):
        """Connect to MongoDB"""
        try:
            logger.info("Connecting to MongoDB...")
            
            self.client = AsyncIOMotorClient(
                settings.MONGODB_URL,
                server_api=ServerApi('1'),
                serverSelectionTimeoutMS=settings.MONGODB_TIMEOUT,
                connectTimeoutMS=settings.MONGODB_TIMEOUT,
                socketTimeoutMS=None,
                tls=True,
                tlsAllowInvalidCertificates=False
            )
            
            # Test connection
            await self.client.admin.command('ping')
            
            self.db = self.client[settings.MONGODB_DATABASE]
            self.collection = self.db[settings.MONGODB_COLLECTION]
            
            self._connected = True
            logger.info(f"✅ Connected to MongoDB database: {settings.MONGODB_DATABASE}")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            raise
    
    async def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            self._connected = False
            logger.info("MongoDB connection closed")
    
    async def ping(self):
        """Ping MongoDB to check connection"""
        if not self.client:
            raise Exception("MongoDB client not initialized")
        await self.client.admin.command('ping')
    
    def is_connected(self) -> bool:
        """Check if connected to MongoDB"""
        return self._connected
    
    async def project_exists(self, url: str) -> bool:
        """Check if a project with the given URL already exists"""
        try:
            count = await self.collection.count_documents({"urlOfProject": url})
            return count > 0
        except Exception as e:
            logger.error(f"Error checking project existence: {e}")
            return False
    
    async def get_project_by_url(self, url: str) -> Optional[Dict]:
        """Get a project by its URL"""
        try:
            project = await self.collection.find_one({"urlOfProject": url})
            if project:
                # Convert ObjectId to string for JSON serialization
                project["_id"] = str(project["_id"])
            return project
        except Exception as e:
            logger.error(f"Error fetching project: {e}")
            return None
    
    async def insert_project(self, project_data: Dict) -> Optional[str]:
        """Insert a new project into the database"""
        try:
            # Check if project already exists
            if await self.project_exists(project_data["urlOfProject"]):
                logger.warning(f"Project already exists: {project_data['urlOfProject']}")
                return None
            
            # Add metadata
            project_data["createdAt"] = datetime.utcnow()
            project_data["updatedAt"] = datetime.utcnow()
            
            result = await self.collection.insert_one(project_data)
            logger.info(f"✅ Inserted project: {project_data['nameOfProject']}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error inserting project: {e}")
            raise
    
    async def update_project_embeddings(self, url: str, embeddings: List[float]) -> bool:
        """Update embeddings for a project"""
        try:
            result = await self.collection.update_one(
                {"urlOfProject": url},
                {
                    "$set": {
                        "embeddingsOfData": embeddings,
                        "updatedAt": datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count > 0:
                logger.info(f"✅ Updated embeddings for: {url}")
                return True
            else:
                logger.warning(f"No project found to update embeddings: {url}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating embeddings: {e}")
            return False
    
    async def get_projects_without_embeddings(self, limit: Optional[int] = None) -> List[Dict]:
        """Get projects that don't have embeddings"""
        try:
            query = {
                "$or": [
                    {"embeddingsOfData": {"$exists": False}},
                    {"embeddingsOfData": []},
                    {"embeddingsOfData": None}
                ]
            }
            
            cursor = self.collection.find(query)
            if limit:
                cursor = cursor.limit(limit)
            
            projects = await cursor.to_list(length=None)
            
            # Convert ObjectId to string
            for project in projects:
                project["_id"] = str(project["_id"])
            
            return projects
            
        except Exception as e:
            logger.error(f"Error fetching projects without embeddings: {e}")
            return []
    
    async def vector_search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict]:
        """
        Perform vector similarity search
        Note: This is a basic implementation. For production, use MongoDB Atlas Vector Search
        """
        try:
            # Get all projects with embeddings
            projects = await self.collection.find({
                "embeddingsOfData": {"$exists": True, "$ne": []}
            }).to_list(length=None)
            
            if not projects:
                return []
            
            # Calculate cosine similarity for each project
            from numpy import dot
            from numpy.linalg import norm
            
            similarities = []
            for project in projects:
                if "embeddingsOfData" in project and project["embeddingsOfData"]:
                    # Cosine similarity
                    similarity = dot(query_embedding, project["embeddingsOfData"]) / (
                        norm(query_embedding) * norm(project["embeddingsOfData"])
                    )
                    
                    project["_id"] = str(project["_id"])
                    project["similarity_score"] = float(similarity)
                    similarities.append(project)
            
            # Sort by similarity score
            similarities.sort(key=lambda x: x["similarity_score"], reverse=True)
            
            # Return top K
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"Error performing vector search: {e}")
            return []
    
    async def bulk_insert_projects(self, projects: List[Dict]) -> Dict[str, int]:
        """Bulk insert projects, skipping duplicates"""
        try:
            inserted_count = 0
            duplicate_count = 0
            failed_count = 0
            
            for project in projects:
                try:
                    # Check if exists
                    if await self.project_exists(project["urlOfProject"]):
                        duplicate_count += 1
                        logger.debug(f"⊘ Skipping duplicate: {project['urlOfProject']}")
                        continue
                    
                    # Add metadata
                    project["createdAt"] = datetime.utcnow()
                    project["updatedAt"] = datetime.utcnow()
                    
                    await self.collection.insert_one(project)
                    inserted_count += 1
                    
                except Exception as e:
                    logger.error(f"Error inserting project {project.get('urlOfProject')}: {e}")
                    failed_count += 1
            
            return {
                "inserted": inserted_count,
                "duplicates": duplicate_count,
                "failed": failed_count
            }
            
        except Exception as e:
            logger.error(f"Error in bulk insert: {e}")
            raise
    
    async def get_total_projects(self) -> int:
        """Get total number of projects"""
        try:
            return await self.collection.count_documents({})
        except Exception as e:
            logger.error(f"Error counting projects: {e}")
            return 0
    
    async def get_projects_with_embeddings_count(self) -> int:
        """Get count of projects with embeddings"""
        try:
            return await self.collection.count_documents({
                "embeddingsOfData": {"$exists": True, "$ne": []}
            })
        except Exception as e:
            logger.error(f"Error counting projects with embeddings: {e}")
            return 0


# Global MongoDB client instance
mongodb_client = MongoDBClient()
