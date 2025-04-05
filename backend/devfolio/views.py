# from .serializers import EncodeSerializers
from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework.response import Response
import logging
import traceback
import os
from process.scrapper import scrapper
from process.crux import crux
from process.vectorization import vectorization
from process.db_manager import get_db_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename=os.path.join(os.path.dirname(__file__), "../logs/api.log")
)

# Ensure logs directory exists
os.makedirs(os.path.join(os.path.dirname(__file__), "../logs"), exist_ok=True)

# Heartbeat request
def Heartbeat(request):
    """Simple heartbeat endpoint to verify backend is running"""
    # Check database connection if available
    db_status = "unavailable"
    try:
        db_manager = get_db_manager()
        if db_manager:
            db_manager.client.admin.command('ping')
            db_status = "connected"
            db_manager.close()
    except Exception as e:
        logging.error(f"Database connection error: {str(e)}")
        db_status = f"error: {str(e)}"
    
    return JsonResponse({
        'status': 'Backend is active',
        'database': db_status
    })

def Stats(request):
    """
    Get statistics about the project database
    
    Returns:
        JSON response with project count and other stats
    """
    try:
        # Get database connection
        db_manager = get_db_manager()
        stats = {
            'total_projects': 0,
            'processed_projects': 0,
            'latest_projects': [],
            'db_status': 'unavailable'
        }
        
        if db_manager:
            # Get total number of projects
            stats['total_projects'] = db_manager.projects.count_documents({})
            
            # Get number of projects with crux words (processed projects)
            stats['processed_projects'] = db_manager.projects.count_documents({"crux_words": {"$exists": True}})
            
            # Get 5 latest projects (for showcase)
            latest_projects = list(db_manager.projects.find(
                {}, 
                {"_id": 0, "project_url": 1, "project_name": 1, "tech_stack": 1}
            ).sort("last_updated", -1).limit(5))
            
            stats['latest_projects'] = latest_projects
            stats['db_status'] = 'connected'
            
            # Close connection
            db_manager.close()
        else:
            # Fallback to CSV for stats if no DB connection
            try:
                import pandas as pd
                import os
                
                csv_path = os.path.join(os.path.dirname(__file__), "../process/devfolio_projects.csv")
                if os.path.exists(csv_path):
                    df = pd.read_csv(csv_path)
                    stats['total_projects'] = len(df)
                    stats['processed_projects'] = len(df[df['Description Crux'].notna()])
                    
                    # Get latest 5 projects (or all if less than 5)
                    latest_count = min(5, len(df))
                    latest_df = df.head(latest_count)
                    
                    stats['latest_projects'] = latest_df[['Project URL', 'Project Name', 'Tech Stack']].to_dict(orient='records')
                    stats['db_status'] = 'csv-fallback'
            except Exception as e:
                logging.error(f"CSV fallback error: {str(e)}")
        
        logging.info("Stats endpoint accessed")
        return JsonResponse({
            'status': 'success',
            'data': stats
        })
    except Exception as e:
        logging.error(f"Error getting stats: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f'Error: {str(e)}'
        }, status=500)

class Devfolio(APIView):
    """API for checking project similarity on Devfolio"""
    
    def post(self, request, *args, **kwargs):
        """
        Process a new project URL for plagiarism detection
        
        Expects:
            projectURL (str): URL of the Devfolio project to check
            
        Returns:
            JSON response with similarity results or error
        """
        projectURL = request.data.get('projectURL')
        
        logging.info(f"Received request for project: {projectURL}")
        
        if not projectURL or not isinstance(projectURL, str):
            logging.warning("Invalid project URL provided")
            return Response({
                'status': 'error', 
                'message': 'Missing or invalid project URL'
            }, status=400)
            
        if not projectURL.startswith('https://devfolio.co/projects/'):
            logging.warning(f"Invalid URL format: {projectURL}")
            return Response({
                'status': 'error', 
                'message': 'Invalid URL format. URL must start with https://devfolio.co/projects/'
            }, status=400)
            
        try:
            # Step 1: Scrape project data
            logging.info(f"Scraping data from {projectURL}")
            scrapedData = scrapper(projectURL)
            
            if not scrapedData or not scrapedData.get('projectDescription'):
                logging.warning(f"No data found for {projectURL}")
                return Response({
                    'status': 'error', 
                    'message': 'No project data found or empty project description'
                }, status=404)
                
            # Step 2: Extract crux words
            logging.info(f"Extracting crux from project description")
            cruxedData = crux(scrapedData)
            
            if not cruxedData:
                logging.warning(f"Failed to extract crux words from {projectURL}")
                return Response({
                    'status': 'error',
                    'message': 'Failed to extract key information from project description'
                }, status=500)
                
            # Step 3: Check for similarity with other projects
            logging.info(f"Calculating similarity with existing projects")
            result = vectorization(cruxedData, projectURL)
            
            if not result or not result.get('top_5_similar_projects'):
                logging.warning(f"No similarity results for {projectURL}")
                return Response({
                    'status': 'warning',
                    'message': 'No similar projects found',
                    'data': {'top_5_similar_projects': []}
                }, status=200)
                
            # Step 4: Return results
            logging.info(f"Successfully processed {projectURL}")
            return Response({
                'status': 'success',
                'data': result
            }, status=200)
            
        except Exception as e:
            error_details = traceback.format_exc()
            logging.error(f"Error processing {projectURL}: {str(e)}\n{error_details}")
            
            return Response({
                'status': 'error',
                'message': f'Error: {str(e)}',
                'details': error_details if os.getenv('DEBUG') == 'True' else None
            }, status=500)