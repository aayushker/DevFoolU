# MongoDB Integration for DevFoolU

This document explains how to set up and use MongoDB Atlas with the DevFoolU project for efficient data storage and retrieval.

## Why MongoDB?

MongoDB Atlas provides several advantages for the DevFoolU project:

1. **Scalability**: Can easily handle large datasets of 300K+ projects
2. **Cloud-based**: Works well with Vercel/Render deployments
3. **Flexible schema**: Ideal for project data that may vary in structure
4. **Efficient querying**: Fast lookups for plagiarism detection
5. **Text search**: Built-in support for searching project descriptions

## Setup Instructions

### 1. Create a MongoDB Atlas Account

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register)
2. Create a free account
3. Create a new cluster (free tier is sufficient to start)

### 2. Configure Network Access

1. Go to Network Access in the Atlas dashboard
2. Click "Add IP Address"
3. Add your current IP address for local development
4. Add IP addresses for your Vercel/Render deployments or use "Allow Access from Anywhere" (less secure but easier for deployment)

### 3. Create a Database User

1. Go to Database Access
2. Click "Add New Database User"
3. Create a username and password (use a strong, random password)
4. Select "Read and write to any database" for permissions

### 4. Get Connection String

1. In your cluster, click "Connect"
2. Choose "Connect your application"
3. Select "Python" as the driver
4. Copy the connection string (it will look like: `mongodb+srv://<username>:<password>@<cluster>.mongodb.net/<dbname>?retryWrites=true&w=majority`)
5. Replace `<username>`, `<password>`, and `<dbname>` with your actual values

### 5. Configure Environment Variables

1. Copy the `.env.example` file to `.env` in the backend directory:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file and add your MongoDB connection string:
   ```
   MONGODB_URI=mongodb+srv://yourusername:yourpassword@yourcluster.mongodb.net/devfolio_db?retryWrites=true&w=majority
   ```

## Importing Existing Data

If you have existing project data in CSV files, you can import it to MongoDB:

```bash
# Import a specific file
python process/import_data.py --file devfolio_projects_with_keybert_crux.csv

# Import all CSV files in a directory
python process/import_data.py --directory data_directory/

# Skip importing crux words
python process/import_data.py --file devfolio_projects.csv --skip-crux
```

## Database Structure

The MongoDB database contains two main collections:

### 1. Projects Collection

Stores information about individual projects:

```json
{
  "project_url": "https://devfolio.co/projects/example-project",
  "project_name": "Example Project",
  "project_description": "This is an example project description...",
  "tech_stack": "Python, React, MongoDB",
  "crux_words": ["machine learning", "data", "analytics"],
  "last_updated": "2023-06-01T12:00:00Z"
}
```

### 2. Similarity Results Collection

Stores the results of similarity checks:

```json
{
  "source_project_url": "https://devfolio.co/projects/example-project",
  "matched_project_url": "https://devfolio.co/projects/similar-project",
  "matched_project_name": "Similar Project",
  "similarity_score": 85.75,
  "timestamp": "2023-06-01T12:30:00Z"
}
```

## Testing the MongoDB Connection

You can test if the MongoDB connection is working by:

1. Running the heartbeat endpoint:
   ```bash
   curl http://localhost:8000/api/heartbeat/
   ```
   
   You should see:
   ```json
   {
     "status": "Backend is active",
     "database": "connected"
   }
   ```

2. Checking the database manually:
   ```bash
   python -c "from process.db_manager import get_db_manager; db = get_db_manager(); print(f'Connected, projects count: {db.projects.count_documents({})}'); db.close()"
   ```

## Troubleshooting

### Connection Issues

1. **Wrong connection string**: Double-check your connection string and ensure the username, password, and cluster name are correct
2. **Network problems**: Ensure your IP is allowed in the network access settings
3. **Firewall issues**: Check if your firewall is blocking MongoDB connections

### Import Problems

1. **CSV format**: Ensure your CSV files have the expected column names
2. **Empty data**: Check if your CSV files have valid data
3. **Permissions**: Ensure your MongoDB user has write permissions

## Fallback Mechanism

The system is designed to fall back to CSV storage if MongoDB is unavailable. This ensures the application continues to work even if there are database connection issues. 