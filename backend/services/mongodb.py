"""MongoDB service for database operations"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo.server_api import ServerApi
from pymongo import UpdateOne
from typing import List, Dict, Optional, Any
import logging
from datetime import datetime, timedelta

from core.config import settings

logger = logging.getLogger("DevFoolU.mongodb")


class MongoDBClient:
    """MongoDB client for async operations"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
        self.collection: Optional[AsyncIOMotorCollection] = None
        self.ingest_jobs_collection: Optional[AsyncIOMotorCollection] = None
        self.ingest_urls_collection: Optional[AsyncIOMotorCollection] = None
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
            self.ingest_jobs_collection = self.db[settings.MONGODB_INGEST_JOBS_COLLECTION]
            self.ingest_urls_collection = self.db[settings.MONGODB_INGEST_URLS_COLLECTION]

            await self._ensure_indexes()
            
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

    @staticmethod
    def _canonicalize_url(url: str) -> str:
        """Normalize URL representation for stable identity checks."""
        cleaned = str(url or "").strip()
        if not cleaned:
            return ""
        cleaned = cleaned.split("?")[0].split("#")[0].strip()
        if cleaned.endswith("/"):
            cleaned = cleaned[:-1]
        return cleaned

    @staticmethod
    def _normalize_technologies(value: Any) -> List[str]:
        """Normalize technologies field to a list of strings."""
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return []

    def _normalize_project_document(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize project document shape for strict schema collections."""
        normalized = {k: v for k, v in project_data.items() if k != "_id"}

        normalized["urlOfProject"] = self._canonicalize_url(normalized.get("urlOfProject", ""))
        normalized["nameOfProject"] = str(normalized.get("nameOfProject", "")).strip()
        normalized["descriptionOfProject"] = str(normalized.get("descriptionOfProject", "")).strip()
        normalized["problemSolved"] = str(normalized.get("problemSolved", "")).strip()
        normalized["challengesFaced"] = str(normalized.get("challengesFaced", "")).strip()
        normalized["technologiesUsed"] = self._normalize_technologies(normalized.get("technologiesUsed"))

        embeddings = normalized.get("embeddingsOfData")
        if not isinstance(embeddings, list):
            normalized["embeddingsOfData"] = []

        return normalized

    async def get_project_urls_set(self) -> set[str]:
        """Fetch all known project URLs as a normalized set."""
        urls: set[str] = set()
        cursor = self.collection.find({}, {"urlOfProject": 1})
        async for doc in cursor:
            canonical = self._canonicalize_url(doc.get("urlOfProject", ""))
            if canonical:
                urls.add(canonical)
        return urls

    async def get_existing_project_urls_in_list(self, urls: List[str], chunk_size: int = 1000) -> set[str]:
        """Return subset of URLs that already exist in project collection."""
        existing: set[str] = set()
        canonical_urls: List[str] = []
        for url in urls:
            canonical = self._canonicalize_url(url)
            if canonical:
                canonical_urls.append(canonical)
        if not canonical_urls:
            return existing

        for idx in range(0, len(canonical_urls), chunk_size):
            chunk = canonical_urls[idx : idx + chunk_size]
            rows = await self.collection.find(
                {"urlOfProject": {"$in": chunk}},
                {"urlOfProject": 1},
            ).to_list(length=None)
            for row in rows:
                canonical = self._canonicalize_url(row.get("urlOfProject", ""))
                if canonical:
                    existing.add(canonical)

        return existing

    async def _ensure_indexes(self):
        """Create indexes used by core and ingestion workflows."""
        if (
            self.collection is None
            or self.ingest_jobs_collection is None
            or self.ingest_urls_collection is None
        ):
            return

        try:
            await self.collection.create_index("urlOfProject", unique=True)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Could not create unique index on urlOfProject: %s", exc)
        await self.collection.create_index("updatedAt")
        await self.collection.create_index("embeddingsOfData")

        await self.ingest_jobs_collection.create_index("createdAt")
        await self.ingest_jobs_collection.create_index("status")

        await self.ingest_urls_collection.create_index(
            [("jobId", 1), ("url", 1)],
            unique=True,
        )
        await self.ingest_urls_collection.create_index(
            [("jobId", 1), ("state", 1), ("nextRetryAt", 1)]
        )
    
    async def project_exists(self, url: str) -> bool:
        """Check if a project with the given URL already exists"""
        try:
            canonical_url = self._canonicalize_url(url)
            count = await self.collection.count_documents({"urlOfProject": canonical_url})
            return count > 0
        except Exception as e:
            logger.error(f"Error checking project existence: {e}")
            return False
    
    async def get_project_by_url(self, url: str) -> Optional[Dict]:
        """Get a project by its URL"""
        try:
            canonical_url = self._canonicalize_url(url)
            project = await self.collection.find_one({"urlOfProject": canonical_url})
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
            project_data = self._normalize_project_document(project_data)

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
                    project = self._normalize_project_document(project)

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

    async def bulk_upsert_projects(self, projects: List[Dict]) -> Dict[str, int]:
        """Bulk upsert projects by URL identity for refresh-friendly ingestion."""
        try:
            if not projects:
                return {
                    "upserted": 0,
                    "modified": 0,
                    "matched": 0,
                    "failed": 0,
                }

            now = datetime.utcnow()
            operations = []
            failed = 0

            for project in projects:
                url = project.get("urlOfProject")
                if not url:
                    failed += 1
                    continue

                project_data = self._normalize_project_document(project)
                project_data["updatedAt"] = now

                operations.append(
                    UpdateOne(
                        {"urlOfProject": url},
                        {
                            "$set": project_data,
                            "$setOnInsert": {"createdAt": now},
                        },
                        upsert=True,
                    )
                )

            if not operations:
                return {
                    "upserted": 0,
                    "modified": 0,
                    "matched": 0,
                    "failed": failed,
                }

            result = await self.collection.bulk_write(operations, ordered=False)
            return {
                "upserted": len(result.upserted_ids) if result.upserted_ids else 0,
                "modified": result.modified_count,
                "matched": result.matched_count,
                "failed": failed,
            }

        except Exception as e:
            logger.error(f"Error in bulk upsert: {e}")
            raise

    async def create_ingest_job(
        self,
        job_id: str,
        mode: str,
        target_projects: int,
        config_snapshot: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create a persisted ingestion job."""
        now = datetime.utcnow()
        job_doc = {
            "_id": job_id,
            "mode": mode,
            "status": "running",
            "targetProjects": target_projects,
            "stats": {
                "discovered": 0,
                "processed": 0,
                "succeeded": 0,
                "failed": 0,
                "upserted": 0,
                "modified": 0,
                "embeddingsGenerated": 0,
                "qosSlowdowns": 0,
                "skippedExisting": 0,
                "problemCaptured": 0,
                "challengesCaptured": 0,
            },
            "config": config_snapshot,
            "createdAt": now,
            "startedAt": now,
            "heartbeatAt": now,
            "updatedAt": now,
            "lastError": None,
        }

        await self.ingest_jobs_collection.update_one(
            {"_id": job_id},
            {"$setOnInsert": job_doc},
            upsert=True,
        )
        return await self.get_ingest_job(job_id)

    async def update_ingest_job(
        self,
        job_id: str,
        set_fields: Optional[Dict[str, Any]] = None,
        inc_fields: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Update ingest job fields and counters."""
        update_payload: Dict[str, Any] = {}
        set_data = set_fields.copy() if set_fields else {}
        set_data["updatedAt"] = datetime.utcnow()

        if set_data:
            update_payload["$set"] = set_data
        if inc_fields:
            update_payload["$inc"] = inc_fields

        if update_payload:
            await self.ingest_jobs_collection.update_one(
                {"_id": job_id},
                update_payload,
            )

    async def get_ingest_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Fetch one ingest job by id."""
        return await self.ingest_jobs_collection.find_one({"_id": job_id})

    async def list_ingest_jobs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """List recent ingest jobs."""
        return await self.ingest_jobs_collection.find().sort("createdAt", -1).limit(limit).to_list(length=limit)

    async def seed_ingest_job_urls(
        self,
        job_id: str,
        urls: List[str],
        skip_existing_projects: bool = True,
    ) -> Dict[str, int]:
        """Seed URL frontier for a job, optionally skipping URLs already in project collection."""
        if not urls:
            return {"seeded": 0, "total": 0, "eligible": 0, "skipped_existing": 0}

        canonical_urls = []
        seen_urls: set[str] = set()
        for url in urls:
            canonical = self._canonicalize_url(url)
            if not canonical or canonical in seen_urls:
                continue
            seen_urls.add(canonical)
            canonical_urls.append(canonical)

        if not canonical_urls:
            return {"seeded": 0, "total": len(urls), "eligible": 0, "skipped_existing": 0}

        skipped_existing = 0
        eligible_urls = canonical_urls
        if skip_existing_projects:
            existing_urls = await self.get_existing_project_urls_in_list(canonical_urls)
            skipped_existing = len(existing_urls)
            eligible_urls = [url for url in canonical_urls if url not in existing_urls]

        now = datetime.utcnow()
        operations = [
            UpdateOne(
                {"jobId": job_id, "url": url},
                {
                    "$setOnInsert": {
                        "jobId": job_id,
                        "url": url,
                        "state": "pending",
                        "attempts": 0,
                        "createdAt": now,
                        "updatedAt": now,
                        "nextRetryAt": now,
                        "lastError": None,
                    }
                },
                upsert=True,
            )
            for url in eligible_urls
        ]

        if not operations:
            return {
                "seeded": 0,
                "total": len(canonical_urls),
                "eligible": len(eligible_urls),
                "skipped_existing": skipped_existing,
            }

        result = await self.ingest_urls_collection.bulk_write(operations, ordered=False)
        return {
            "seeded": len(result.upserted_ids) if result.upserted_ids else 0,
            "total": len(canonical_urls),
            "eligible": len(eligible_urls),
            "skipped_existing": skipped_existing,
        }

    async def fetch_ingest_job_urls_for_processing(
        self,
        job_id: str,
        limit: int,
        max_attempts: int,
    ) -> List[str]:
        """Fetch pending URLs and mark them as processing."""
        now = datetime.utcnow()
        query = {
            "jobId": job_id,
            "$or": [
                {"state": "pending"},
                {
                    "state": "failed",
                    "attempts": {"$lt": max_attempts},
                    "nextRetryAt": {"$lte": now},
                },
            ],
        }

        docs = await self.ingest_urls_collection.find(query).sort(
            [("attempts", 1), ("updatedAt", 1)]
        ).limit(limit).to_list(length=limit)

        urls = [doc["url"] for doc in docs]
        if not urls:
            return []

        await self.ingest_urls_collection.update_many(
            {"jobId": job_id, "url": {"$in": urls}},
            {
                "$set": {
                    "state": "processing",
                    "updatedAt": now,
                }
            },
        )
        return urls

    async def mark_ingest_urls_succeeded(self, job_id: str, urls: List[str]) -> None:
        """Mark URL batch as succeeded."""
        if not urls:
            return

        await self.ingest_urls_collection.update_many(
            {"jobId": job_id, "url": {"$in": urls}},
            {
                "$set": {
                    "state": "succeeded",
                    "updatedAt": datetime.utcnow(),
                    "lastError": None,
                }
            },
        )

    async def mark_ingest_urls_failed(
        self,
        job_id: str,
        urls: List[str],
        backoff_base_seconds: float,
        backoff_max_seconds: float,
        error_message: str = "scrape_failed",
        error_by_url: Optional[Dict[str, str]] = None,
    ) -> None:
        """Mark URL batch as failed and schedule retry using exponential backoff."""
        if not urls:
            return

        existing_docs = await self.ingest_urls_collection.find(
            {"jobId": job_id, "url": {"$in": urls}},
            {"url": 1, "attempts": 1},
        ).to_list(length=None)
        attempts_map = {doc["url"]: int(doc.get("attempts", 0)) for doc in existing_docs}

        now = datetime.utcnow()
        operations = []
        for url in urls:
            attempts = attempts_map.get(url, 0) + 1
            delay_seconds = min(backoff_max_seconds, backoff_base_seconds * (2 ** max(0, attempts - 1)))
            next_retry_at = now + timedelta(seconds=delay_seconds)
            operations.append(
                UpdateOne(
                    {"jobId": job_id, "url": url},
                    {
                        "$set": {
                            "state": "failed",
                            "attempts": attempts,
                            "nextRetryAt": next_retry_at,
                            "updatedAt": now,
                            "lastError": (
                                (error_by_url or {}).get(url, error_message)[:240]
                                if isinstance((error_by_url or {}).get(url, error_message), str)
                                else error_message
                            ),
                        }
                    },
                    upsert=False,
                )
            )

        if operations:
            await self.ingest_urls_collection.bulk_write(operations, ordered=False)

    async def reset_processing_urls(self, job_id: str) -> None:
        """Reset in-flight URLs to pending, used after crashes/restarts."""
        await self.ingest_urls_collection.update_many(
            {"jobId": job_id, "state": "processing"},
            {"$set": {"state": "pending", "updatedAt": datetime.utcnow()}},
        )

    async def get_ingest_url_state_counts(self, job_id: str) -> Dict[str, int]:
        """Return URL counts grouped by state for a job."""
        pipeline = [
            {"$match": {"jobId": job_id}},
            {"$group": {"_id": "$state", "count": {"$sum": 1}}},
        ]
        rows = await self.ingest_urls_collection.aggregate(pipeline).to_list(length=None)
        counts = {"pending": 0, "processing": 0, "succeeded": 0, "failed": 0}
        for row in rows:
            counts[str(row.get("_id", "pending"))] = int(row.get("count", 0))
        return counts

    async def count_ingest_urls(self, job_id: str) -> int:
        """Count how many URLs are tracked for a given ingestion job."""
        return await self.ingest_urls_collection.count_documents({"jobId": job_id})

    async def get_retriable_failed_count(self, job_id: str, max_attempts: int) -> int:
        """Count failed URLs that can still be retried."""
        return await self.ingest_urls_collection.count_documents(
            {
                "jobId": job_id,
                "state": "failed",
                "attempts": {"$lt": max_attempts},
            }
        )

    async def get_next_retry_at(self, job_id: str, max_attempts: int) -> Optional[datetime]:
        """Fetch the earliest next retry timestamp for retriable failed URLs."""
        doc = await self.ingest_urls_collection.find_one(
            {
                "jobId": job_id,
                "state": "failed",
                "attempts": {"$lt": max_attempts},
            },
            sort=[("nextRetryAt", 1)],
            projection={"nextRetryAt": 1},
        )
        if not doc:
            return None
        return doc.get("nextRetryAt")
    
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
