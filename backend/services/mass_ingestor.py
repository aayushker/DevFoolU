"""Mass ingestion orchestrator for resilient Devfolio backfill and incremental refresh."""

from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from playwright.async_api import async_playwright

from core.config import settings
from services.embedding import embedding_service
from services.mongodb import mongodb_client
from services.scraper import scraper_service

from scraper.parser import scrape_projects
from scraper.scroll import collect_project_urls

logger = logging.getLogger("DevFoolU.mass_ingestor")


class _SimpleLogger:
    """Adapter to satisfy scraper module logging interface."""

    def info(self, msg, *args):
        logger.info(msg % args if args else msg)

    def warning(self, msg, *args):
        logger.warning(msg % args if args else msg)

    def error(self, msg, *args):
        logger.error(msg % args if args else msg)


class MassIngestorService:
    """Coordinates long-running ingestion jobs with pause/resume and checkpointing."""

    def __init__(self):
        self._task: Optional[asyncio.Task] = None
        self._current_job_id: Optional[str] = None
        self._current_mode: str = "backfill"
        self._current_target: int = settings.MASS_INGEST_TARGET_PROJECTS

        self._pause_event = asyncio.Event()
        self._pause_event.set()
        self._stop_requested = False
        self._lock = asyncio.Lock()

        self._qos_concurrency = self._initial_concurrency()
        self._qos_delay_min = settings.MASS_INGEST_QOS_DELAY_MIN
        self._qos_delay_max = settings.MASS_INGEST_QOS_DELAY_MAX

    def _initial_concurrency(self) -> int:
        base = max(settings.MASS_INGEST_DEFAULT_CONCURRENCY, settings.SCRAPER_CONCURRENCY)
        return max(settings.MASS_INGEST_QOS_MIN_CONCURRENCY, min(base, settings.MASS_INGEST_QOS_MAX_CONCURRENCY))

    def _build_config(self, target_projects: int):
        config = scraper_service._create_config()
        config.target_projects = max(1, target_projects)
        config.concurrency = max(1, self._qos_concurrency)
        config.rate_delay_range = (
            max(0.0, self._qos_delay_min),
            max(self._qos_delay_min, self._qos_delay_max),
        )
        return config

    def _snapshot_config(self, mode: str, target_projects: int) -> Dict[str, Any]:
        return {
            "mode": mode,
            "targetProjects": target_projects,
            "batchSize": settings.MASS_INGEST_BATCH_SIZE,
            "maxUrlAttempts": settings.MASS_INGEST_MAX_URL_ATTEMPTS,
            "defaultConcurrency": self._qos_concurrency,
            "delayMin": self._qos_delay_min,
            "delayMax": self._qos_delay_max,
            "generateEmbeddings": settings.MASS_INGEST_GENERATE_EMBEDDINGS,
            "skipExistingProjectUrls": settings.MASS_INGEST_SKIP_EXISTING_PROJECT_URLS,
        }

    def _resolve_target_projects(self, mode: str, target_projects: Optional[int]) -> int:
        """Resolve target project count using mode-aware defaults."""
        if target_projects is not None:
            return max(1, int(target_projects))

        if mode == "incremental":
            return max(1, int(settings.MASS_INGEST_INCREMENTAL_TARGET_PROJECTS))

        return max(1, int(settings.MASS_INGEST_TARGET_PROJECTS))

    def _is_task_running(self) -> bool:
        return self._task is not None and not self._task.done()

    def _adjust_qos(self, batch_size: int, failed_count: int) -> Dict[str, Any]:
        if batch_size <= 0:
            return {
                "slowdown": False,
                "concurrency": self._qos_concurrency,
                "delayMin": self._qos_delay_min,
                "delayMax": self._qos_delay_max,
            }

        failure_ratio = failed_count / float(batch_size)
        slowdown = False

        if failure_ratio >= settings.MASS_INGEST_QOS_FAILURE_THRESHOLD:
            new_concurrency = max(
                settings.MASS_INGEST_QOS_MIN_CONCURRENCY,
                int(self._qos_concurrency * 0.75),
            )
            new_delay_min = min(settings.MASS_INGEST_QOS_DELAY_CAP, self._qos_delay_min * 1.25)
            new_delay_max = min(settings.MASS_INGEST_QOS_DELAY_CAP, self._qos_delay_max * 1.25)

            if (
                new_concurrency < self._qos_concurrency
                or new_delay_min > self._qos_delay_min
                or new_delay_max > self._qos_delay_max
            ):
                slowdown = True

            self._qos_concurrency = new_concurrency
            self._qos_delay_min = new_delay_min
            self._qos_delay_max = new_delay_max

        elif failure_ratio <= settings.MASS_INGEST_QOS_RECOVERY_THRESHOLD:
            self._qos_concurrency = min(
                settings.MASS_INGEST_QOS_MAX_CONCURRENCY,
                self._qos_concurrency + 1,
            )
            self._qos_delay_min = max(settings.MASS_INGEST_QOS_DELAY_MIN, self._qos_delay_min * 0.95)
            self._qos_delay_max = max(settings.MASS_INGEST_QOS_DELAY_MAX, self._qos_delay_max * 0.95)

        return {
            "slowdown": slowdown,
            "concurrency": self._qos_concurrency,
            "delayMin": self._qos_delay_min,
            "delayMax": self._qos_delay_max,
            "failureRatio": failure_ratio,
        }

    async def start(self, mode: str = "backfill", target_projects: Optional[int] = None) -> Dict[str, Any]:
        """Start a fresh ingestion job if none is running."""
        if not settings.MASS_INGEST_ENABLED:
            raise RuntimeError("Mass ingestion is disabled by configuration")

        async with self._lock:
            if self._is_task_running():
                return {
                    "started": False,
                    "job_id": self._current_job_id,
                    "message": "A mass ingest job is already running",
                }

            self._stop_requested = False
            self._pause_event.set()
            self._qos_concurrency = self._initial_concurrency()
            self._qos_delay_min = settings.MASS_INGEST_QOS_DELAY_MIN
            self._qos_delay_max = settings.MASS_INGEST_QOS_DELAY_MAX

            self._current_mode = mode if mode in {"backfill", "incremental"} else "backfill"
            self._current_target = self._resolve_target_projects(self._current_mode, target_projects)
            self._current_job_id = uuid.uuid4().hex

            await mongodb_client.create_ingest_job(
                job_id=self._current_job_id,
                mode=self._current_mode,
                target_projects=self._current_target,
                config_snapshot=self._snapshot_config(self._current_mode, self._current_target),
            )

            self._task = asyncio.create_task(
                self._run_job(
                    job_id=self._current_job_id,
                    mode=self._current_mode,
                    target_projects=self._current_target,
                    resume_existing=False,
                )
            )

            return {
                "started": True,
                "job_id": self._current_job_id,
                "mode": self._current_mode,
                "target_projects": self._current_target,
            }

    async def pause(self, job_id: Optional[str] = None) -> Dict[str, Any]:
        """Pause current ingestion job."""
        target_job_id = job_id or self._current_job_id
        if not target_job_id:
            return {"paused": False, "message": "No active job"}

        self._pause_event.clear()
        await mongodb_client.update_ingest_job(
            target_job_id,
            set_fields={
                "status": "paused",
                "heartbeatAt": datetime.utcnow(),
            },
        )
        return {"paused": True, "job_id": target_job_id}

    async def resume(self, job_id: Optional[str] = None) -> Dict[str, Any]:
        """Resume a paused job, recovering processing URLs if needed."""
        async with self._lock:
            target_job_id = job_id or self._current_job_id
            if not target_job_id:
                return {"resumed": False, "message": "No job selected"}

            job = await mongodb_client.get_ingest_job(target_job_id)
            if not job:
                return {"resumed": False, "message": "Job not found", "job_id": target_job_id}

            if job.get("status") in {"completed", "stopped"}:
                return {
                    "resumed": False,
                    "message": f"Job is already {job.get('status')}",
                    "job_id": target_job_id,
                }

            self._current_job_id = target_job_id
            self._current_mode = str(job.get("mode", "backfill"))
            self._current_target = int(job.get("targetProjects", settings.MASS_INGEST_TARGET_PROJECTS))
            self._stop_requested = False
            self._pause_event.set()

            await mongodb_client.update_ingest_job(
                target_job_id,
                set_fields={
                    "status": "running",
                    "heartbeatAt": datetime.utcnow(),
                    "lastError": None,
                },
            )

            if not self._is_task_running():
                await mongodb_client.reset_processing_urls(target_job_id)
                self._task = asyncio.create_task(
                    self._run_job(
                        job_id=target_job_id,
                        mode=self._current_mode,
                        target_projects=self._current_target,
                        resume_existing=True,
                    )
                )

            return {"resumed": True, "job_id": target_job_id}

    async def stop(self, job_id: Optional[str] = None) -> Dict[str, Any]:
        """Request graceful stop for current job."""
        target_job_id = job_id or self._current_job_id
        if not target_job_id:
            return {"stopped": False, "message": "No active job"}

        self._stop_requested = True
        self._pause_event.set()

        await mongodb_client.update_ingest_job(
            target_job_id,
            set_fields={
                "status": "stopped",
                "heartbeatAt": datetime.utcnow(),
            },
        )

        return {"stopped": True, "job_id": target_job_id}

    async def get_status(self, job_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Fetch enriched status for one job."""
        target_job_id = job_id
        if not target_job_id:
            if self._current_job_id:
                target_job_id = self._current_job_id
            else:
                jobs = await mongodb_client.list_ingest_jobs(limit=1)
                if not jobs:
                    return None
                target_job_id = jobs[0].get("_id")

        if not target_job_id:
            return None

        job = await mongodb_client.get_ingest_job(target_job_id)
        if not job:
            return None

        counts = await mongodb_client.get_ingest_url_state_counts(target_job_id)
        job["urlStateCounts"] = counts
        job["runtime"] = {
            "isRunningTask": self._is_task_running() and self._current_job_id == target_job_id,
            "isPaused": not self._pause_event.is_set() and self._current_job_id == target_job_id,
            "qos": {
                "concurrency": self._qos_concurrency,
                "delayMin": self._qos_delay_min,
                "delayMax": self._qos_delay_max,
            },
        }
        return job

    async def list_jobs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """List recent jobs."""
        return await mongodb_client.list_ingest_jobs(limit=limit)

    async def start_on_startup_if_enabled(self) -> Optional[Dict[str, Any]]:
        """Optionally start ingestion when backend boots."""
        if not settings.MASS_INGEST_ENABLED or not settings.MASS_INGEST_ON_STARTUP:
            return None

        return await self.start(
            mode=settings.MASS_INGEST_STARTUP_MODE,
            target_projects=None,
        )

    async def _wait_if_paused(self, job_id: str) -> None:
        while not self._pause_event.is_set() and not self._stop_requested:
            await mongodb_client.update_ingest_job(
                job_id,
                set_fields={"status": "paused", "phase": "paused", "heartbeatAt": datetime.utcnow()},
            )
            await asyncio.sleep(2)

    async def _discovery_heartbeat(self, job_id: str) -> None:
        """Emit heartbeat while URL discovery is running."""
        while True:
            await mongodb_client.update_ingest_job(
                job_id,
                set_fields={
                    "status": "running",
                    "phase": "discovering_urls",
                    "heartbeatAt": datetime.utcnow(),
                },
            )
            await asyncio.sleep(max(1, settings.MASS_INGEST_DISCOVERY_HEARTBEAT_SECONDS))

    async def _run_job(
        self,
        job_id: str,
        mode: str,
        target_projects: int,
        resume_existing: bool,
    ) -> None:
        simple_logger = _SimpleLogger()
        logger.info("Starting mass ingest job %s (%s)", job_id, mode)

        try:
            await mongodb_client.reset_processing_urls(job_id)
            await mongodb_client.update_ingest_job(
                job_id,
                set_fields={
                    "status": "running",
                    "phase": "initializing",
                    "heartbeatAt": datetime.utcnow(),
                    "lastError": None,
                },
            )

            async with async_playwright() as playwright:
                should_discover = True
                if resume_existing:
                    tracked_urls = await mongodb_client.count_ingest_urls(job_id)
                    should_discover = tracked_urls == 0

                if should_discover:
                    await mongodb_client.update_ingest_job(
                        job_id,
                        set_fields={
                            "phase": "discovering_urls",
                            "heartbeatAt": datetime.utcnow(),
                        },
                    )

                    exclude_urls: Optional[set[str]] = None
                    if settings.MASS_INGEST_SKIP_EXISTING_PROJECT_URLS:
                        exclude_urls = await mongodb_client.get_project_urls_set()
                        logger.info(
                            "Loaded %s existing project URLs for discovery exclusion.",
                            len(exclude_urls),
                        )

                    heartbeat_task = asyncio.create_task(self._discovery_heartbeat(job_id))
                    discover_config = self._build_config(target_projects=target_projects)

                    async def on_discovery_progress(snapshot: Dict[str, int]) -> None:
                        if self._stop_requested:
                            raise asyncio.CancelledError("Discovery interrupted by stop request")

                        await mongodb_client.update_ingest_job(
                            job_id,
                            set_fields={
                                "phase": "discovering_urls",
                                "heartbeatAt": datetime.utcnow(),
                                "stats.discovered": int(snapshot.get("collected", 0)),
                                "discoveryProgress": {
                                    "attempt": int(snapshot.get("attempt", 0)),
                                    "target": int(snapshot.get("target", 0)),
                                    "seen": int(snapshot.get("seen", 0)),
                                    "excluded": int(snapshot.get("excluded", 0)),
                                },
                            },
                        )

                    try:
                        try:
                            urls = await collect_project_urls(
                                playwright,
                                discover_config,
                                simple_logger,
                                progress_callback=on_discovery_progress,
                                exclude_urls=exclude_urls,
                            )
                        except asyncio.CancelledError:
                            urls = []
                    finally:
                        heartbeat_task.cancel()
                        try:
                            await heartbeat_task
                        except asyncio.CancelledError:
                            pass

                    seed_result = await mongodb_client.seed_ingest_job_urls(
                        job_id,
                        urls,
                        skip_existing_projects=settings.MASS_INGEST_SKIP_EXISTING_PROJECT_URLS,
                    )

                    await mongodb_client.update_ingest_job(
                        job_id,
                        set_fields={
                            "phase": "scraping",
                            "heartbeatAt": datetime.utcnow(),
                            "stats.discovered": seed_result["seeded"],
                        },
                        inc_fields={
                            "stats.skippedExisting": seed_result.get("skipped_existing", 0),
                        },
                    )

                    logger.info(
                        "Job %s discovery complete: %s URLs seeded (from %s discovered, %s skipped existing)",
                        job_id,
                        seed_result["seeded"],
                        seed_result["total"],
                        seed_result.get("skipped_existing", 0),
                    )

                while not self._stop_requested:
                    await self._wait_if_paused(job_id)
                    if self._stop_requested:
                        break

                    batch_urls = await mongodb_client.fetch_ingest_job_urls_for_processing(
                        job_id=job_id,
                        limit=settings.MASS_INGEST_BATCH_SIZE,
                        max_attempts=settings.MASS_INGEST_MAX_URL_ATTEMPTS,
                    )

                    if not batch_urls:
                        retriable_failed = await mongodb_client.get_retriable_failed_count(
                            job_id,
                            settings.MASS_INGEST_MAX_URL_ATTEMPTS,
                        )
                        if retriable_failed > 0:
                            next_retry_at = await mongodb_client.get_next_retry_at(
                                job_id,
                                settings.MASS_INGEST_MAX_URL_ATTEMPTS,
                            )
                            sleep_seconds = 5
                            if next_retry_at:
                                delta = (next_retry_at - datetime.utcnow()).total_seconds()
                                sleep_seconds = max(1, min(30, int(delta) if delta > 0 else 1))

                            await mongodb_client.update_ingest_job(
                                job_id,
                                set_fields={
                                    "phase": "waiting_for_retry",
                                    "heartbeatAt": datetime.utcnow(),
                                },
                            )
                            await asyncio.sleep(sleep_seconds)
                            continue
                        break

                    batch_config = self._build_config(target_projects=len(batch_urls))
                    projects, failures, failure_reasons = await scrape_projects(
                        playwright,
                        batch_urls,
                        batch_config,
                        simple_logger,
                    )

                    scanned_at = datetime.utcnow().isoformat()
                    for project in projects:
                        metadata = project.get("scrapeMetadata")
                        if not isinstance(metadata, dict):
                            metadata = {}
                        metadata.update(
                            {
                                "jobId": job_id,
                                "mode": mode,
                                "scannedAt": scanned_at,
                                "qosConcurrency": self._qos_concurrency,
                                "qosDelayMin": round(self._qos_delay_min, 3),
                                "qosDelayMax": round(self._qos_delay_max, 3),
                            }
                        )
                        project["scrapeMetadata"] = metadata

                    embeddings_generated = 0
                    if settings.MASS_INGEST_GENERATE_EMBEDDINGS and projects:
                        try:
                            vectors = await embedding_service.generate_embeddings_for_projects(projects)
                            for project, vector in zip(projects, vectors):
                                project["embeddingsOfData"] = vector
                            embeddings_generated = len(vectors)
                        except Exception as exc:  # noqa: BLE001
                            logger.warning("Batch embedding failed for job %s, falling back per-project: %s", job_id, exc)
                            for project in projects:
                                try:
                                    project["embeddingsOfData"] = await embedding_service.generate_project_embedding(project)
                                    embeddings_generated += 1
                                except Exception:
                                    project["embeddingsOfData"] = []

                    upsert_result = await mongodb_client.bulk_upsert_projects(projects)

                    problem_captured = sum(1 for p in projects if str(p.get("problemSolved", "")).strip())
                    challenges_captured = sum(1 for p in projects if str(p.get("challengesFaced", "")).strip())

                    successful_urls = [p.get("urlOfProject") for p in projects if p.get("urlOfProject")]
                    successful_urls = [u for u in successful_urls if isinstance(u, str)]

                    await mongodb_client.mark_ingest_urls_succeeded(job_id, successful_urls)
                    await mongodb_client.mark_ingest_urls_failed(
                        job_id,
                        failures,
                        backoff_base_seconds=settings.MASS_INGEST_RETRY_BACKOFF_BASE_SECONDS,
                        backoff_max_seconds=settings.MASS_INGEST_RETRY_BACKOFF_MAX_SECONDS,
                        error_by_url=failure_reasons,
                    )

                    qos_feedback = self._adjust_qos(len(batch_urls), len(failures))
                    inc_fields = {
                        "stats.processed": len(batch_urls),
                        "stats.succeeded": len(successful_urls),
                        "stats.failed": len(failures),
                        "stats.upserted": upsert_result.get("upserted", 0),
                        "stats.modified": upsert_result.get("modified", 0),
                        "stats.embeddingsGenerated": embeddings_generated,
                        "stats.problemCaptured": problem_captured,
                        "stats.challengesCaptured": challenges_captured,
                    }
                    if qos_feedback["slowdown"]:
                        inc_fields["stats.qosSlowdowns"] = 1

                    await mongodb_client.update_ingest_job(
                        job_id,
                        set_fields={
                            "heartbeatAt": datetime.utcnow(),
                            "status": "running",
                            "phase": "scraping",
                            "qos": {
                                "concurrency": qos_feedback["concurrency"],
                                "delayMin": qos_feedback["delayMin"],
                                "delayMax": qos_feedback["delayMax"],
                                "failureRatio": qos_feedback["failureRatio"],
                            },
                        },
                        inc_fields=inc_fields,
                    )

            final_status = "stopped" if self._stop_requested else "completed"
            await mongodb_client.update_ingest_job(
                job_id,
                set_fields={
                    "status": final_status,
                    "phase": "stopped" if self._stop_requested else "completed",
                    "finishedAt": datetime.utcnow(),
                    "heartbeatAt": datetime.utcnow(),
                },
            )
            logger.info("Mass ingest job %s finished with status %s", job_id, final_status)

        except Exception as exc:  # noqa: BLE001
            logger.error("Mass ingest job %s failed: %s", job_id, exc, exc_info=True)
            await mongodb_client.reset_processing_urls(job_id)
            await mongodb_client.update_ingest_job(
                job_id,
                set_fields={
                    "status": "failed",
                    "phase": "failed",
                    "lastError": str(exc),
                    "finishedAt": datetime.utcnow(),
                    "heartbeatAt": datetime.utcnow(),
                },
            )

        finally:
            self._pause_event.set()
            self._stop_requested = False
            self._task = None
            if self._current_job_id == job_id:
                self._current_job_id = None


mass_ingestor_service = MassIngestorService()
