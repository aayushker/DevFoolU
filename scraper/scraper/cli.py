from __future__ import annotations

import argparse
import asyncio
import sys

from playwright.async_api import async_playwright

from .config import ScraperConfig
from .logger import setup_logging
from .parser import scrape_projects
from .scroll import collect_project_urls
from .storage import write_embeddings_placeholder, write_failures, write_projects_csv


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scrape Devfolio project listings.")
    parser.add_argument("--limit", type=int, default=1000, help="Number of projects to scrape.")
    parser.add_argument("--headless", action=argparse.BooleanOptionalAction, default=True, help="Run browser in headless mode.")
    parser.add_argument("--data-path", default="projects_data.csv", help="CSV path for project data.")
    parser.add_argument("--embeddings-path", default="embeddings.csv", help="CSV path for embeddings placeholder.")
    parser.add_argument("--log-path", default="scraper.log", help="Log file path.")
    parser.add_argument("--concurrency", type=int, default=6, help="Number of concurrent project page fetches.")
    parser.add_argument("--rate-min", type=float, help="Minimum delay (seconds) between actions.")
    parser.add_argument("--rate-max", type=float, help="Maximum delay (seconds) between actions.")
    parser.add_argument("--failures-path", default="failed_projects.txt", help="Path to record failed URLs.")
    parser.add_argument("--scroll-pause", type=float, help="Base pause between scroll attempts (seconds).")
    parser.add_argument("--scroll-wait-timeout", type=float, help="Timeout to wait for new cards after each scroll.")
    parser.add_argument("--scroll-step-multiplier", type=float, help="Window height multiplier for each scroll step.")
    return parser


async def run(config: ScraperConfig):
    logger = setup_logging(config.log_path)
    logger.info("Scraper started with configuration: %s", config)

    async with async_playwright() as playwright:
        urls = await collect_project_urls(playwright, config, logger)
        if not urls:
            logger.error("No project URLs collected. Exiting.")
            return 1

        records, failures = await scrape_projects(playwright, urls[: config.target_projects], config, logger)

    write_projects_csv(records, config.output_data_path)
    write_embeddings_placeholder(records, config.output_embeddings_path)
    write_failures(failures, config.failures_path)

    logger.info("Successfully wrote %s project records to %s.", len(records), config.output_data_path)
    if failures:
        logger.warning("Failed to scrape %s projects. See %s for details.", len(failures), config.failures_path)
    else:
        logger.info("All project pages scraped successfully.")

    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    config = ScraperConfig.from_args(args)

    try:
        return asyncio.run(run(config))
    except KeyboardInterrupt:
        print("Interrupted by user.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())

