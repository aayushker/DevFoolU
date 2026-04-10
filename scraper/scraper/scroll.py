from __future__ import annotations

import random
from typing import Iterable, List, Set
from urllib.parse import urljoin

from playwright.async_api import Playwright, TimeoutError as PlaywrightTimeoutError

from .config import ScraperConfig


PROJECT_LINK_SELECTOR = 'a[href*="/projects/"]'


async def _gather_project_links(page) -> List[str]:
    links: List[str] = []
    anchor_locator = page.locator(PROJECT_LINK_SELECTOR)
    count = await anchor_locator.count()
    for idx in range(count):
        href = await anchor_locator.nth(idx).get_attribute("href")
        if href:
            cleaned = href.split("?")[0]
            if cleaned not in links:
                links.append(cleaned)
    return links


async def collect_project_urls(
    playwright: Playwright, config: ScraperConfig, logger
) -> List[str]:
    """Scroll the Devfolio listing page until the desired number of project URLs are collected."""
    logger.info("Starting listing scrape for up to %s projects.", config.target_projects)
    browser = await playwright.chromium.launch(headless=config.headless)
    context = await browser.new_context()
    page = await context.new_page()

    try:
        await page.goto(config.listing_url, wait_until="networkidle", timeout=config.request_timeout_ms)
    except PlaywrightTimeoutError:
        logger.warning("Initial navigation timed out, retrying with load event.")
        await page.goto(config.listing_url, wait_until="load")

    try:
        await page.wait_for_selector(PROJECT_LINK_SELECTOR, timeout=15000)
    except PlaywrightTimeoutError:
        sample_links = await page.eval_on_selector_all(
            "a",
            "elements => elements.slice(0, 20).map(el => el.getAttribute('href') || '')",
        )
        logger.warning(
            "Project cards did not appear within 15s; proceeding with scroll attempts. Found sample anchors: %s",
            [link for link in sample_links if link],
        )

    collected_set: Set[str] = set()
    ordered_links: List[str] = []
    idle_rounds = 0

    for attempt in range(config.max_scroll_attempts):
        before = len(collected_set)
        new_links = await _gather_project_links(page)
        for link in new_links:
            if link not in collected_set:
                collected_set.add(link)
                ordered_links.append(link)

        after = len(collected_set)
        if after > before:
            idle_rounds = 0
        if after >= config.target_projects:
            logger.info("Collected required number of project URLs (%s).", config.target_projects)
            break

        await page.evaluate(
            "(multiplier) => window.scrollBy(0, window.innerHeight * multiplier);",
            config.scroll_step_multiplier,
        )

        should_count_idle = after == before

        try:
            await page.wait_for_function(
                "(args) => document.querySelectorAll(args.selector).length > args.previous",
                arg={"selector": PROJECT_LINK_SELECTOR, "previous": after},
                timeout=int(config.scroll_wait_timeout * 1000),
            )
            idle_rounds = 0
        except PlaywrightTimeoutError:
            if should_count_idle:
                idle_rounds += 1

        if idle_rounds >= config.scroll_idle_tolerance:
            logger.warning(
                "No new projects detected after %s idle rounds. Stopping scroll.",
                config.scroll_idle_tolerance,
            )
            break

        delay = random.uniform(*config.rate_delay_range)
        await page.wait_for_timeout(int((config.scroll_pause_seconds + delay) * 1000))

    await context.close()
    await browser.close()

    absolute_urls = [urljoin(config.base_url, href) for href in ordered_links]

    logger.info("Listing scrape complete. Found %s project URLs.", len(absolute_urls))
    return absolute_urls[: config.target_projects]

