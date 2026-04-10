from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from pathlib import Path
from typing import Tuple


@dataclass(slots=True)
class ScraperConfig:
    """Runtime configuration for the Devfolio scraper."""

    base_url: str = "https://devfolio.co"
    listing_path: str = "/search?primary_filter=projects"
    target_projects: int = 1000
    scroll_pause_seconds: float = 1.5
    max_scroll_attempts: int = 250
    scroll_idle_tolerance: int = 12
    scroll_wait_timeout: float = 6.0
    scroll_step_multiplier: float = 0.9
    max_retries: int = 3
    retry_backoff_seconds: float = 3.0
    rate_delay_range: Tuple[float, float] = field(default_factory=lambda: (0.5, 1.8))
    headless: bool = True
    concurrency: int = 6
    request_timeout_ms: int = 45_000
    output_data_path: Path = field(default_factory=lambda: Path("projects_data.csv"))
    output_embeddings_path: Path = field(default_factory=lambda: Path("embeddings.csv"))
    log_path: Path = field(default_factory=lambda: Path("scraper.log"))
    failures_path: Path = field(default_factory=lambda: Path("failed_projects.txt"))
    progress_refresh_seconds: float = 0.5
    screenshot_on_error: bool = False

    @property
    def listing_url(self) -> str:
        return f"{self.base_url}{self.listing_path}"

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> "ScraperConfig":
        """Create a config instance from argparse arguments."""
        values = {
            "target_projects": args.limit,
            "headless": args.headless,
            "output_data_path": Path(args.data_path),
            "output_embeddings_path": Path(args.embeddings_path),
            "log_path": Path(args.log_path),
            "failures_path": Path(args.failures_path),
            "concurrency": max(1, args.concurrency),
        }
        if args.rate_min is not None and args.rate_max is not None:
            values["rate_delay_range"] = (max(0.0, args.rate_min), max(args.rate_min, args.rate_max))
        if args.scroll_pause is not None:
            values["scroll_pause_seconds"] = max(0.1, args.scroll_pause)
        if args.scroll_wait_timeout is not None:
            values["scroll_wait_timeout"] = max(1.0, args.scroll_wait_timeout)
        if args.scroll_step_multiplier is not None:
            values["scroll_step_multiplier"] = min(2.0, max(0.1, args.scroll_step_multiplier))
        return cls(**values)

