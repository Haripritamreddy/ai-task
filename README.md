# Docker Guide

### Step 1: Set Environment Variables

Ensure that your `.env` file contains all the necessary environment variables. This file should be placed in the root directory of your project.

**Example `.env` file:**

```bash
GOOGLE_API_KEY=your_google_api_key(https://aistudio.google.com/)
```
### Step 2: Build the Docker Image

Navigate to the root directory of your project where the `Dockerfile` is located and run the following command to build the Docker image:

```bash
docker build -t my-flask-app .
```
This command builds an image named `my-flask-app` from the `Dockerfile` in the current directory.

### Step 3: Run the Docker Container

After building the image, you can run a container from it with the following command:

```bash
docker run -p 5000:5000 my-flask-app
```
This will start your application and make it accessible on port 5000.

###Testing
```
curl http://localhost:5000/health
```
and

```
curl -X POST -H "Content-Type: application/json" -d "{\"text\": \"What is component one?\", \"top_k\": 2, \"threshold\": 0.2, \"user_id\": 1234}" http://localhost:5000/search

```

# Caching Strategy

A caching mechanism to store the results of frequently asked queries. This helps reduce the load on the vector database and significantly speeds up response times for repeated queries.

**How it works:**

1. When a new query arrives, the application first checks if the query exists in the cache.
2. If the query is found in the cache (**cache hit**), the cached results are retrieved and returned immediately, bypassing the need to query the vector database.
3. If the query is not found in the cache (**cache miss**), the application performs a similarity search on the vector database, retrieves the relevant documents, and stores the query and its results in the cache for future use.

**Benefits of Caching:**

- **Reduced Latency:** Caching significantly reduces the time it takes to retrieve results for repeated queries, as it avoids the more computationally expensive vector database search.
- **Improved Performance:** By reducing the load on the vector database, caching improves the overall performance and responsiveness of the application.
- **Cost Savings:**  In cases where the vector database is a cloud-based service, caching can help reduce costs associated with query operations.

## SQLite for Caching

This application uses SQLite as the caching mechanism. SQLite is a lightweight, file-based database that offers several advantages for this use case:

### Benefits of SQLite:

- **Simplicity:** SQLite is very easy to set up and use. It requires no separate server or complex configuration.
- **Persistence:** The cache data is stored in a file (`cache.db`), ensuring that the cache persists even if the application restarts.
- **Portability:** SQLite databases are single files, making them easily portable and deployable.
- **Zero Configuration:** SQLite requires no configuration, making it ideal for simple caching scenarios.


## Logging

The application includes logging to track cache hits and misses. This information can be useful for monitoring the effectiveness of the caching strategy and identifying potential areas for improvement.

**Example Log Messages:**
2024-09-14 15:30:00 INFO: Retrieved results from cache for query: What is component one?
127.0.0.1 - - [14/Sep/2024 15:30:00] "POST /search HTTP/1.1" 200 -
2024-09-14 15:31:00 INFO: Retrieved results from vector store for query: What is component two?
127.0.0.1 - - [14/Sep/2024 15:31:00] "POST /search HTTP/1.1" 200 -