import re
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer

# Download stopwords if not already present
nltk.download('stopwords')
from nltk.corpus import stopwords

# Define a set of common stop words and project-related words to exclude
stop_words = list(set(stopwords.words('english')).union({
    'project', 'solution', 'aim', 'system', 'feature', 'challenges', 'makes', 
    'aims', 'user', 'uses', 'provides', 'allows', 'helps', 'like', 'include',
    'using', 'providing', 'solves', 'integration', 'app', 'application', 'ran',
}))

# Function to preprocess text (remove punctuation, convert to lowercase)
def preprocess_text(text):
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    return text.lower()

# Function to extract crux words
def extract_crux_words(project_details, num_words=20):
    description = project_details.get('projectDescription', "")
    processed_description = preprocess_text(description)
    
    if not processed_description.strip():
        return []  # Return an empty list if the description is empty or only contains stop words
    
    # Set up TF-IDF vectorizer with custom stop words
    vectorizer = TfidfVectorizer(stop_words=stop_words, max_features=200)
    tfidf_matrix = vectorizer.fit_transform([processed_description])
    
    # Extract top terms based on TF-IDF scores
    terms = vectorizer.get_feature_names_out()
    scores = tfidf_matrix.toarray().flatten()
    term_scores = sorted(zip(terms, scores), key=lambda x: x[1], reverse=True)
    
    # Get the top num_words terms with highest scores
    crux_words = [term for term, score in term_scores[:num_words]]
    
    return crux_words

def crux(scrappedData):
    # Extract crux words from the project description
    crux_words = extract_crux_words(scrappedData)
    return crux_words