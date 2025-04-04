import pandas as pd
import logging
from keybert import KeyBERT
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from db_manager import get_db_manager
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Initialize KeyBERT model
kw_model = KeyBERT()

def extract_keybert_crux(description, num_keywords=15):
    """
    Extract key phrases from a project description using KeyBERT
    
    Args:
        description (str): Project description text
        num_keywords (int): Number of keywords to extract
        
    Returns:
        list: List of keywords/phrases
    """
    if not description or not isinstance(description, str):
        return []
    
    try:
        keywords = kw_model.extract_keywords(
            description, 
            keyphrase_ngram_range=(1, 2), 
            stop_words='english', 
            top_n=num_keywords
        )
        crux_words = [keyword[0] for keyword in keywords]
        return crux_words
    except Exception as e:
        logging.error(f"Error extracting keywords: {str(e)}")
        return []

def calculate_similarity(crux1, crux2):
    """
    Calculate similarity between two sets of crux words
    
    Args:
        crux1 (list): First list of crux words
        crux2 (list): Second list of crux words
        
    Returns:
        float: Similarity percentage (0-100)
    """
    if not crux1 or not crux2:
        return 0
    
    try:
        text1 = " ".join(crux1)
        text2 = " ".join(crux2)
        vectorizer = CountVectorizer().fit_transform([text1, text2])
        vectors = vectorizer.toarray()
        cosine_sim = cosine_similarity(vectors)
        similarity_percentage = cosine_sim[0][1] * 100
        return similarity_percentage
    except Exception as e:
        logging.error(f"Error calculating similarity: {str(e)}")
        return 0

def process_projects_mongodb(ps_crux_words, db_manager, max_results=5):
    """
    Calculate similarity between the provided project crux and all projects in the database
    
    Args:
        ps_crux_words (list): List of crux words from the project to check
        db_manager: Database manager instance
        max_results (int): Maximum number of similar projects to return
        
    Returns:
        dict: Dictionary with all_projects and top_similar_projects
    """
    try:
        # Get all projects with crux words from database
        projects = db_manager.get_all_projects(with_crux=True)
        
        if not projects:
            logging.warning("No projects with crux words found in database")
            return {"all_projects": [], "top_5_similar_projects": []}
        
        logging.info(f"Calculating similarity for {len(projects)} projects")
        
        # Calculate similarity for each project
        for project in projects:
            project_crux = project.get("crux_words", [])
            similarity = calculate_similarity(project_crux, ps_crux_words)
            
            # Apply scaling factor similar to the original code
            similarity = similarity * 3.5
            
            # Ensure we don't exceed 100%
            similarity = min(similarity, 100.0)
            
            # Add similarity score to project
            project["Similarity with PS (%)"] = similarity
            
            # Format for compatibility with original code
            project["Project URL"] = project.get("project_url", "")
            project["Project Name"] = project.get("project_name", "")
            project["Project Description"] = project.get("project_description", "")
            project["Description Crux"] = project.get("crux_words", [])
        
        # Sort projects by similarity
        sorted_projects = sorted(projects, key=lambda p: p["Similarity with PS (%)"], reverse=True)
        
        # Get top similar projects
        top_similar_projects = sorted_projects[:max_results] if len(sorted_projects) >= max_results else sorted_projects
        
        # Save to database
        if ps_crux_words and "Project URL" in projects[0]:
            source_url = projects[0]["Project URL"]
            db_manager.save_similarity_results(source_url, top_similar_projects)
        
        # Create result dictionary similar to original format
        result = {
            "all_projects": sorted_projects,
            "top_5_similar_projects": top_similar_projects
        }
        
        return result
    
    except Exception as e:
        logging.error(f"Error processing projects from MongoDB: {str(e)}")
        return {"all_projects": [], "top_5_similar_projects": []}

def process_projects_csv(ps_crux_words, csv_file_path):
    """
    Legacy CSV-based project processing
    
    Args:
        ps_crux_words (list): List of crux words from the project to check
        csv_file_path (str): Path to CSV file with project data
        
    Returns:
        dict: Dictionary with all_projects and top_similar_projects
    """
    try:
        if not os.path.exists(csv_file_path):
            logging.error(f"CSV file not found: {csv_file_path}")
            return {"all_projects": [], "top_5_similar_projects": []}
            
        df = pd.read_csv(csv_file_path)

        # Extract crux words for each project if not already done
        if "Description Crux" not in df.columns:
            df["Description Crux"] = df["Project Description"].apply(lambda desc: extract_keybert_crux(desc))

        # Calculate similarity with the provided project
        df["Similarity with PS (%)"] = df["Description Crux"].apply(lambda crux: calculate_similarity(crux, ps_crux_words))
        
        # Apply scaling factor (same as original code)
        df["Similarity with PS (%)"] = df["Similarity with PS (%)"] * 3.5
        
        # Cap at 100%
        df["Similarity with PS (%)"] = df["Similarity with PS (%)"].apply(lambda x: min(x, 100.0))

        # Get top similar projects
        top_5_similar_projects = df.nlargest(5, "Similarity with PS (%)")

        # Save results to CSV for reference
        df.to_csv("devfolio_projects_with_keybert_crux.csv", index=False)
        top_5_similar_projects[["Project URL", "Project Name", "Description Crux", "Similarity with PS (%)"]].to_csv("top_5_similar_projects.csv", index=False)

        # Format result dictionary
        result = {
            "all_projects": df.to_dict(orient="records"),
            "top_5_similar_projects": top_5_similar_projects[["Project URL", "Project Name", "Description Crux", "Similarity with PS (%)"]].to_dict(orient="records")
        }

        return result
        
    except Exception as e:
        logging.error(f"Error processing projects from CSV: {str(e)}")
        return {"all_projects": [], "top_5_similar_projects": []}

def vectorization(ps_crux_words, project_url=None):
    """
    Main function to calculate similarity between a project and existing projects
    
    Args:
        ps_crux_words (list): List of crux words from the project to check
        project_url (str): Optional project URL for saving results
        
    Returns:
        dict: Dictionary with all_projects and top_similar_projects
    """
    # Try to use MongoDB first
    db_manager = get_db_manager()
    
    if db_manager:
        logging.info("Using MongoDB for vectorization")
        
        # Store the crux words for this project if URL is provided
        if project_url:
            project = db_manager.get_project_by_url(project_url)
            if project:
                db_manager.save_project({"Project URL": project_url}, ps_crux_words)
        
        # Process using MongoDB
        result = process_projects_mongodb(ps_crux_words, db_manager)
        
        # Close database connection
        db_manager.close()
        
        return result
    else:
        # Fall back to CSV method
        logging.info("MongoDB not available, falling back to CSV")
        csv_file_path = os.path.join(os.path.dirname(__file__), "devfolio_projects.csv")
        result = process_projects_csv(ps_crux_words, csv_file_path)
        
        return result

# For testing
if __name__ == "__main__":
    # Example crux words
    test_crux = ["machine learning", "AI", "data", "analytics", "prediction", "model"]
    
    # Test with MongoDB or fall back to CSV
    results = vectorization(test_crux)
    
    # Print top similar projects
    if results and "top_5_similar_projects" in results:
        for i, project in enumerate(results["top_5_similar_projects"]):
            print(f"{i+1}. {project.get('Project Name')} - {project.get('Similarity with PS (%)'):.2f}%")