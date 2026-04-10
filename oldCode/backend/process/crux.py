import re
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer

nltk.download('stopwords')
from nltk.corpus import stopwords

stop_words = list(set(stopwords.words('english')).union({
    'project', 'solution', 'aim', 'system', 'feature', 'challenges', 'makes', 
    'aims', 'user', 'uses', 'provides', 'allows', 'helps', 'like', 'include',
    'using', 'providing', 'solves', 'integration', 'app', 'application', 'ran',
}))

def preprocess_text(text):
    text = re.sub(r'[^\w\s]', '', text)  
    return text.lower()

def extract_crux_words(project_details, num_words=20):
    description = project_details.get('projectDescription', "")
    processed_description = preprocess_text(description)
    
    if not processed_description.strip():
        return [] 
    
    vectorizer = TfidfVectorizer(stop_words=stop_words, max_features=200)
    tfidf_matrix = vectorizer.fit_transform([processed_description])
    terms = vectorizer.get_feature_names_out()
    scores = tfidf_matrix.toarray().flatten()
    term_scores = sorted(zip(terms, scores), key=lambda x: x[1], reverse=True)
    crux_words = [term for term, score in term_scores[:num_words]]
    
    return crux_words

def crux(scrappedData):
    crux_words = extract_crux_words(scrappedData)
    return crux_words