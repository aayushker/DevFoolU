#!/usr/bin/env python3
"""
Import existing project data into MongoDB
"""
import os
import sys
import argparse
import logging
from dotenv import load_dotenv
from .db_manager import get_db_manager, DatabaseManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("import_data.log"),
        logging.StreamHandler()
    ]
)

def import_file(db_manager, file_path, include_crux=True):
    """
    Import a CSV file into MongoDB
    
    Args:
        db_manager: Database manager instance
        file_path: Path to CSV file
        include_crux: Whether to import crux words
        
    Returns:
        int: Number of records imported
    """
    if not os.path.exists(file_path):
        logging.error(f"File not found: {file_path}")
        return 0
        
    logging.info(f"Importing data from {file_path}")
    count = db_manager.import_from_csv(file_path, include_crux=include_crux)
    logging.info(f"Imported {count} records from {file_path}")
    
    return count

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Import project data into MongoDB")
    parser.add_argument("--file", type=str, help="CSV file to import")
    parser.add_argument("--directory", type=str, help="Directory containing CSV files to import")
    parser.add_argument("--connection", type=str, help="MongoDB connection string (optional, will use MONGODB_URI env var if not provided)")
    parser.add_argument("--skip-crux", action="store_true", help="Skip importing crux words")
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Get database manager
    db_manager = None
    if args.connection:
        db_manager = DatabaseManager(args.connection)
    else:
        db_manager = get_db_manager()
        
    if not db_manager:
        logging.error("Failed to connect to MongoDB. Check your connection string.")
        sys.exit(1)
    
    total_imported = 0
    
    # Import specific file
    if args.file:
        total_imported += import_file(db_manager, args.file, include_crux=not args.skip_crux)
    
    # Import all CSV files in directory
    if args.directory:
        if not os.path.isdir(args.directory):
            logging.error(f"Directory not found: {args.directory}")
            sys.exit(1)
            
        csv_files = [f for f in os.listdir(args.directory) if f.endswith('.csv')]
        
        if not csv_files:
            logging.warning(f"No CSV files found in {args.directory}")
        else:
            logging.info(f"Found {len(csv_files)} CSV files to import")
            
            for file in csv_files:
                file_path = os.path.join(args.directory, file)
                total_imported += import_file(db_manager, file_path, include_crux=not args.skip_crux)
    
    # If neither file nor directory specified, check for default files
    if not args.file and not args.directory:
        default_files = [
            "devfolio_projects.csv",
            "devfolio_projects_with_keybert_crux.csv"
        ]
        
        for file in default_files:
            if os.path.exists(file):
                total_imported += import_file(db_manager, file, include_crux=not args.skip_crux)
    
    # Print summary
    logging.info(f"Import completed. Total records imported: {total_imported}")
    
    # Close database connection
    db_manager.close()

if __name__ == "__main__":
    main() 