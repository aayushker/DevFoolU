import os
import argparse
import logging
import pandas as pd
from datetime import datetime
from url_scraper import get_project_urls, collect_project_metadata
from batch_scraper import DevfolioScraper

# Configure logging
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
log_file = os.path.join(LOG_DIR, f"scrape_manager_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

def main():
    parser = argparse.ArgumentParser(description="Devfolio Project Scraping Manager")
    parser.add_argument("--collect-urls", action="store_true", help="Collect project URLs from Devfolio")
    parser.add_argument("--collect-metadata", action="store_true", help="Collect basic metadata without full scraping")
    parser.add_argument("--full-scrape", action="store_true", help="Perform full scraping of project details")
    parser.add_argument("--start-page", type=int, default=1, help="Starting page number")
    parser.add_argument("--end-page", type=int, default=10, help="Ending page number")
    parser.add_argument("--batch-size", type=int, default=100, help="Batch size for full scraping")
    parser.add_argument("--url-file", type=str, default="project_urls.csv", help="File with project URLs")
    parser.add_argument("--metadata-file", type=str, default="project_metadata.csv", help="File with project metadata")
    parser.add_argument("--output-file", type=str, default="devfolio_projects.csv", help="Output file for full scraping")
    parser.add_argument("--use-proxies", action="store_true", help="Use proxy rotation (requires proxy list)")
    parser.add_argument("--proxy-list", type=str, default="proxies.txt", help="File with proxy list (one per line)")
    
    args = parser.parse_args()
    
    # Step 1: Collect URLs if requested
    if args.collect_urls:
        logging.info(f"Starting URL collection from pages {args.start_page} to {args.end_page}")
        urls = get_project_urls(
            start_page=args.start_page,
            end_page=args.end_page,
            output_file=args.url_file
        )
        logging.info(f"Collected {len(urls)} project URLs")
    
    # Step 2: Collect metadata if requested
    if args.collect_metadata:
        if not os.path.exists(args.url_file):
            logging.error(f"URL file {args.url_file} not found. Run with --collect-urls first.")
            return
            
        logging.info(f"Starting metadata collection from {args.url_file}")
        collect_project_metadata(
            url_file=args.url_file,
            output_file=args.metadata_file
        )
    
    # Step 3: Full scraping if requested
    if args.full_scrape:
        if not os.path.exists(args.url_file) and not os.path.exists(args.metadata_file):
            logging.error("Neither URL file nor metadata file found. Run with --collect-urls or --collect-metadata first.")
            return
        
        # Load URLs to scrape
        if os.path.exists(args.metadata_file):
            # Prioritize URLs from metadata file
            df = pd.read_csv(args.metadata_file)
            urls = df["URL"].tolist()
            logging.info(f"Loaded {len(urls)} URLs from metadata file")
        else:
            df = pd.read_csv(args.url_file)
            urls = df["URL"].tolist()
            logging.info(f"Loaded {len(urls)} URLs from URL file")
        
        # Load proxies if requested
        proxies = None
        if args.use_proxies:
            if os.path.exists(args.proxy_list):
                with open(args.proxy_list, "r") as f:
                    proxies = [line.strip() for line in f if line.strip()]
                logging.info(f"Loaded {len(proxies)} proxies from {args.proxy_list}")
            else:
                logging.warning(f"Proxy list file {args.proxy_list} not found. Running without proxies.")
        
        # Process in batches
        for i in range(0, len(urls), args.batch_size):
            batch_urls = urls[i:i+args.batch_size]
            batch_output = f"batch_{i//args.batch_size}_{args.output_file}"
            
            logging.info(f"Processing batch {i//args.batch_size + 1}, URLs {i} to {i+len(batch_urls)-1}")
            
            scraper = DevfolioScraper(proxies=proxies)
            batch_results = scraper.batch_scrape(batch_urls, output_file=batch_output)
            
            logging.info(f"Completed batch {i//args.batch_size + 1}, scraped {len(batch_results)} projects")
        
        # Merge batches if more than one
        batch_files = [f for f in os.listdir(".") if f.startswith("batch_") and f.endswith(args.output_file)]
        if len(batch_files) > 1:
            logging.info(f"Merging {len(batch_files)} batch files")
            
            all_data = []
            for file in batch_files:
                try:
                    df = pd.read_csv(file)
                    all_data.append(df)
                except Exception as e:
                    logging.error(f"Error reading batch file {file}: {str(e)}")
            
            if all_data:
                merged_df = pd.concat(all_data, ignore_index=True)
                merged_df.drop_duplicates(subset=["Project URL"], keep="first", inplace=True)
                merged_df.to_csv(args.output_file, index=False)
                logging.info(f"Merged data saved to {args.output_file}, {len(merged_df)} projects")
    
    logging.info("Scraping manager completed")

if __name__ == "__main__":
    main() 