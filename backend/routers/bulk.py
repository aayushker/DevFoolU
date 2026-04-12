"""Router for bulk scraping and processing operations"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Header
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging
import asyncio
import json
from datetime import datetime

from services.scraper import scraper_service
from services.embedding import embedding_service
from services.mongodb import mongodb_client
from services.mass_ingestor import mass_ingestor_service
from core.config import settings

logger = logging.getLogger("DevFoolU.routers.bulk")

router = APIRouter()


class BulkScrapeRequest(BaseModel):
    """Request model for bulk scraping"""
    limit: int = 100
    generate_embeddings: bool = True
    store_projects: bool = True


class BulkScrapeResponse(BaseModel):
    """Response model for bulk scrape"""
    status: str
    message: str
    total_scraped: int
    total_failed: int
    total_stored: int
    duplicates: int


class GenerateEmbeddingsRequest(BaseModel):
    """Request model for generating embeddings"""
    limit: Optional[int] = None  # None = all projects without embeddings


class GenerateEmbeddingsResponse(BaseModel):
    """Response model for embedding generation"""
    status: str
    message: str
    processed: int
    updated: int
    failed: int


class MassIngestStartRequest(BaseModel):
    """Request model for starting mass ingestion."""
    mode: str = "backfill"  # backfill | incremental
    target_projects: Optional[int] = None


class MassIngestControlResponse(BaseModel):
    """Response model for ingestion control actions."""
    status: str
    message: str
    job_id: Optional[str] = None


# Background task storage
background_tasks_status = {}


def _validate_admin_token(x_admin_token: Optional[str] = Header(default=None)):
    """Require admin token only when configured."""
    if settings.MASS_INGEST_ADMIN_TOKEN and x_admin_token != settings.MASS_INGEST_ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid admin token")


@router.post("/scrape-stream")
async def bulk_scrape_stream(request: BulkScrapeRequest):
    """
    Bulk scrape projects with real-time progress updates via SSE
    """
    async def event_generator():
        task_id = datetime.now().strftime("%Y%m%d%H%M%S")
        
        try:
            # Initialize status
            yield f"data: {json.dumps({'status': 'started', 'message': 'Starting bulk scrape', 'progress': 0, 'task_id': task_id})}\n\n"
            
            # Scrape projects
            yield f"data: {json.dumps({'status': 'scraping', 'message': 'Collecting project URLs...', 'progress': 10})}\n\n"
            
            projects, failures = await scraper_service.scrape_bulk_projects(
                limit=request.limit
            )
            
            if not projects:
                yield f"data: {json.dumps({'status': 'error', 'message': 'No projects scraped'})}\n\n"
                return
            
            yield f"data: {json.dumps({'status': 'scraped', 'message': f'Scraped {len(projects)} projects', 'progress': 50, 'total': len(projects), 'failed': len(failures)})}\n\n"
            
            # Generate embeddings
            if request.generate_embeddings:
                yield f"data: {json.dumps({'status': 'generating_embeddings', 'message': 'Generating embeddings...', 'progress': 60})}\n\n"
                
                for idx, project in enumerate(projects):
                    try:
                        embeddings = await embedding_service.generate_project_embedding(project)
                        project["embeddingsOfData"] = embeddings
                        
                        progress = 60 + (30 * (idx + 1) / len(projects))
                        if (idx + 1) % 10 == 0:  # Update every 10 projects
                            yield f"data: {json.dumps({'status': 'generating_embeddings', 'message': f'Generated embeddings for {idx + 1}/{len(projects)} projects', 'progress': progress})}\n\n"
                    
                    except Exception as e:
                        logger.error(f"Error generating embedding: {e}")
                        project["embeddingsOfData"] = []
            
            # Store projects
            stored = 0
            duplicates = 0
            
            if request.store_projects:
                yield f"data: {json.dumps({'status': 'storing', 'message': 'Storing projects in database...', 'progress': 90})}\n\n"
                
                result = await mongodb_client.bulk_insert_projects(projects)
                stored = result["inserted"]
                duplicates = result["duplicates"]
            
            # Complete
            yield f"data: {json.dumps({'status': 'complete', 'message': 'Bulk scrape completed', 'progress': 100, 'total_scraped': len(projects), 'total_failed': len(failures), 'total_stored': stored, 'duplicates': duplicates})}\n\n"
            
        except Exception as e:
            logger.error(f"Error in bulk scrape stream: {e}", exc_info=True)
            yield f"data: {json.dumps({'status': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )


@router.post("/scrape", response_model=BulkScrapeResponse)
async def bulk_scrape(request: BulkScrapeRequest):
    """
    Bulk scrape projects (non-streaming)
    
    Workflow:
    1. Scrape N projects from Devfolio
    2. Generate embeddings (if requested)
    3. Store in database (if requested)
    """
    try:
        logger.info(f"Starting bulk scrape for {request.limit} projects")
        
        # Scrape projects
        projects, failures = await scraper_service.scrape_bulk_projects(limit=request.limit)
        
        if not projects:
            raise HTTPException(
                status_code=400,
                detail="Failed to scrape any projects"
            )
        
        # Generate embeddings
        if request.generate_embeddings:
            logger.info("Generating embeddings...")
            for project in projects:
                try:
                    embeddings = await embedding_service.generate_project_embedding(project)
                    project["embeddingsOfData"] = embeddings
                except Exception as e:
                    logger.error(f"Error generating embedding: {e}")
                    project["embeddingsOfData"] = []
        
        # Store projects
        stored = 0
        duplicates = 0
        
        if request.store_projects:
            logger.info("Storing projects...")
            result = await mongodb_client.bulk_insert_projects(projects)
            stored = result["inserted"]
            duplicates = result["duplicates"]
        
        return BulkScrapeResponse(
            status="success",
            message=f"Bulk scrape completed successfully",
            total_scraped=len(projects),
            total_failed=len(failures),
            total_stored=stored,
            duplicates=duplicates
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in bulk scrape: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error in bulk scrape: {str(e)}"
        )


@router.post("/generate-embeddings-stream")
async def generate_embeddings_stream(request: GenerateEmbeddingsRequest):
    """
    Generate embeddings for projects that don't have them (with streaming updates)
    """
    async def event_generator():
        try:
            # Get projects without embeddings
            yield f"data: {json.dumps({'status': 'fetching', 'message': 'Fetching projects without embeddings...', 'progress': 0})}\n\n"
            
            projects = await mongodb_client.get_projects_without_embeddings(limit=request.limit)
            
            if not projects:
                yield f"data: {json.dumps({'status': 'complete', 'message': 'All projects already have embeddings', 'progress': 100})}\n\n"
                return
            
            total = len(projects)
            yield f"data: {json.dumps({'status': 'processing', 'message': f'Found {total} projects without embeddings', 'progress': 10, 'total': total})}\n\n"
            
            updated = 0
            failed = 0
            
            for idx, project in enumerate(projects):
                try:
                    # Generate embedding
                    embeddings = await embedding_service.generate_project_embedding(project)
                    
                    # Update in database
                    success = await mongodb_client.update_project_embeddings(
                        project["urlOfProject"],
                        embeddings
                    )
                    
                    if success:
                        updated += 1
                    else:
                        failed += 1
                    
                    progress = 10 + (80 * (idx + 1) / total)
                    
                    if (idx + 1) % 5 == 0:  # Update every 5 projects
                        yield f"data: {json.dumps({'status': 'processing', 'message': f'Processed {idx + 1}/{total} projects', 'progress': progress, 'updated': updated, 'failed': failed})}\n\n"
                
                except Exception as e:
                    logger.error(f"Error processing project: {e}")
                    failed += 1
            
            # Complete
            yield f"data: {json.dumps({'status': 'complete', 'message': 'Embedding generation complete', 'progress': 100, 'total': total, 'updated': updated, 'failed': failed})}\n\n"
            
        except Exception as e:
            logger.error(f"Error in embedding generation: {e}", exc_info=True)
            yield f"data: {json.dumps({'status': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )


@router.post("/generate-embeddings", response_model=GenerateEmbeddingsResponse)
async def generate_embeddings(request: GenerateEmbeddingsRequest):
    """
    Generate embeddings for projects that don't have them (non-streaming)
    """
    try:
        logger.info("Starting embedding generation for projects")
        
        # Get projects without embeddings
        projects = await mongodb_client.get_projects_without_embeddings(limit=request.limit)
        
        if not projects:
            return GenerateEmbeddingsResponse(
                status="success",
                message="All projects already have embeddings",
                processed=0,
                updated=0,
                failed=0
            )
        
        updated = 0
        failed = 0
        
        for project in projects:
            try:
                # Generate embedding
                embeddings = await embedding_service.generate_project_embedding(project)
                
                # Update in database
                success = await mongodb_client.update_project_embeddings(
                    project["urlOfProject"],
                    embeddings
                )
                
                if success:
                    updated += 1
                else:
                    failed += 1
            
            except Exception as e:
                logger.error(f"Error processing project: {e}")
                failed += 1
        
        return GenerateEmbeddingsResponse(
            status="success",
            message=f"Processed {len(projects)} projects",
            processed=len(projects),
            updated=updated,
            failed=failed
        )
    
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error generating embeddings: {str(e)}"
        )


@router.get("/status")
async def get_bulk_status():
    """Get statistics about bulk operations"""
    try:
        total = await mongodb_client.get_total_projects()
        with_embeddings = await mongodb_client.get_projects_with_embeddings_count()
        
        return {
            "status": "success",
            "total_projects": total,
            "projects_with_embeddings": with_embeddings,
            "projects_without_embeddings": total - with_embeddings,
            "completion_percentage": (with_embeddings / total * 100) if total > 0 else 0
        }
    
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting status: {str(e)}"
        )


@router.post("/ingest/start", response_model=MassIngestControlResponse)
async def start_mass_ingest(
    request: MassIngestStartRequest,
    x_admin_token: Optional[str] = Header(default=None),
):
    """Start a mass ingestion job."""
    _validate_admin_token(x_admin_token)

    try:
        result = await mass_ingestor_service.start(
            mode=request.mode,
            target_projects=request.target_projects,
        )
        if result.get("started"):
            return MassIngestControlResponse(
                status="success",
                message="Mass ingest job started",
                job_id=result.get("job_id"),
            )

        return MassIngestControlResponse(
            status="running",
            message=result.get("message", "Mass ingest job already running"),
            job_id=result.get("job_id"),
        )

    except Exception as e:
        logger.error(f"Error starting mass ingest: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error starting mass ingest: {str(e)}")


@router.post("/ingest/pause", response_model=MassIngestControlResponse)
async def pause_mass_ingest(
    job_id: Optional[str] = None,
    x_admin_token: Optional[str] = Header(default=None),
):
    """Pause a running mass ingestion job."""
    _validate_admin_token(x_admin_token)

    result = await mass_ingestor_service.pause(job_id=job_id)
    return MassIngestControlResponse(
        status="success" if result.get("paused") else "not_found",
        message=result.get("message", "Mass ingest job paused"),
        job_id=result.get("job_id"),
    )


@router.post("/ingest/resume", response_model=MassIngestControlResponse)
async def resume_mass_ingest(
    job_id: Optional[str] = None,
    x_admin_token: Optional[str] = Header(default=None),
):
    """Resume a paused mass ingestion job."""
    _validate_admin_token(x_admin_token)

    result = await mass_ingestor_service.resume(job_id=job_id)
    return MassIngestControlResponse(
        status="success" if result.get("resumed") else "not_found",
        message=result.get("message", "Mass ingest job resumed"),
        job_id=result.get("job_id"),
    )


@router.post("/ingest/stop", response_model=MassIngestControlResponse)
async def stop_mass_ingest(
    job_id: Optional[str] = None,
    x_admin_token: Optional[str] = Header(default=None),
):
    """Stop a running mass ingestion job."""
    _validate_admin_token(x_admin_token)

    result = await mass_ingestor_service.stop(job_id=job_id)
    return MassIngestControlResponse(
        status="success" if result.get("stopped") else "not_found",
        message=result.get("message", "Mass ingest stop requested"),
        job_id=result.get("job_id"),
    )


@router.get("/ingest/status")
async def ingest_status(
    job_id: Optional[str] = None,
    x_admin_token: Optional[str] = Header(default=None),
):
    """Get status for one ingest job (current job by default)."""
    _validate_admin_token(x_admin_token)

    status = await mass_ingestor_service.get_status(job_id=job_id)
    if not status:
        raise HTTPException(status_code=404, detail="No ingest job found")
    return {"status": "success", "job": status}


@router.get("/ingest/jobs")
async def list_ingest_jobs(
    limit: int = 10,
    x_admin_token: Optional[str] = Header(default=None),
):
    """List recent ingestion jobs."""
    _validate_admin_token(x_admin_token)

    jobs = await mass_ingestor_service.list_jobs(limit=max(1, min(limit, 100)))
    return {
        "status": "success",
        "count": len(jobs),
        "jobs": jobs,
    }
