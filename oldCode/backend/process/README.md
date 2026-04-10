# Devfolio Project Scraper

This directory contains scripts for scraping project data from Devfolio in an efficient, respectful manner that avoids IP blocks and minimizes load on their servers.

## Features

- **Headless scraping**: All scraping is performed in the background
- **Rate limiting**: Automatic delays between requests to avoid overloading servers
- **Proxy rotation**: Optional support for using multiple proxies to distribute requests
- **Error handling**: Robust retry logic for handling temporary failures
- **Checkpoint saving**: Regular saving of progress to avoid data loss
- **Resume capability**: Can resume from previous runs if interrupted
- **Batch processing**: Processes URLs in manageable batches

## Requirements

Install all requirements from the main requirements.txt file:

```bash
pip install -r ../requirements.txt
```

## Scripts Overview

- `scrapper.py`: Original single-project scraper (now runs in headless mode)
- `batch_scraper.py`: Multi-threaded batch scraper with rate limiting and proxy support
- `url_scraper.py`: Scraper for collecting project URLs from Devfolio listings
- `scrape_manager.py`: Main script to orchestrate the entire scraping workflow

## Usage

### Basic Workflow

The recommended workflow consists of three steps:

1. **Collect project URLs** from Devfolio listings
2. **Collect basic metadata** (optional but recommended)
3. **Perform full scraping** of project details

### Command Line Examples

#### Step 1: Collect URLs
```bash
python scrape_manager.py --collect-urls --start-page 1 --end-page 10
```

This will create a `project_urls.csv` file with URLs from pages 1-10.

#### Step 2: Collect Metadata (Optional)
```bash
python scrape_manager.py --collect-metadata
```

This will create a `project_metadata.csv` file with basic info about each project.

#### Step 3: Full Scrape
```bash
python scrape_manager.py --full-scrape --batch-size 50
```

This will perform full scraping in batches of 50 projects.

### Complete Example
```bash
# Run the entire pipeline
python scrape_manager.py --collect-urls --collect-metadata --full-scrape --start-page 1 --end-page 100 --batch-size 100
```

### Using Proxies (Advanced)

To use proxy rotation:

1. Create a `proxies.txt` file with one proxy per line in the format `http://ip:port`
2. Add the `--use-proxies` flag:

```bash
python scrape_manager.py --full-scrape --use-proxies
```

## Configuration Options

The `scrape_manager.py` script accepts various command-line arguments:

| Argument | Description | Default |
|----------|-------------|---------|
| `--collect-urls` | Collect project URLs from Devfolio | - |
| `--collect-metadata` | Collect basic metadata | - |
| `--full-scrape` | Perform full scraping of project details | - |
| `--start-page` | Starting page number | 1 |
| `--end-page` | Ending page number | 10 |
| `--batch-size` | Batch size for full scraping | 100 |
| `--url-file` | File with project URLs | project_urls.csv |
| `--metadata-file` | File with project metadata | project_metadata.csv |
| `--output-file` | Output file for full scraping | devfolio_projects.csv |
| `--use-proxies` | Use proxy rotation | - |
| `--proxy-list` | File with proxy list | proxies.txt |

## Best Practices

1. **Start small**: Begin with a small number of pages/projects to test
2. **Use metadata collection**: This helps prioritize which projects to scrape first
3. **Be respectful**: Use reasonable delays and batch sizes
4. **Monitor logs**: Check the logs directory for issues
5. **Use proxies**: For large-scale scraping, distribute requests across multiple IPs 