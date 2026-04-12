import pandas as pd
import json
from typing import List, Dict
from pymongo import MongoClient
from pymongo.server_api import ServerApi

try:
    from env_utils import require_env_value
except ImportError:
    from knowledge_base_scraper.env_utils import require_env_value

# MongoDB Configuration
CONNECTION_STRING = require_env_value("MONGODB_URL")
DATABASE_NAME = "DevFoolU"
COLLECTION_NAME = "Cluster0"

def parse_tech_stack(tech_stack_str: str) -> List[str]:
    """Parse comma-separated tech stack string into list"""
    if pd.isna(tech_stack_str) or tech_stack_str.strip() == "":
        return []
    # Remove quotes and split by comma
    tech_list = [tech.strip().strip('"') for tech in tech_stack_str.split(',')]
    # Filter out empty strings
    return [tech for tech in tech_list if tech]

def transform_row_to_document(row: pd.Series) -> Dict:
    """Transform a CSV row into MongoDB document format"""
    return {
        "urlOfProject": row['urlOfProject'] if pd.notna(row['urlOfProject']) else "",
        "nameOfProject": row['nameOfProject'] if pd.notna(row['nameOfProject']) else "",
        "descriptionOfProject": row['descriptionOfProject'] if pd.notna(row['descriptionOfProject']) else "",
        "problemSolved": row['problemSolved'] if pd.notna(row['problemSolved']) else "",
        "challengesFaced": row['challengesFaced'] if pd.notna(row['challengesFaced']) else "",
        "technologiesUsed": parse_tech_stack(row['technologiesUsed']) if pd.notna(row['technologiesUsed']) else [],
        "embeddingsOfData": []  # Keeping empty, will be generated later
    }

def load_and_transform_csv(csv_path: str) -> List[Dict]:
    """Load CSV and transform all rows to MongoDB documents"""
    # Read CSV
    df = pd.read_csv(csv_path)
    
    # Transform each row
    documents = []
    for _, row in df.iterrows():
        doc = transform_row_to_document(row)
        # Only add if required fields are present
        if doc['urlOfProject'] and doc['nameOfProject']:
            documents.append(doc)
    
    return documents

def insert_to_mongodb(documents: List[Dict]):
    """Insert transformed documents into MongoDB, skipping duplicates based on urlOfProject"""
    try:
        # Connect to MongoDB with improved settings
        print("Attempting to connect to MongoDB...")
        print("Please ensure your IP is whitelisted in MongoDB Atlas...")
        
        client = MongoClient(
            CONNECTION_STRING,
            server_api=ServerApi('1'),
            serverSelectionTimeoutMS=30000,
            connectTimeoutMS=30000,
            socketTimeoutMS=None,
            tls=True,
            tlsAllowInvalidCertificates=False
        )
        
        # Ping to confirm connection
        client.admin.command('ping')
        print("✓ Successfully connected to MongoDB!")
        
        # Get database and collection
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        
        # Get existing URLs from MongoDB to check for duplicates
        print("\nChecking for existing projects in database...")
        existing_urls = set()
        try:
            existing_projects = collection.find({}, {"urlOfProject": 1})
            existing_urls = {doc['urlOfProject'] for doc in existing_projects if 'urlOfProject' in doc}
            print(f"Found {len(existing_urls)} existing projects in database")
        except Exception as e:
            print(f"Warning: Could not fetch existing URLs: {e}")
        
        # Filter out duplicates
        if documents:
            new_documents = []
            duplicate_count = 0
            
            for doc in documents:
                if doc['urlOfProject'] in existing_urls:
                    duplicate_count += 1
                    print(f"⊘ Skipping duplicate: {doc['nameOfProject'][:50]}...")
                else:
                    new_documents.append(doc)
            
            print(f"\n{'='*60}")
            print(f"Total documents to process: {len(documents)}")
            print(f"Duplicates found (skipped): {duplicate_count}")
            print(f"New documents to insert: {len(new_documents)}")
            print(f"{'='*60}\n")
            
            if not new_documents:
                print("No new documents to insert. All projects already exist in database.")
                client.close()
                return
            
            # Insert new documents in smaller batches to avoid timeout
            batch_size = 100  # Insert 100 documents at a time
            total_inserted = 0
            failed_inserts = 0
            
            for i in range(0, len(new_documents), batch_size):
                batch = new_documents[i:i+batch_size]
                try:
                    result = collection.insert_many(batch, ordered=False)
                    total_inserted += len(result.inserted_ids)
                    print(f"✓ Inserted batch {i//batch_size + 1}: {len(result.inserted_ids)} documents")
                except Exception as batch_error:
                    failed_inserts += len(batch)
                    print(f"✗ Error in batch {i//batch_size + 1}: {batch_error}")
                    continue
            
            print(f"\n{'='*60}")
            print(f"Total successfully inserted: {total_inserted} documents")
            if failed_inserts > 0:
                print(f"Failed to insert: {failed_inserts} documents")
            print(f"{'='*60}")
        else:
            print("No valid documents to insert.")
        
        # Close connection
        client.close()
        print("\nMongoDB connection closed.")
        
    except Exception as e:
        print(f"\n✗ Error during MongoDB operation: {e}")
        print("\n" + "="*60)
        print("TROUBLESHOOTING STEPS:")
        print("="*60)
        print("1. Go to MongoDB Atlas (https://cloud.mongodb.com)")
        print("2. Navigate to: Network Access → IP Access List")
        print("3. Click 'Add IP Address'")
        print("4. Either add your current IP or click 'Allow Access from Anywhere'")
        print("5. Wait 1-2 minutes for changes to propagate")
        print("6. Try running this script again")
        print("="*60)

def main():
    # Path to your CSV file
    csv_file_path = "/home/gopatron/Documents/DevFoolU/knowledge_base_scraper/projects_data.csv"
    
    print("Starting CSV to MongoDB transformation...")
    print(f"Reading CSV from: {csv_file_path}\n")
    
    # Load and transform data
    documents = load_and_transform_csv(csv_file_path)
    
    print(f"Transformed {len(documents)} documents")
    print("\nSample document:")
    print(json.dumps(documents[0], indent=2))
    
    # Ask for confirmation before inserting
    response = input("\nDo you want to insert these documents into MongoDB? (yes/no): ")
    
    if response.lower() == 'yes':
        insert_to_mongodb(documents)
    else:
        print("Insertion cancelled.")

if __name__ == "__main__":
    main()