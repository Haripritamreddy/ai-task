# app.py
import os
from flask import Flask, request, jsonify
from threading import Thread
from scraper import scrape_and_add_documents  # Import the scraping function
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables
load_dotenv()

# Initialize Chroma Vector Store (do this only once)
embedding_function = GoogleGenerativeAIEmbeddings(google_api_key=os.getenv('GOOGLE_API_KEY'),model="models/text-embedding-004")
vector_store = Chroma(
    collection_name="example_collection",
    embedding_function=embedding_function,
    persist_directory="./chroma_langchain_2_db",
)

# Start scraping in the background
def start_scraping_thread():
    thread = Thread(target=scrape_and_add_documents)
    thread.daemon = True  # Allow the main thread to exit even if the scraper is running
    thread.start()

# Initialize the scraping thread within the application context
with app.app_context():
    start_scraping_thread()

# Health check endpoint
@app.route('/health')
def health():
    return jsonify({"status": "ok"})

# Search endpoint
@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    query = data.get('text')
    top_k = data.get('top_k', 4)  # Default to 4 if not specified
    threshold = data.get('threshold', 0.8)  # Default to 0.8 if not specified

    if not query:
        return jsonify({"error": "Missing 'text' parameter"}), 400

    # Perform the search
    results = vector_store.similarity_search_with_relevance_scores(query, k=top_k, score_threshold=threshold)

    # Format the results
    formatted_results = [{"page_content": doc.page_content, "score": score} for doc, score in results]
    
    return jsonify(formatted_results)

if __name__ == "__main__":
    app.run(debug=True, port=5000) 