import time
import random
import requests
import pandas as pd
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
from tqdm import tqdm
from .db_manager import get_db_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="scraper.log"
)

# Constants
MAX_WORKERS = 3  # Limit parallel connections
REQUEST_DELAY_MIN = 2  # Minimum seconds between requests
REQUEST_DELAY_MAX = 5  # Maximum seconds between requests
RETRY_DELAY = 30  # Seconds to wait if rate limited
MAX_RETRIES = 3  # Maximum number of retry attempts
CHECKPOINT_INTERVAL = 50  # Save progress every N projects
CSV_BACKUP_ENABLED = True  # Enable CSV backup in addition to MongoDB

class DevfolioScraper:
    def __init__(self, proxies=None, db_manager=None):
        """
        Initialize the scraper with optional proxy list
        
        Args:
            proxies (list): Optional list of proxy URLs in format "http://ip:port"
            db_manager: Optional database manager for storing results
        """
        self.proxies = proxies
        self.user_agent = UserAgent()
        self.results = []
        self.counter = 0
        self.db_manager = db_manager
        
    def get_chrome_options(self, use_proxy=False, proxy=None):
        """Configure Chrome options for scraping"""
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument(f"user-agent={self.user_agent.random}")
        
        if use_proxy and proxy:
            options.add_argument(f'--proxy-server={proxy}')
            
        return options
    
    def scrape_project(self, url, retry_count=0):
        """
        Scrape a single project with retry logic
        
        Args:
            url (str): The project URL to scrape
            retry_count (int): Current retry attempt
            
        Returns:
            dict: Project data or None if failed
        """
        if retry_count > MAX_RETRIES:
            logging.error(f"Max retries exceeded for {url}")
            return None
            
        # Add random delay to avoid detection
        time.sleep(random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX))
        
        # Check if project already exists in database
        if self.db_manager:
            existing_project = self.db_manager.get_project_by_url(url)
            if existing_project:
                logging.info(f"Project {url} already exists in database, skipping")
                # Return the existing project data in the format expected by the rest of the code
                return {
                    "Project URL": existing_project.get("project_url"),
                    "Project Name": existing_project.get("project_name"),
                    "Project Description": existing_project.get("project_description"),
                    "Tech Stack": existing_project.get("tech_stack")
                }
        
        # Select a proxy if available
        proxy = None
        if self.proxies:
            proxy = random.choice(self.proxies)
        
        # Initialize Chrome
        options = self.get_chrome_options(use_proxy=bool(proxy), proxy=proxy)
        driver = None
        
        try:
            driver = webdriver.Chrome(options=options)
            driver.get(url)
            
            project_name = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, "//h1"))
            ).text

            try:
                project_description_element = driver.find_element(By.XPATH, "//*[@id='__next']/div[2]/section[1]/div[1]/div")
                all_text = [element.text for element in project_description_element.find_elements(By.XPATH, ".//*")]
                project_description = " ".join(all_text)
            except:
                project_description = "No description available"

            tech_stack_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'sc-edUIhV sc-jmnVvD ProjectTechCard__ProjectTechChip-sc-c8650bcd-0 coEGBY dxbIEt BTjHj')]")
            tech_stack = ", ".join([element.text for element in tech_stack_elements])
            
            data = {
                "Project URL": url,
                "Project Name": project_name,
                "Project Description": project_description,
                "Tech Stack": tech_stack
            }
            
            # Save to database immediately if available
            if self.db_manager:
                self.db_manager.save_project(data)
            
            # Log success and increment counter
            logging.info(f"Successfully scraped: {url}")
            self.counter += 1
            
            # Save checkpoint periodically
            if self.counter % CHECKPOINT_INTERVAL == 0:
                self.save_checkpoint()
                
            return data
            
        except Exception as e:
            logging.warning(f"Error scraping {url}: {str(e)}")
            
            # Check for rate limiting or blocking indicators
            if driver and ("rate" in driver.page_source.lower() or 
                          "block" in driver.page_source.lower() or
                          "captcha" in driver.page_source.lower()):
                logging.warning(f"Possible rate limit/block detected. Waiting {RETRY_DELAY}s")
                time.sleep(RETRY_DELAY)
            
            # Retry with exponential backoff
            return self.scrape_project(url, retry_count + 1)
            
        finally:
            if driver:
                driver.quit()
    
    def batch_scrape(self, urls, output_file="devfolio_projects.csv"):
        """
        Scrape multiple projects in parallel with rate limiting
        
        Args:
            urls (list): List of project URLs to scrape
            output_file (str): Path to save results
        """
        logging.info(f"Starting batch scrape of {len(urls)} projects")
        
        try:
            # Get existing URLs from database if available
            if self.db_manager:
                existing_urls = self.db_manager.get_existing_urls()
                urls_to_scrape = [url for url in urls if url not in existing_urls]
                logging.info(f"Database has {len(existing_urls)} projects. {len(urls_to_scrape)} new URLs to scrape.")
            else:
                # Fall back to CSV if no database
                try:
                    existing_df = pd.read_csv(output_file)
                    existing_urls = set(existing_df["Project URL"].tolist())
                    urls_to_scrape = [url for url in urls if url not in existing_urls]
                    self.results = existing_df.to_dict('records')
                    logging.info(f"Loaded {len(self.results)} existing records. {len(urls_to_scrape)} new URLs to scrape.")
                except (FileNotFoundError, pd.errors.EmptyDataError):
                    urls_to_scrape = urls
                    logging.info(f"No existing data found. Starting fresh with {len(urls_to_scrape)} URLs.")
            
            # Use ThreadPoolExecutor for controlled parallelism
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                for data in tqdm(executor.map(self.scrape_project, urls_to_scrape), total=len(urls_to_scrape)):
                    if data:
                        self.results.append(data)
                        
                        # Save to database in small batches if available
                        if self.db_manager and len(self.results) % 10 == 0:
                            # Get the last 10 results
                            recent_results = self.results[-10:]
                            self.db_manager.save_batch(recent_results)
            
            # Save final results
            if self.db_manager:
                # Save any remaining results
                remaining_count = len(self.results) % 10
                if remaining_count > 0:
                    recent_results = self.results[-remaining_count:]
                    self.db_manager.save_batch(recent_results)
                
                # Export to CSV for backup if enabled
                if CSV_BACKUP_ENABLED and output_file:
                    self.db_manager.export_to_csv(output_file)
            else:
                # Fall back to CSV
                self.save_results(output_file)
                
            logging.info(f"Batch scraping completed. Scraped {self.counter} projects.")
            
            return self.results
            
        except KeyboardInterrupt:
            logging.info("Scraping interrupted. Saving current progress.")
            if CSV_BACKUP_ENABLED and output_file:
                self.save_results(output_file)
            return self.results
    
    def save_checkpoint(self):
        """Save intermediate results during scraping"""
        if CSV_BACKUP_ENABLED:
            df = pd.DataFrame(self.results)
            df.to_csv(f"checkpoint_{self.counter}.csv", index=False)
            logging.info(f"Saved checkpoint with {len(self.results)} records")
        
    def save_results(self, output_file):
        """Save final results to CSV"""
        if not output_file:
            return
            
        df = pd.DataFrame(self.results)
        df.to_csv(output_file, index=False)
        logging.info(f"Saved {len(self.results)} records to {output_file}")


def get_project_urls(start_page=1, end_page=10):
    """
    Scrape project URLs from Devfolio listings
    
    Args:
        start_page (int): Starting page number
        end_page (int): Ending page number
        
    Returns:
        list: List of project URLs
    """
    urls = []
    ua = UserAgent()
    
    for page in range(start_page, end_page + 1):
        time.sleep(random.uniform(2, 5))  # Be nice to their servers
        
        try:
            headers = {'User-Agent': ua.random}
            response = requests.get(
                f"https://devfolio.co/projects?page={page}", 
                headers=headers
            )
            
            if response.status_code == 200:
                # Extract project URLs from the page
                # This is simplified and would need to be adjusted based on actual page structure
                # In a real implementation, use BeautifulSoup or similar to parse HTML
                
                # Example with BeautifulSoup:
                # from bs4 import BeautifulSoup
                # soup = BeautifulSoup(response.text, 'html.parser')
                # project_links = soup.select('.project-card a')
                # page_urls = [f"https://devfolio.co{link['href']}" for link in project_links]
                
                # For demo purposes:
                page_urls = []  # Replace with actual implementation
                
                urls.extend(page_urls)
                logging.info(f"Collected {len(page_urls)} URLs from page {page}")
            else:
                logging.warning(f"Failed to fetch page {page}: HTTP {response.status_code}")
        
        except Exception as e:
            logging.error(f"Error fetching page {page}: {str(e)}")
    
    return urls

# Example usage
if __name__ == "__main__":
    # Get database manager
    db_manager = get_db_manager()
    
    if not db_manager:
        logging.warning("No database connection available. Using CSV storage only.")
    
    # Option 1: Scrape from predefined list of URLs
    project_urls = [
        "https://devfolio.co/projects/example-project-1",
        "https://devfolio.co/projects/example-project-2",
        # Add more URLs
    ]
    
    # Option 2: Get URLs from listing pages
    # project_urls = get_project_urls(start_page=1, end_page=5)
    
    # Optional: List of rotating proxies
    proxies = [
        # "http://proxy1:port",
        # "http://proxy2:port",
    ]
    
    # Initialize and run scraper
    scraper = DevfolioScraper(proxies=proxies, db_manager=db_manager)
    results = scraper.batch_scrape(project_urls, output_file="devfolio_projects.csv")
    
    # Clean up
    if db_manager:
        db_manager.close() 