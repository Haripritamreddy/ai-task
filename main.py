import os
import sqlite3
import json
import logging
import time
from flask import Flask, request, jsonify
from threading import Thread
from scraper import scrape_and_add_documents
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

# Rate limiting parameters (requests per minute)
RATE_LIMIT = 5
TIME_WINDOW = 60  # seconds

# Initialize request tracking dictionary
request_counts = {}

# Load environment variables
load_dotenv()

# Initialize SQLite database and table (if not exists)
DATABASE = 'cache.db'
conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS cache (
        query TEXT PRIMARY KEY,
        results TEXT
    )
''')
conn.commit()
conn.close() 

# Initialize Chroma Vector Store
embedding_function = GoogleGenerativeAIEmbeddings(
    google_api_key=os.getenv('GOOGLE_API_KEY'), 
    model="models/text-embedding-004"
)
vector_store = Chroma(
    collection_name="example_collection",
    embedding_function=embedding_function,
    persist_directory="./chroma_langchain_2_db"
)

# Start scraping in the background
def start_scraping_thread():
    thread = Thread(target=scrape_and_add_documents)
    thread.daemon = True
    thread.start()

# Initialize the scraping thread within the application context
with app.app_context():
    start_scraping_thread()


# Rate limiting decorator
def rate_limit(func):
    def wrapper(*args, **kwargs):
        user_id = request.get_json().get('user_id')  # Get user_id from request

        if user_id not in request_counts:
            request_counts[user_id] = []

        current_time = time.time()
        request_counts[user_id] = [
            ts for ts in request_counts[user_id] if current_time - ts <= TIME_WINDOW
        ]  # Remove expired timestamps

        if len(request_counts[user_id]) >= RATE_LIMIT:
            logger.warning(f"Rate limit exceeded for user: {user_id}")
            return jsonify({"error": "Rate limit exceeded"}), 429

        request_counts[user_id].append(current_time)
        return func(*args, **kwargs)

    return wrapper

# Health check endpoint
@app.route('/health')
def health():
    return jsonify({"status": "ok"})

# Search endpoint with rate limiting, inference time recording, and cache retrieval time
@app.route('/search', methods=['POST'])
@rate_limit
def search():
    data = request.get_json()
    query = data.get('text')
    top_k = data.get('top_k', 2)
    threshold = data.get('threshold', 0.2)

    start_time = time.time()

    # Check if the query is in the cache
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT results FROM cache WHERE query = ?", (query,))
    row = cursor.fetchone()
    conn.close()

    if row:
        cached_results = json.loads(row[0])
        end_time = time.time()
        inference_time = end_time - start_time
        logger.info(f"Retrieved results from cache for query: {query} (Inference time: {inference_time:.4f} seconds)")
        return jsonify(cached_results)

    # Perform vector search and get results
    results = vector_store.similarity_search_with_relevance_scores(
        query, k=top_k, score_threshold=threshold
    )
    formatted_results = [
        {"page_content": doc.page_content, "score": score}
        for doc, score in results
    ]

    # Store the results in the cache
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO cache (query, results) VALUES (?, ?)", (query, json.dumps(formatted_results)))
    conn.commit()
    conn.close()

    end_time = time.time()
    inference_time = end_time - start_time
    logger.info(f"Retrieved results from vector store for query: {query} (Inference time: {inference_time:.4f} seconds)")
    return jsonify(formatted_results)

if __name__ == "__main__":
    app.run(debug=True, port=5000)