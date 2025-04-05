import os
import logging
import pymongo
from pymongo import MongoClient
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="db_manager.log"
)

# Load environment variables
load_dotenv()

class DatabaseManager:
    """MongoDB database manager for Devfolio project data"""
    
    def __init__(self, connection_string=None):
        """
        Initialize MongoDB connection
        
        Args:
            connection_string (str): MongoDB connection string. If None, read from MONGODB_URI env var
        """
        if connection_string is None:
            connection_string = os.getenv("MONGODB_URI")
            
        if not connection_string:
            raise ValueError("MongoDB connection string not provided and MONGODB_URI env var not set")
            
        try:
            self.client = MongoClient(connection_string)
            self.db = self.client.devfolio_db
            self.projects = self.db.projects
            self.similarity_results = self.db.similarity_results
            
            # Create indexes for better performance
            self._create_indexes()
            
            # Verify connection
            self.client.admin.command('ping')
            logging.info("Connected to MongoDB successfully")
            
        except Exception as e:
            logging.error(f"Failed to connect to MongoDB: {str(e)}")
            raise
    
    def _create_indexes(self):
        """Create necessary indexes for efficient queries"""
        try:
            # Project URL as unique identifier
            self.projects.create_index([("project_url", pymongo.ASCENDING)], unique=True)
            
            # Text index for searching project descriptions
            self.projects.create_index([("project_description", pymongo.TEXT)])
            
            # Index for tech stack filtering
            self.projects.create_index([("tech_stack", pymongo.ASCENDING)])
            
            # Index for last_updated field for data freshness checks
            self.projects.create_index([("last_updated", pymongo.DESCENDING)])
            
            # Indexes for similarity results
            self.similarity_results.create_index([("source_project_url", pymongo.ASCENDING)])
            self.similarity_results.create_index([("timestamp", pymongo.DESCENDING)])
            
            logging.info("Created database indexes")
        except Exception as e:
            logging.error(f"Failed to create indexes: {str(e)}")
    
    def get_existing_urls(self):
        """
        Get all project URLs already in the database
        
        Returns:
            set: Set of project URLs
        """
        try:
            return set(doc["project_url"] for doc in self.projects.find({}, {"project_url": 1}))
        except Exception as e:
            logging.error(f"Error getting existing URLs: {str(e)}")
            return set()
    
    def save_project(self, project_data, crux_words=None):
        """
        Save a single project to the database
        
        Args:
            project_data (dict): Dictionary containing project data
            crux_words (list): Optional list of crux words for the project
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            project_url = project_data.get("Project URL")
            
            if not project_url:
                logging.warning("Cannot save project without URL")
                return False
                
            doc = {
                "project_url": project_url,
                "project_name": project_data.get("Project Name") or project_data.get("projectName", ""),
                "project_description": project_data.get("Project Description") or project_data.get("projectDescription", ""),
                "tech_stack": project_data.get("Tech Stack", ""),
                "last_updated": datetime.now()
            }
            
            if crux_words:
                doc["crux_words"] = crux_words
            
            # Upsert - update if exists, insert if doesn't
            result = self.projects.update_one(
                {"project_url": project_url},
                {"$set": doc},
                upsert=True
            )
            
            return result.acknowledged
            
        except Exception as e:
            logging.error(f"Error saving project {project_data.get('Project URL')}: {str(e)}")
            return False
    
    def save_batch(self, projects, crux_data=None):
        """
        Save a batch of projects efficiently with bulk operations
        
        Args:
            projects (list): List of project data dictionaries
            crux_data (dict): Optional dictionary mapping project URLs to crux words
            
        Returns:
            int: Number of projects saved
        """
        if not projects:
            return 0
            
        try:
            operations = []
            
            for project in projects:
                project_url = project.get("Project URL")
                if not project_url:
                    continue
                    
                doc = {
                    "project_url": project_url,
                    "project_name": project.get("Project Name") or project.get("projectName", ""),
                    "project_description": project.get("Project Description") or project.get("projectDescription", ""),
                    "tech_stack": project.get("Tech Stack", ""),
                    "last_updated": datetime.now()
                }
                
                if crux_data and project_url in crux_data:
                    doc["crux_words"] = crux_data[project_url]
                
                operations.append(
                    pymongo.UpdateOne(
                        {"project_url": project_url},
                        {"$set": doc},
                        upsert=True
                    )
                )
            
            if operations:
                result = self.projects.bulk_write(operations)
                logging.info(f"Saved batch of {len(operations)} projects")
                return result.upserted_count + result.modified_count
            
            return 0
            
        except Exception as e:
            logging.error(f"Error in batch save: {str(e)}")
            return 0
    
    def save_similarity_results(self, source_url, results):
        """
        Save similarity results for a project
        
        Args:
            source_url (str): URL of the source project
            results (list): List of similar projects with similarity scores
            
        Returns:
            bool: True if saved successfully
        """
        try:
            # First delete any existing results
            self.similarity_results.delete_many({"source_project_url": source_url})
            
            # Insert new results
            if not results:
                return True
                
            documents = []
            for result in results:
                documents.append({
                    "source_project_url": source_url,
                    "matched_project_url": result.get("Project URL"),
                    "matched_project_name": result.get("Project Name"),
                    "similarity_score": result.get("Similarity with PS (%)"),
                    "timestamp": datetime.now()
                })
            
            if documents:
                self.similarity_results.insert_many(documents)
                
            return True
            
        except Exception as e:
            logging.error(f"Error saving similarity results for {source_url}: {str(e)}")
            return False
    
    def get_project_by_url(self, url):
        """
        Get a project by its URL
        
        Args:
            url (str): Project URL
            
        Returns:
            dict: Project data or None if not found
        """
        try:
            return self.projects.find_one({"project_url": url})
        except Exception as e:
            logging.error(f"Error getting project {url}: {str(e)}")
            return None
    
    def get_all_projects(self, limit=None, with_crux=False):
        """
        Get all projects
        
        Args:
            limit (int): Optional limit on number of projects to return
            with_crux (bool): Whether to include projects with crux words only
            
        Returns:
            list: List of projects
        """
        try:
            query = {}
            if with_crux:
                query["crux_words"] = {"$exists": True}
                
            projection = {
                "_id": 0, 
                "project_url": 1,
                "project_name": 1,
                "project_description": 1,
                "tech_stack": 1,
                "crux_words": 1,
                "last_updated": 1
            }
            
            cursor = self.projects.find(query, projection)
            
            if limit:
                cursor = cursor.limit(limit)
                
            return list(cursor)
            
        except Exception as e:
            logging.error(f"Error getting all projects: {str(e)}")
            return []
    
    def get_similarity_results(self, source_url):
        """
        Get similarity results for a project
        
        Args:
            source_url (str): Source project URL
            
        Returns:
            list: List of similarity results
        """
        try:
            results = list(self.similarity_results.find(
                {"source_project_url": source_url},
                {"_id": 0}
            ).sort("similarity_score", pymongo.DESCENDING))
            
            return results
        except Exception as e:
            logging.error(f"Error getting similarity results for {source_url}: {str(e)}")
            return []
    
    def export_to_csv(self, output_file="mongodb_export.csv"):
        """
        Export projects to CSV for backup or analysis
        
        Args:
            output_file (str): Output CSV filename
            
        Returns:
            bool: True if export successful
        """
        try:
            projects = self.get_all_projects()
            
            if not projects:
                logging.warning("No projects to export")
                return False
                
            # Convert MongoDB documents to DataFrame
            df = pd.DataFrame(projects)
            
            # Handle date formatting
            if "last_updated" in df.columns:
                df["last_updated"] = df["last_updated"].apply(lambda x: x.strftime("%Y-%m-%d %H:%M:%S") if x else "")
            
            # Handle list fields
            if "crux_words" in df.columns:
                df["crux_words"] = df["crux_words"].apply(lambda x: ", ".join(x) if x else "")
            
            df.to_csv(output_file, index=False)
            logging.info(f"Exported {len(df)} projects to {output_file}")
            
            return True
            
        except Exception as e:
            logging.error(f"Error exporting to CSV: {str(e)}")
            return False
            
    def import_from_csv(self, input_file, include_crux=True):
        """
        Import projects from CSV file
        
        Args:
            input_file (str): Input CSV file
            include_crux (bool): Whether to import crux words
            
        Returns:
            int: Number of projects imported
        """
        try:
            df = pd.read_csv(input_file)
            
            if df.empty:
                logging.warning(f"No data in {input_file}")
                return 0
                
            projects = df.to_dict("records")
            
            # Handle crux words
            crux_data = {}
            if include_crux and "crux_words" in df.columns:
                for project in projects:
                    url = project.get("Project URL") or project.get("project_url")
                    crux = project.get("crux_words")
                    
                    if url and crux and isinstance(crux, str):
                        crux_data[url] = [word.strip() for word in crux.split(",")]
            
            # Standardize column names
            formatted_projects = []
            for project in projects:
                formatted = {}
                
                # Map different possible column names to standard ones
                url = project.get("Project URL") or project.get("project_url")
                if not url:
                    continue
                    
                formatted["Project URL"] = url
                formatted["Project Name"] = project.get("Project Name") or project.get("project_name", "")
                formatted["Project Description"] = project.get("Project Description") or project.get("project_description", "")
                formatted["Tech Stack"] = project.get("Tech Stack") or project.get("tech_stack", "")
                
                formatted_projects.append(formatted)
            
            if formatted_projects:
                count = self.save_batch(formatted_projects, crux_data)
                logging.info(f"Imported {count} projects from {input_file}")
                return count
                
            return 0
            
        except Exception as e:
            logging.error(f"Error importing from CSV {input_file}: {str(e)}")
            return 0
    
    def close(self):
        """Close database connection"""
        try:
            self.client.close()
            logging.info("Closed MongoDB connection")
        except Exception as e:
            logging.error(f"Error closing MongoDB connection: {str(e)}")


# Helper Functions
def get_db_manager():
    """
    Get a database manager instance with connection from environment variables
    
    Returns:
        DatabaseManager: Database manager instance
    """
    try:
        mongodb_uri = os.getenv("MONGODB_URI")
        if not mongodb_uri:
            logging.error("MONGODB_URI environment variable not set")
            return None
            
        return DatabaseManager(mongodb_uri)
    except Exception as e:
        logging.error(f"Failed to create database manager: {str(e)}")
        return None


# Example usage
if __name__ == "__main__":
    # Test the database manager
    try:
        # This requires MONGODB_URI in .env file or environment
        db_manager = get_db_manager()
        
        if db_manager:
            # Example operations
            print(f"Connected to MongoDB. Projects collection has {db_manager.projects.count_documents({})} documents")
            
            # Import existing CSV data if available
            csv_file = "devfolio_projects_with_keybert_crux.csv"
            if os.path.exists(csv_file):
                print(f"Importing data from {csv_file}...")
                count = db_manager.import_from_csv(csv_file)
                print(f"Imported {count} projects")
            
            # Close connection
            db_manager.close()
            
    except Exception as e:
        print(f"Error in database manager test: {str(e)}") 