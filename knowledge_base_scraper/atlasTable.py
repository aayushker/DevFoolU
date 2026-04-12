from pymongo import MongoClient
from pymongo.errors import OperationFailure
from pymongo.server_api import ServerApi

try:
    from env_utils import require_env_value
except ImportError:
    from knowledge_base_scraper.env_utils import require_env_value

# --- 1. Configuration ---

CONNECTION_STRING = require_env_value("MONGODB_URL")

# Specify your database and collection names
DATABASE_NAME = "DevFoolU"  # Replace with your desired database name
COLLECTION_NAME = "Cluster0"         # Replace with your desired collection name

# --- 2. Define the Schema Validator ---
# This schema enforces that all your fields are "required"
project_schema_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            "urlOfProject",
            "nameOfProject",
            "descriptionOfProject",
            "problemSolved",
            "challengesFaced",
            "technologiesUsed",
            "embeddingsOfData"
        ],
        "properties": {
            "urlOfProject": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "nameOfProject": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "descriptionOfProject": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "problemSolved": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "challengesFaced": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "technologiesUsed": {
                "bsonType": "array",
                "items": {"bsonType": "string"},
                "description": "must be an array of strings and is required"
            },
            "embeddingsOfData": {
                "bsonType": "array",
                # Assuming embeddings are floating-point numbers
                "items": {"bsonType": "double"}, 
                "description": "must be an array of numbers (embeddings) and is required"
            }
        }
    }
}

# --- 3. Connect and Create/Update Collection ---

try:
    # Connect to MongoDB Atlas
    client = MongoClient(CONNECTION_STRING, server_api=ServerApi('1'))
    # Ping the server to confirm connection
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")

    # Get the database
    db = client[DATABASE_NAME]

    # Try to create the collection with the validator
    try:
        db.create_collection(
            COLLECTION_NAME,
            validator=project_schema_validator,
            validationLevel="strict"
        )
        print(f"\nCollection '{COLLECTION_NAME}' created successfully with validation.")
        
    except OperationFailure as e:
        # If collection already exists, update its validation rules
        if "already exists" in str(e):
            print(f"\nCollection '{COLLECTION_NAME}' already exists. Updating validation...")
            db.command(
                "collMod", 
                COLLECTION_NAME, 
                validator=project_schema_validator, 
                validationLevel="strict"
            )
            print("Validation rules updated successfully.")
        else:
            print(f"An error occurred: {e}")

    # --- 4. Test the Validation ---
    
    projects_collection = db[COLLECTION_NAME]

    # --- Example 1: A VALID document ---
    valid_project = {
        "urlOfProject": "https://github.com/my-user/my-project",
        "nameOfProject": "My AI Portfolio Project",
        "descriptionOfProject": "A project that solves a cool problem using AI.",
        "problemSolved": "The problem of finding matching documents.",
        "challengesFaced": "Getting the embedding dimensions right.",
        "technologiesUsed": ["Python", "MongoDB", "PyTorch", "FastAPI"],
        "embeddingsOfData": [0.123, 0.456, 0.789, -0.234]
    }

    try:
        result = projects_collection.insert_one(valid_project)
        print(f"\nSuccessfully inserted valid document with id: {result.inserted_id}")
    except Exception as e:
        print(f"\nError inserting valid document: {e}")


    # --- Example 2: An INVALID document (missing 'nameOfProject') ---
    invalid_project = {
        "urlOfProject": "https://github.com/my-user/bad-project",
        # "nameOfProject": "This field is missing!",
        "descriptionOfProject": "This document will be rejected.",
        "problemSolved": "N/A",
        "challengesFaced": "N/A",
        "technologiesUsed": ["Basic"],
        "embeddingsOfData": [0.1, 0.2]
    }

    print("\nAttempting to insert an invalid document (missing 'nameOfProject')...")
    try:
        projects_collection.insert_one(invalid_project)
        print("Error: The invalid document was inserted (validation might be off).")
    except OperationFailure as e:
        print("Successfully caught expected error:")
        print(f"Error details: {e.details}")
        
except Exception as e:
    print(f"An error occurred during connection or setup: {e}")

finally:
    # Close the connection
    if 'client' in locals():
        client.close()
        print("\nMongoDB connection closed.")