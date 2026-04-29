import chromadb
import os

# Define where our local vector database will live
DB_PATH = "../chroma_db"

def setup_knowledge_base():
    """Initializes ChromaDB and populates it with system documentation."""
    print("Initializing Vector Database...")
    
    # 1. Create a persistent client so data is saved to disk
    client = chromadb.PersistentClient(path=DB_PATH)

    # 2. Create a collection (similar to a table in SQL)
    # ChromaDB automatically uses 'all-MiniLM-L6-v2' to embed the text for us!
    collection = client.get_or_create_collection(name="devops_docs")

    # 3. Our "Official Documentation" (Dummy Data for our specific errors)
    documents = [
        "Error: psycopg2.OperationalError: FATAL: too many connections. Fix: Increase max_connections in postgresql.conf or implement connection pooling using PgBouncer.",
        "Error: TimeoutError: Request to external payment gateway API timed out. Fix: Check network egress rules, verify the external gateway status page, and ensure exponential backoff retries are active in the microservice.",
        "Error: KeyError: 'user_auth_token' missing. Fix: Ensure the frontend router is passing the Authorization header with a valid Bearer token. Check the auth middleware validation logic.",
        "Error: MemoryError: Unable to allocate 2.4GiB for array shape. Fix: The batch size is too large for the available RAM. Reduce batch size in the data loader configuration or upgrade the EC2 instance memory."
    ]
    
    # Unique IDs for each document
    ids = ["doc_db_01", "doc_net_01", "doc_auth_01", "doc_mem_01"]

    # 4. Insert into the database. (Chroma automatically converts these strings to vectors!)
    collection.upsert(documents=documents, ids=ids)
    
    print("✅ Knowledge base successfully populated with official documentation!")
    return collection

def retrieve_relevant_docs(error_message, collection):
    """Searches the database for the documentation closest to the error."""
    print(f"\n🔍 Searching knowledge base for context regarding the error...")
    
    # 5. Query the database
    results = collection.query(
        query_texts=[error_message],
        n_results=1 # We only want the single most relevant document
    )
    
    if results['documents'] and results['documents'][0]:
        retrieved_doc = results['documents'][0][0]
        print(f"📖 Found relevant documentation: {retrieved_doc}")
        return retrieved_doc
    
    return "No official documentation found for this error."

# Run this once to populate the database when the script is executed directly
if __name__ == "__main__":
    setup_knowledge_base()