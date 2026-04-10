from __future__ import annotations

import asyncio
import random
from pathlib import Path
from typing import Dict, Iterable, List, Tuple
from urllib.parse import urlparse

from playwright.async_api import Browser, Playwright, TimeoutError as PlaywrightTimeoutError
from tqdm import tqdm

from .config import ScraperConfig


SECTION_KEYWORDS: Dict[str, Tuple[str, ...]] = {
    "problemSolved": ("problem", "problem statement", "what it does", "solution"),
    "challengesFaced": ("challenge", "challenges", "obstacle", "hurdle"),
    "technologiesUsed": ("technologies", "tech stack", "built with", "stack"),
}


async def _extract_heading_section(page, keywords: Iterable[str]) -> str:
    script = """
    (keywords) => {
        const isHeading = (element) => {
            const tag = element.tagName ? element.tagName.toLowerCase() : "";
            return ["h1","h2","h3","h4","h5","h6"].includes(tag);
        };
        const lowerKeywords = keywords.map(k => k.toLowerCase());
        const headings = Array.from(document.querySelectorAll("h1, h2, h3, h4, h5, h6"));
        for (const heading of headings) {
            const text = (heading.innerText || "").trim().toLowerCase();
            for (const keyword of lowerKeywords) {
                if (text.includes(keyword)) {
                    const chunks = [];
                    let sibling = heading.nextElementSibling;
                    while (sibling && !isHeading(sibling)) {
                        if (sibling.innerText) {
                            chunks.push(sibling.innerText.trim());
                        }
                        sibling = sibling.nextElementSibling;
                    }
                    return chunks.join("\\n").trim();
                }
            }
        }
        return "";
    }
    """
    text = await page.evaluate(script, list(keywords))
    return text.strip()


async def _extract_meta_description(page) -> str:
    meta = await page.locator('meta[property="og:description"]').first.get_attribute("content")
    if meta:
        return meta.strip()
    meta = await page.locator('meta[name="description"]').first.get_attribute("content")
    return meta.strip() if meta else ""


async def _extract_name(page) -> str:
    heading = page.locator("main h1").first
    if await heading.count():
        text = await heading.text_content()
        if text:
            return text.strip()
    title = await page.title()
    if title:
        return title.replace("| Devfolio", "").strip()
    return ""


async def _scrape_project_page(page, url: str, config: ScraperConfig) -> Dict[str, str]:
    await page.goto(url, wait_until="networkidle", timeout=config.request_timeout_ms)
    await page.wait_for_timeout(int(random.uniform(*config.rate_delay_range) * 1000))

    name = await _extract_name(page)
    description = await _extract_meta_description(page)

    sections = {}
    for field, keywords in SECTION_KEYWORDS.items():
        sections[field] = await _extract_heading_section(page, keywords)

    # Best-effort fallback for technologies: collect pills or badges.
    if not sections["technologiesUsed"]:
        pill_text = await page.evaluate(
            """
            () => {
                const selectors = [
                    "[class*='Tag']",
                    "[class*='tag']",
                    "[class*='Tech']",
                    "a[href*='tag']",
                    "span.chip",
                    "[data-testid*='chip']"
                ];
                const values = new Set();
                for (const selector of selectors) {
                    for (const el of document.querySelectorAll(selector)) {
                        const text = el.innerText ? el.innerText.trim() : "";
                        if (text && text.length <= 40) {
                            values.add(text);
                        }
                    }
                }
                return Array.from(values).join(", ");
            }
            """
        )
        sections["technologiesUsed"] = pill_text.strip()

    return {
        "urlOfProject": url,
        "nameOfProject": name,
        "descriptionOfProject": description,
        "problemSolved": sections["problemSolved"],
        "challengesFaced": sections["challengesFaced"],
        "technologiesUsed": sections["technologiesUsed"],
    }


async def scrape_projects(playwright: Playwright, urls: List[str], config: ScraperConfig, logger):
    """Scrape multiple project pages concurrently."""
    if not urls:
        return [], []

    browser: Browser = await playwright.chromium.launch(headless=config.headless)
    context = await browser.new_context()
    semaphore = asyncio.Semaphore(config.concurrency)

    results: List[Dict[str, str]] = []
    failures: List[str] = []
    lock = asyncio.Lock()
    progress = tqdm(total=len(urls), desc="Scraping projects", dynamic_ncols=True)

    async def worker(project_url: str):
        nonlocal results, failures
        attempt = 0
        while attempt <= config.max_retries:
            attempt += 1
            async with semaphore:
                page = await context.new_page()
                try:
                    data = await _scrape_project_page(page, project_url, config)
                except PlaywrightTimeoutError:
                    logger.warning(
                        "Timeout scraping %s (attempt %s/%s)", project_url, attempt, config.max_retries + 1
                    )
                    if config.screenshot_on_error:
                        errors_dir = Path("errors")
                        errors_dir.mkdir(parents=True, exist_ok=True)
                        safe_name = urlparse(project_url).path.replace("/", "_")
                        await page.screenshot(path=errors_dir / f"{safe_name}.png")
                except Exception as exc:  # noqa: BLE001
                    logger.warning(
                        "Error scraping %s (attempt %s/%s): %s",
                        project_url,
                        attempt,
                        config.max_retries + 1,
                        exc,
                    )
                else:
                    async with lock:
                        results.append(data)
                    await page.close()
                    return
                finally:
                    if not page.is_closed():
                        await page.close()

            await asyncio.sleep(config.retry_backoff_seconds * attempt)

        async with lock:
            failures.append(project_url)
        logger.error("Failed to scrape %s after %s attempts.", project_url, config.max_retries + 1)

    async def run_worker(url: str):
        try:
            await worker(url)
        finally:
            progress.update(1)

    await asyncio.gather(*(run_worker(url) for url in urls))
    progress.close()

    await context.close()
    await browser.close()

    return results, failures

