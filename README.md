## Caching Strategy

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