import time
import random
import requests
import logging
import pandas as pd
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from urllib.parse import urlparse, urljoin

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="url_scraper.log"
)

# Constants
BASE_URL = "https://devfolio.co/projects"
DELAY_MIN = 3  # Minimum seconds between requests
DELAY_MAX = 7  # Maximum seconds between requests
MAX_RETRIES = 5

def get_project_urls(start_page=1, end_page=10, output_file="project_urls.csv"):
    """
    Scrape project URLs from Devfolio project listings pages
    
    Args:
        start_page (int): Starting page number
        end_page (int): Ending page number
        output_file (str): File to save the URLs
        
    Returns:
        list: List of scraped project URLs
    """
    all_urls = []
    ua = UserAgent()
    
    # Try to load existing URLs if available
    try:
        existing_df = pd.read_csv(output_file)
        all_urls = existing_df["URL"].tolist()
        logging.info(f"Loaded {len(all_urls)} existing URLs from {output_file}")
    except (FileNotFoundError, pd.errors.EmptyDataError):
        logging.info("No existing URL file found. Starting fresh.")
    
    # Set for checking duplicates
    existing_urls = set(all_urls)
    
    for page in range(start_page, end_page + 1):
        logging.info(f"Processing page {page}/{end_page}")
        
        # Add random delay between requests
        delay = random.uniform(DELAY_MIN, DELAY_MAX)
        logging.info(f"Waiting {delay:.2f}s before next request")
        time.sleep(delay)
        
        # Get page with retries
        for attempt in range(MAX_RETRIES):
            try:
                headers = {'User-Agent': ua.random}
                url = f"{BASE_URL}?page={page}"
                logging.info(f"Requesting {url}")
                
                response = requests.get(url, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    break
                else:
                    logging.warning(f"Attempt {attempt+1}/{MAX_RETRIES}: HTTP {response.status_code}")
                    time.sleep(delay * (attempt + 1))  # Exponential backoff
            except Exception as e:
                logging.error(f"Request error on attempt {attempt+1}/{MAX_RETRIES}: {str(e)}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(delay * (attempt + 1))
                else:
                    logging.error(f"Skipping page {page} after max retries")
                    continue
        
        if response.status_code != 200:
            logging.error(f"Failed to get page {page} after {MAX_RETRIES} attempts")
            continue
            
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find project links
        # Note: This selector needs to be adjusted based on the actual page structure
        # You might need to inspect the Devfolio website to find the correct selector
        project_cards = soup.select('.ProjectCard-sc-7dada411-0')
        
        if not project_cards:
            logging.warning(f"No project cards found on page {page}. Selector might need updating.")
            # Try alternative selectors
            project_cards = soup.select('a[href^="/projects/"]')
            
        page_urls = []
        for card in project_cards:
            # Find the link - adjust as needed based on actual HTML structure
            link = card.find('a') or card
            if link and link.get('href'):
                href = link.get('href')
                
                # Handle relative URLs
                if href.startswith('/'):
                    full_url = urljoin("https://devfolio.co", href)
                else:
                    full_url = href
                    
                # Normalize and validate URL
                parsed = urlparse(full_url)
                if parsed.netloc == 'devfolio.co' and '/projects/' in parsed.path:
                    # Skip duplicates
                    if full_url not in existing_urls:
                        page_urls.append(full_url)
                        existing_urls.add(full_url)
        
        logging.info(f"Found {len(page_urls)} new URLs on page {page}")
        all_urls.extend(page_urls)
        
        # Save progress after each page
        df = pd.DataFrame({"URL": all_urls})
        df.to_csv(output_file, index=False)
        logging.info(f"Saved {len(all_urls)} URLs to {output_file}")
        
    return all_urls

def collect_project_metadata(url_file="project_urls.csv", output_file="project_metadata.csv", limit=None):
    """
    Collect basic metadata about projects without full scraping
    
    Args:
        url_file (str): CSV file with project URLs
        output_file (str): File to save project metadata
        limit (int): Optional limit on number of URLs to process
    """
    try:
        url_df = pd.read_csv(url_file)
        urls = url_df["URL"].tolist()
        
        if limit:
            urls = urls[:limit]
            
        logging.info(f"Preparing to collect metadata for {len(urls)} projects")
        
        # Try to load existing metadata
        try:
            metadata_df = pd.read_csv(output_file)
            existing_urls = set(metadata_df["URL"].tolist())
            urls_to_process = [url for url in urls if url not in existing_urls]
            metadata = metadata_df.to_dict('records')
            logging.info(f"Loaded {len(metadata)} existing records. {len(urls_to_process)} new URLs to process.")
        except (FileNotFoundError, pd.errors.EmptyDataError):
            urls_to_process = urls
            metadata = []
            logging.info(f"No existing metadata found. Processing {len(urls_to_process)} URLs.")
        
        ua = UserAgent()
        
        for i, url in enumerate(urls_to_process):
            if i > 0 and i % 10 == 0:
                logging.info(f"Progress: {i}/{len(urls_to_process)} ({i/len(urls_to_process)*100:.1f}%)")
                
            # Random delay
            time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))
            
            try:
                headers = {'User-Agent': ua.random}
                response = requests.get(url, headers=headers, timeout=30)
                
                if response.status_code != 200:
                    logging.warning(f"HTTP {response.status_code} for {url}")
                    continue
                    
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract basic metadata (adjust selectors as needed)
                title = soup.find('h1')
                title_text = title.text.strip() if title else "Unknown"
                
                # Just get the length of description without full scraping
                description_element = soup.select_one("#__next > div:nth-child(2) > section:nth-child(1) > div:nth-child(1) > div")
                desc_length = len(description_element.text) if description_element else 0
                
                # Count tech stack items
                tech_stack_elements = soup.select("div.ProjectTechCard__ProjectTechChip-sc-c8650bcd-0")
                tech_count = len(tech_stack_elements)
                
                metadata.append({
                    "URL": url,
                    "Title": title_text,
                    "Description_Length": desc_length,
                    "Tech_Count": tech_count,
                    "Last_Updated": pd.Timestamp.now().strftime("%Y-%m-%d")
                })
                
                # Save every 50 records
                if len(metadata) % 50 == 0:
                    pd.DataFrame(metadata).to_csv(output_file, index=False)
                    logging.info(f"Saved {len(metadata)} metadata records")
                    
            except Exception as e:
                logging.error(f"Error processing {url}: {str(e)}")
        
        # Final save
        pd.DataFrame(metadata).to_csv(output_file, index=False)
        logging.info(f"Completed. Saved {len(metadata)} metadata records to {output_file}")
        
    except Exception as e:
        logging.error(f"Failed to process metadata: {str(e)}")

if __name__ == "__main__":
    # Scrape project URLs
    urls = get_project_urls(start_page=1, end_page=5, output_file="project_urls.csv")
    
    # Optional: Collect basic metadata
    collect_project_metadata(url_file="project_urls.csv", output_file="project_metadata.csv", limit=100) 