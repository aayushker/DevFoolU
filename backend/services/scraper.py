"""Scraper service that wraps the existing scraper module"""

import sys
import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Optional
from playwright.async_api import async_playwright

# Add scraper module to path
from core.config import settings
sys.path.insert(0, str(settings.SCRAPER_DIR))

from scraper.config import ScraperConfig
from scraper.parser import scrape_projects, _scrape_project_page
from scraper.scroll import collect_project_urls

logger = logging.getLogger("DevFoolU.scraper")


class ScraperService:
    """Service for scraping Devfolio projects"""
    
    def __init__(self):
        self.config = self._create_config()
    
    def _create_config(self) -> ScraperConfig:
        """Create scraper configuration from settings"""
        blocked_resource_types = tuple(
            item.strip()
            for item in settings.SCRAPER_BLOCK_RESOURCE_TYPES.split(",")
            if item.strip()
        )

        return ScraperConfig(
            base_url=settings.SCRAPER_BASE_URL,
            headless=settings.SCRAPER_HEADLESS,
            request_timeout_ms=settings.SCRAPER_TIMEOUT_MS,
            page_ready_timeout_ms=settings.SCRAPER_PAGE_READY_TIMEOUT_MS,
            navigation_wait_until=settings.SCRAPER_NAVIGATION_WAIT_UNTIL,
            blocked_resource_types=blocked_resource_types,
            max_retries=settings.SCRAPER_MAX_RETRIES,
            retry_backoff_seconds=settings.SCRAPER_RETRY_BACKOFF,
            concurrency=settings.SCRAPER_CONCURRENCY,
            rate_delay_range=(settings.SCRAPER_RATE_DELAY_MIN, settings.SCRAPER_RATE_DELAY_MAX),
        )
    
    async def scrape_single_project(self, url: str, progress_callback=None) -> Optional[Dict]:
        """
        Scrape a single project URL
        
        Args:
            url: Project URL to scrape
            progress_callback: Optional callback for progress updates
        
        Returns:
            Project data dictionary or None if failed
        """
        try:
            if progress_callback:
                await progress_callback({
                    "status": "scraping",
                    "message": f"Starting to scrape: {url}",
                    "progress": 0
                })
            
            logger.info(f"Scraping single project: {url}")
            
            async with async_playwright() as playwright:
                browser = await playwright.chromium.launch(headless=self.config.headless)
                context = await browser.new_context()
                page = await context.new_page()
                
                try:
                    if progress_callback:
                        await progress_callback({
                            "status": "scraping",
                            "message": "Loading project page...",
                            "progress": 30
                        })
                    
                    # Use the scraper's page scraping function
                    project_data = await _scrape_project_page(page, url, self.config)
                    
                    if progress_callback:
                        await progress_callback({
                            "status": "scraping",
                            "message": "Project data extracted successfully",
                            "progress": 100
                        })
                    
                    logger.info(f"✅ Successfully scraped: {project_data.get('nameOfProject', 'Unknown')}")
                    return project_data
                    
                except Exception as e:
                    logger.error(f"Error scraping page: {e}")
                    if progress_callback:
                        await progress_callback({
                            "status": "error",
                            "message": f"Failed to scrape: {str(e)}",
                            "progress": 0
                        })
                    return None
                    
                finally:
                    await page.close()
                    await context.close()
                    await browser.close()
        
        except Exception as e:
            logger.error(f"Error in scrape_single_project: {e}")
            if progress_callback:
                await progress_callback({
                    "status": "error",
                    "message": f"Scraping failed: {str(e)}",
                    "progress": 0
                })
            return None
    
    async def scrape_bulk_projects(
        self,
        limit: int = 100,
        progress_callback=None
    ) -> tuple[List[Dict], List[str]]:
        """
        Scrape multiple projects from Devfolio
        
        Args:
            limit: Maximum number of projects to scrape
            progress_callback: Optional callback for progress updates
        
        Returns:
            Tuple of (successful_projects, failed_urls)
        """
        try:
            if progress_callback:
                await progress_callback({
                    "status": "collecting_urls",
                    "message": "Collecting project URLs from listing page...",
                    "progress": 0
                })
            
            logger.info(f"Starting bulk scrape for up to {limit} projects")
            
            # Create a simple logger for the scraper module
            class SimpleLogger:
                def info(self, msg, *args):
                    logger.info(msg % args if args else msg)
                def warning(self, msg, *args):
                    logger.warning(msg % args if args else msg)
                def error(self, msg, *args):
                    logger.error(msg % args if args else msg)
            
            simple_logger = SimpleLogger()
            
            async with async_playwright() as playwright:
                # Collect URLs
                if progress_callback:
                    await progress_callback({
                        "status": "collecting_urls",
                        "message": "Scrolling through project listings...",
                        "progress": 10
                    })
                
                # Update config with limit
                config = self._create_config()
                config.target_projects = limit
                
                urls = await collect_project_urls(playwright, config, simple_logger)
                
                if not urls:
                    logger.error("No URLs collected")
                    if progress_callback:
                        await progress_callback({
                            "status": "error",
                            "message": "Failed to collect project URLs",
                            "progress": 0
                        })
                    return [], []
                
                if progress_callback:
                    await progress_callback({
                        "status": "scraping_projects",
                        "message": f"Collected {len(urls)} URLs. Starting to scrape...",
                        "progress": 20
                    })
                
                logger.info(f"Collected {len(urls)} project URLs")
                
                # Scrape projects
                projects, failures, _failure_reasons = await scrape_projects(
                    playwright,
                    urls[:limit],
                    config,
                    simple_logger
                )
                
                if progress_callback:
                    await progress_callback({
                        "status": "completed",
                        "message": f"Scraped {len(projects)} projects successfully",
                        "progress": 100,
                        "total": len(projects),
                        "failed": len(failures)
                    })
                
                logger.info(f"✅ Bulk scrape complete: {len(projects)} successful, {len(failures)} failed")
                
                return projects, failures
        
        except Exception as e:
            logger.error(f"Error in bulk scrape: {e}")
            if progress_callback:
                await progress_callback({
                    "status": "error",
                    "message": f"Bulk scrape failed: {str(e)}",
                    "progress": 0
                })
            return [], []


# Global scraper service instance
scraper_service = ScraperService()
