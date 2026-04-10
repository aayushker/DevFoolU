from pymongo import MongoClient
from pymongo.server_api import ServerApi
from sentence_transformers import SentenceTransformer
from typing import List, Dict
import time

# MongoDB Configuration
CONNECTION_STRING = "mongodb+srv://singhaayushker_db_user:y3aQRy6lKFQfkrDa@cluster0.w8pounl.mongodb.net/?appName=Cluster0"
DATABASE_NAME = "DevFoolU"
COLLECTION_NAME = "Cluster0"

# Initialize the embedding model
print("Loading embedding model...")
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
print("✅ Model loaded successfully!\n")

def create_combined_text(project: Dict) -> str:
    """
    Combine all relevant fields from a project document into a single text
    for embedding generation.
    """
    parts = []
    
    # Add project name
    if project.get('nameOfProject'):
        parts.append(f"Project: {project['nameOfProject']}")
    
    # Add description
    if project.get('descriptionOfProject'):
        parts.append(f"Description: {project['descriptionOfProject']}")
    
    # Add problem solved
    if project.get('problemSolved'):
        parts.append(f"Problem: {project['problemSolved']}")
    
    # Add challenges faced
    if project.get('challengesFaced'):
        parts.append(f"Challenges: {project['challengesFaced']}")
    
    # Add technologies
    if project.get('technologiesUsed') and isinstance(project['technologiesUsed'], list):
        tech_str = ", ".join(project['technologiesUsed'])
        if tech_str:
            parts.append(f"Technologies: {tech_str}")
    
    # Combine all parts with separator
    combined = " | ".join(parts)
    
    # If combined text is empty, use at least the project name or URL
    if not combined.strip():
        combined = project.get('nameOfProject', project.get('urlOfProject', 'Unknown Project'))
    
    return combined

def generate_embedding(text: str) -> List[float]:
    """Generate embedding vector for given text"""
    embedding = model.encode(text)
    return embedding.tolist()

def fetch_and_update_embeddings():
    """
    Fetch each project from MongoDB, generate embeddings, and update the document
    """
    try:
        # Connect to MongoDB with improved settings
        print("Connecting to MongoDB Atlas...")
        client = MongoClient(
            CONNECTION_STRING,
            server_api=ServerApi('1'),
            serverSelectionTimeoutMS=60000,
            connectTimeoutMS=60000,
            socketTimeoutMS=60000,
            retryWrites=True,
            w='majority'
        )
        
        # Ping to confirm connection
        client.admin.command('ping')
        print("✅ Successfully connected to MongoDB!\n")
        
        # Get database and collection
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        
        # Count total projects
        total_projects = collection.count_documents({})
        print(f"Found {total_projects} projects in the database.")
        
        if total_projects == 0:
            print("No projects found. Please insert data first.")
            return
        
        # Query to find projects without embeddings or with empty embeddings
        query = {
            "$or": [
                {"embeddingsOfData": {"$exists": False}},
                {"embeddingsOfData": []},
                {"embeddingsOfData": None}
            ]
        }
        
        # Count projects without embeddings
        projects_without_embeddings = collection.count_documents(query)
        projects_with_embeddings = total_projects - projects_without_embeddings
        
        print(f"Projects with embeddings: {projects_with_embeddings}")
        print(f"Projects without embeddings: {projects_without_embeddings}\n")
        
        if projects_without_embeddings == 0:
            print("✅ All projects already have embeddings! No work to do.")
            client.close()
            return
        
        # Fetch only projects without embeddings
        print("Starting embedding generation and update process...\n")
        print("-" * 80)
        
        updated_count = 0
        failed_count = 0
        
        # Process each project one by one (only those without embeddings)
        for idx, project in enumerate(collection.find(query), 1):
            project_id = project['_id']
            project_name = project.get('nameOfProject', 'Unknown')
            
            try:
                # Create combined text for embedding
                combined_text = create_combined_text(project)
                
                # Generate embedding
                print(f"[{idx}/{projects_without_embeddings}] 🔄 Processing: '{project_name[:50]}...'")
                embedding = generate_embedding(combined_text)
                
                # Update the document in MongoDB
                result = collection.update_one(
                    {'_id': project_id},
                    {'$set': {'embeddingsOfData': embedding}}
                )
                
                if result.modified_count > 0:
                    print(f"[{idx}/{projects_without_embeddings}] ✅ Updated with {len(embedding)}-dim embedding")
                    updated_count += 1
                else:
                    print(f"[{idx}/{projects_without_embeddings}] ⚠️  No changes made")
                
                # Small delay to avoid overwhelming the database
                time.sleep(0.1)
                
            except Exception as e:
                print(f"[{idx}/{projects_without_embeddings}] ❌ Error processing '{project_name[:50]}...': {e}")
                failed_count += 1
                continue
        
        # Print summary
        print("-" * 80)
        print("\n📊 Summary:")
        print(f"   Total projects in database: {total_projects}")
        print(f"   Projects that already had embeddings: {projects_with_embeddings}")
        print(f"   Projects processed: {projects_without_embeddings}")
        print(f"   ✅ Successfully updated: {updated_count}")
        print(f"   ❌ Failed: {failed_count}")
        print(f"\n🎉 Embedding generation complete!")
        
        # Close connection
        client.close()
        print("\nMongoDB connection closed.")
        
    except Exception as e:
        print(f"\n❌ Error during MongoDB operation: {e}")
        print("\nTroubleshooting tips:")
        print("1. Check your internet connection")
        print("2. Verify MongoDB Atlas cluster is running")
        print("3. Check if your IP address is whitelisted in MongoDB Atlas")
        print("4. Ensure the collection exists and has data")

def main():
    """Main function"""
    print("=" * 80)
    print("📝 MongoDB Embedding Generator")
    print("=" * 80)
    print()
    
    # Ask for confirmation
    response = input("This will generate and update embeddings for all projects.\nContinue? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        print()
        fetch_and_update_embeddings()
    else:
        print("Operation cancelled.")

if __name__ == "__main__":
    main()
