import pandas as pd
from keybert import KeyBERT
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Initialize KeyBERT model
kw_model = KeyBERT()

# Define a function to extract crux keywords using KeyBERT
def extract_keybert_crux(description, num_keywords=15):
    keywords = kw_model.extract_keywords(description, keyphrase_ngram_range=(1, 2), stop_words='english', top_n=num_keywords)
    # Extract only the keyword phrases without scores
    crux_words = [keyword[0] for keyword in keywords]
    return crux_words

# Define a function to calculate similarity percentage
def calculate_similarity(crux1, crux2):
    # Convert lists to strings for vectorization
    text1 = " ".join(crux1)
    text2 = " ".join(crux2)
    # Initialize CountVectorizer
    vectorizer = CountVectorizer().fit_transform([text1, text2])
    vectors = vectorizer.toarray()
    # Compute cosine similarity
    cosine_sim = cosine_similarity(vectors)
    similarity_percentage = cosine_sim[0][1] * 100  # Convert to percentage
    return similarity_percentage

def process_projects(ps_crux_words, csv_file_path="devfolio_projects.csv"):
    # Load CSV file
    df = pd.read_csv(csv_file_path)

    # Apply KeyBERT extraction and add as a new column
    df['Description Crux'] = df['Project Description'].apply(lambda desc: extract_keybert_crux(desc))

    # Calculate similarity with problem statement's crux words
    df['Similarity with PS (%)'] = df['Description Crux'].apply(lambda crux: calculate_similarity(crux, ps_crux_words))
    # Double the similarity percentage values
    df['Similarity with PS (%)'] = df['Similarity with PS (%)'] * 2.56

    # Sort by similarity and select top 5
    top_5_similar_projects = df.nlargest(5, 'Similarity with PS (%)')

    # Convert the results to a dictionary
    result = {
        "all_projects": df.to_dict(orient='records'),
        "top_5_similar_projects": top_5_similar_projects[['Project URL', 'Project Name', 'Description Crux', 'Similarity with PS (%)']].to_dict(orient='records')
    }

    return result

def vectorization(ps_crux_words):
    result = process_projects(ps_crux_words)
    return result