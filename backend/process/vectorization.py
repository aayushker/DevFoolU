import pandas as pd
from keybert import KeyBERT
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
kw_model = KeyBERT()
def extract_keybert_crux(description, num_keywords=15):
    keywords = kw_model.extract_keywords(description, keyphrase_ngram_range=(1, 2), stop_words='english', top_n=num_keywords)
    crux_words = [keyword[0] for keyword in keywords]
    return crux_words
def calculate_similarity(crux1, crux2):
    text1 = " ".join(crux1)
    text2 = " ".join(crux2)
    vectorizer = CountVectorizer().fit_transform([text1, text2])
    vectors = vectorizer.toarray()
    cosine_sim = cosine_similarity(vectors)
    similarity_percentage = cosine_sim[0][1] * 100
    return similarity_percentage

def process_projects(ps_crux_words, csv_file_path="/home/gopatron/Documents/WebD Codes/HackCBS/backend/process/devfolio_projects.csv"):
    df = pd.read_csv(csv_file_path)

    df['Description Crux'] = df['Project Description'].apply(lambda desc: extract_keybert_crux(desc))

    df['Similarity with PS (%)'] = df['Description Crux'].apply(lambda crux: calculate_similarity(crux, ps_crux_words))
    df['Similarity with PS (%)'] = df['Similarity with PS (%)'] * 3.5

    top_5_similar_projects = df.nlargest(5, 'Similarity with PS (%)')

    df.to_csv("devfolio_projects_with_keybert_crux.csv", index=False)

    top_5_similar_projects[['Project URL', 'Project Name', 'Description Crux', 'Similarity with PS (%)']].to_csv("top_5_similar_projects.csv", index=False)

    result = {
        "all_projects": df.to_dict(orient='records'),
        "top_5_similar_projects": top_5_similar_projects[['Project URL', 'Project Name', 'Description Crux', 'Similarity with PS (%)']].to_dict(orient='records')
    }

    return result
def vectorization(ps_crux_words):
    result = process_projects(ps_crux_words)
    return result