# Devfolio Scraper

This project provides a production-grade scraper for Devfolio projects using Playwright and asynchronous Python utilities. The scraper scrolls through the Devfolio projects listing, captures detailed project information, and writes structured outputs alongside robust logging.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Install Playwright browsers:
   ```bash
   playwright install
   ```

## Usage

Run the scraper with default settings (1,000 projects, headless):
```bash
python -m scraper.cli
```

Optional flags:
- `--limit 500` scrape a different number of projects.
- `--data-path custom_data.csv` set a custom CSV output path.
- `--embeddings-path embeddings.csv` set embeddings output file.
- `--no-headless` launch the browser in headed mode.
- `--scroll-pause 0.6 --scroll-wait-timeout 4 --rate-min 0.2 --rate-max 0.5` tune performance.

Outputs:
- `projects_data.csv`
- `embeddings.csv` (placeholder entries while embeddings are disabled)
- `scraper.log`

