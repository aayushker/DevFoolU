from __future__ import annotations

import asyncio
import random
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple
from urllib.parse import urlparse

from playwright.async_api import Browser, Playwright, TimeoutError as PlaywrightTimeoutError
from tqdm import tqdm

from .config import ScraperConfig


SECTION_KEYWORDS: Dict[str, Tuple[str, ...]] = {
    "problemSolved": (
        "problem",
        "problem statement",
        "problem we solve",
        "pain point",
        "solution",
        "what it does",
        "overview",
    ),
    "challengesFaced": (
        "challenge",
        "challenges",
        "obstacle",
        "hurdle",
        "roadblock",
        "difficulty",
        "limitations",
    ),
    "technologiesUsed": (
        "technologies",
        "tech stack",
        "built with",
        "stack",
        "tools",
        "framework",
        "libraries",
    ),
}

STOP_SECTION_KEYWORDS: Tuple[str, ...] = (
    "problem",
    "challenge",
    "technology",
    "tech stack",
    "team",
    "future",
    "roadmap",
    "demo",
    "github",
    "conclusion",
)


def _clean_text(text: str) -> str:
    if not text:
        return ""
    compact = re.sub(r"[ \t]+", " ", text)
    compact = re.sub(r"\n{3,}", "\n\n", compact)
    return compact.strip()


def _extract_section_from_main_text(main_text: str, keywords: Iterable[str]) -> str:
    """Extract section-like content from full page text when structured selectors fail."""
    if not main_text:
        return ""

    lines = [
        _clean_text(line)
        for line in re.split(r"[\r\n]+", main_text)
        if _clean_text(line)
    ]
    if not lines:
        return ""

    lower_keywords = [k.lower() for k in keywords]
    lower_stop = [k.lower() for k in STOP_SECTION_KEYWORDS]

    for idx, line in enumerate(lines):
        lower_line = line.lower()
        if not any(keyword in lower_line for keyword in lower_keywords):
            continue

        # Common pattern: "Problem Statement: ..."
        if ":" in line:
            left, right = line.split(":", 1)
            if right.strip() and any(keyword in left.lower() for keyword in lower_keywords):
                return _clean_text(right)[:1200]

        collected: List[str] = []
        for candidate in lines[idx + 1 : idx + 9]:
            lower_candidate = candidate.lower()
            if collected and any(stop_word in lower_candidate for stop_word in lower_stop):
                break
            if len(candidate) < 10:
                continue
            collected.append(candidate)
            if len(" ".join(collected)) >= 1200:
                break

        if collected:
            return _clean_text(" ".join(collected))[:1200]

        if len(line) > 25:
            return _clean_text(line)[:1200]

    return ""


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


async def _extract_main_text(page) -> str:
    script = r"""
    () => {
        const root = document.querySelector("main") || document.body;
        if (!root) {
            return "";
        }
        return (root.innerText || "").trim();
    }
    """
    text = await page.evaluate(script)
    return _clean_text(text)


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


async def _extract_tagline(page) -> str:
    script = r"""
    () => {
        const root = document.querySelector("main") || document.body;
        const heading = root.querySelector("h1");
        if (!heading) {
            return "";
        }

        const clean = (txt) => (txt || "").replace(/\s+/g, " ").trim();

        let next = heading.nextElementSibling;
        while (next) {
            const text = clean(next.innerText || "");
            if (text && text.length >= 12 && text.length <= 180) {
                return text;
            }
            if (next.tagName && /^H[1-6]$/.test(next.tagName)) {
                break;
            }
            next = next.nextElementSibling;
        }
        return "";
    }
    """
    tagline = await page.evaluate(script)
    return tagline.strip()


async def _extract_tags(page) -> List[str]:
    script = r"""
    () => {
        const selectors = [
            "[class*='Tag']",
            "[class*='tag']",
            "[class*='Chip']",
            "[class*='chip']",
            "a[href*='/tag/']",
            "[data-testid*='chip']"
        ];
        const values = new Set();

        const clean = (txt) => (txt || "").replace(/\s+/g, " ").trim();
        for (const selector of selectors) {
            for (const node of document.querySelectorAll(selector)) {
                const text = clean(node.innerText || "");
                if (text && text.length <= 60) {
                    values.add(text);
                }
            }
        }
        return Array.from(values).slice(0, 30);
    }
    """
    tags = await page.evaluate(script)
    return [tag.strip() for tag in tags if isinstance(tag, str) and tag.strip()]


async def _extract_external_links(page) -> Dict[str, str]:
    script = r"""
    () => {
        const links = Array.from(document.querySelectorAll("a[href]"))
            .map((node) => {
                const href = (node.getAttribute("href") || "").trim();
                const text = (node.innerText || "").trim().toLowerCase();
                return { href, text };
            })
            .filter((item) => item.href && /^https?:\/\//i.test(item.href));

        const byPriority = (predicates) => {
            for (const check of predicates) {
                const match = links.find((item) => check(item));
                if (match) {
                    return match.href;
                }
            }
            return "";
        };

        const githubUrl = byPriority([
            (item) => item.href.includes("github.com"),
            (item) => item.text.includes("github")
        ]);

        const demoUrl = byPriority([
            (item) => item.text.includes("demo") || item.text.includes("prototype"),
            (item) => item.href.includes("youtube.com") || item.href.includes("youtu.be"),
            (item) => item.href.includes("loom.com")
        ]);

        const liveUrl = byPriority([
            (item) => item.text.includes("live") || item.text.includes("try") || item.text.includes("launch"),
            (item) => item.text.includes("website")
        ]);

        const docsUrl = byPriority([
            (item) => item.text.includes("doc") || item.text.includes("readme")
        ]);

        return {
            githubUrl,
            demoUrl,
            liveUrl,
            docsUrl
        };
    }
    """
    links = await page.evaluate(script)
    return {
        "githubUrl": (links.get("githubUrl") or "").strip(),
        "demoUrl": (links.get("demoUrl") or "").strip(),
        "liveUrl": (links.get("liveUrl") or "").strip(),
        "docsUrl": (links.get("docsUrl") or "").strip(),
    }


async def _navigate_to_project_page(page, url: str, config: ScraperConfig) -> None:
    """Navigate with fallbacks to reduce false timeouts on pages with noisy network activity."""
    wait_until = getattr(config, "navigation_wait_until", "domcontentloaded")
    try:
        await page.goto(url, wait_until=wait_until, timeout=config.request_timeout_ms)
    except PlaywrightTimeoutError:
        fallback_wait = "load" if wait_until != "load" else "domcontentloaded"
        await page.goto(url, wait_until=fallback_wait, timeout=config.request_timeout_ms)

    ready_timeout = int(getattr(config, "page_ready_timeout_ms", 12_000))
    try:
        await page.wait_for_selector(
            "main h1, main, meta[property='og:description']",
            timeout=ready_timeout,
        )
    except PlaywrightTimeoutError:
        pass

    title = (await page.title() or "").lower()
    if "just a moment" in title or "attention required" in title:
        raise RuntimeError("blocked_by_bot_protection")

    await page.wait_for_timeout(int(random.uniform(*config.rate_delay_range) * 1000))


async def _scrape_project_page(page, url: str, config: ScraperConfig) -> Dict[str, Any]:
    await _navigate_to_project_page(page, url, config)

    name = await _extract_name(page)
    tagline = await _extract_tagline(page)
    description = await _extract_meta_description(page)
    main_text = await _extract_main_text(page)

    sections: Dict[str, str] = {}
    for field, keywords in SECTION_KEYWORDS.items():
        structured_text = await _extract_heading_section(page, keywords)
        if structured_text:
            sections[field] = _clean_text(structured_text)
        else:
            sections[field] = _extract_section_from_main_text(main_text, keywords)

    tags = await _extract_tags(page)

    # Best-effort fallback for technologies from tag chips.
    if not sections["technologiesUsed"] and tags:
        sections["technologiesUsed"] = ", ".join(tags)

    # Last-resort fallback: if explicit sections are missing, keep non-empty semantic context.
    if not sections["problemSolved"] and description:
        sections["problemSolved"] = description

    if not sections["challengesFaced"]:
        sections["challengesFaced"] = _extract_section_from_main_text(
            main_text,
            ("challenge", "obstacle", "difficulty", "limitation", "issue"),
        )

    external_links = await _extract_external_links(page)
    og_image = await page.locator('meta[property="og:image"]').first.get_attribute("content")

    extraction_quality = {
        "problemCaptured": bool(sections["problemSolved"]),
        "challengesCaptured": bool(sections["challengesFaced"]),
        "technologiesCaptured": bool(sections["technologiesUsed"]),
    }

    return {
        "urlOfProject": url,
        "nameOfProject": name,
        "tagLine": tagline,
        "descriptionOfProject": description,
        "problemSolved": sections["problemSolved"],
        "challengesFaced": sections["challengesFaced"],
        "technologiesUsed": sections["technologiesUsed"],
        "tagsOfProject": tags,
        "imageOfProject": (og_image or "").strip(),
        "githubUrl": external_links["githubUrl"],
        "demoUrl": external_links["demoUrl"],
        "liveUrl": external_links["liveUrl"],
        "docsUrl": external_links["docsUrl"],
        "rawContentOfProject": main_text[:5000],
        "extractionQuality": extraction_quality,
    }


async def scrape_projects(playwright: Playwright, urls: List[str], config: ScraperConfig, logger):
    """Scrape multiple project pages concurrently."""
    if not urls:
        return [], []

    browser: Browser = await playwright.chromium.launch(headless=config.headless)
    context = await browser.new_context()

    blocked_types = {
        str(item).strip().lower()
        for item in getattr(config, "blocked_resource_types", ())
        if str(item).strip()
    }
    if blocked_types:
        async def block_heavy_assets(route):
            if route.request.resource_type in blocked_types:
                await route.abort()
            else:
                await route.continue_()

        await context.route("**/*", block_heavy_assets)

    semaphore = asyncio.Semaphore(config.concurrency)

    results: List[Dict[str, Any]] = []
    failures: List[str] = []
    failure_reasons: Dict[str, str] = {}
    lock = asyncio.Lock()
    progress = tqdm(total=len(urls), desc="Scraping projects", dynamic_ncols=True)

    async def worker(project_url: str):
        nonlocal results, failures, failure_reasons
        attempt = 0
        last_error = "scrape_failed"
        while attempt <= config.max_retries:
            attempt += 1
            is_rate_limited = False
            async with semaphore:
                page = await context.new_page()
                try:
                    data = await _scrape_project_page(page, project_url, config)
                except PlaywrightTimeoutError:
                    last_error = "timeout"
                    logger.warning(
                        "Timeout scraping %s (attempt %s/%s)", project_url, attempt, config.max_retries + 1
                    )
                    if config.screenshot_on_error:
                        errors_dir = Path("errors")
                        errors_dir.mkdir(parents=True, exist_ok=True)
                        safe_name = urlparse(project_url).path.replace("/", "_")
                        await page.screenshot(path=errors_dir / f"{safe_name}.png")
                except Exception as exc:  # noqa: BLE001
                    message = str(exc).lower()
                    is_rate_limited = "429" in message or "too many requests" in message
                    if is_rate_limited:
                        last_error = "rate_limited"
                    else:
                        last_error = f"{type(exc).__name__}: {str(exc)[:180]}"
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

            base_backoff = config.retry_backoff_seconds * attempt
            if is_rate_limited:
                base_backoff *= 2
            jitter = random.uniform(0.2, 1.0)
            await asyncio.sleep(base_backoff + jitter)

        async with lock:
            failures.append(project_url)
            failure_reasons[project_url] = last_error
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

    return results, failures, failure_reasons

