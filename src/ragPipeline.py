# Knowledge base: fixed DevOps runbooks (no external embedding model required)
DOCS = [
    {
        "id": "doc_db_01",
        "text": (
            "Error: psycopg2.OperationalError: FATAL: too many connections. "
            "Fix: Increase max_connections in postgresql.conf or implement "
            "connection pooling using PgBouncer."
        ),
        "keywords": [
            "psycopg2",
            "operationalerror",
            "too many connections",
            "postgresql",
            "max_connections",
            "pgbouncer",
            "database",
            "connection",
        ],
    },
    {
        "id": "doc_net_01",
        "text": (
            "Error: TimeoutError: Request to external payment gateway API timed out. "
            "Fix: Check network egress rules, verify the external gateway status page, "
            "and ensure exponential backoff retries are active in the microservice."
        ),
        "keywords": [
            "timeout",
            "timed out",
            "payment gateway",
            "egress",
            "network",
            "retry",
            "backoff",
            "external api",
        ],
    },
    {
        "id": "doc_auth_01",
        "text": (
            "Error: KeyError: 'user_auth_token' missing. "
            "Fix: Ensure the frontend router is passing the Authorization header with a "
            "valid Bearer token. Check the auth middleware validation logic."
        ),
        "keywords": [
            "keyerror",
            "user_auth_token",
            "authorization",
            "bearer",
            "token",
            "auth",
            "middleware",
            "401",
            "403",
        ],
    },
    {
        "id": "doc_mem_01",
        "text": (
            "Error: MemoryError: Unable to allocate 2.4GiB for array shape. "
            "Fix: The batch size is too large for the available RAM. Reduce batch size "
            "in the data loader configuration or upgrade the EC2 instance memory."
        ),
        "keywords": [
            "memoryerror",
            "allocate",
            "out of memory",
            "oom",
            "ram",
            "batch size",
            "giB",
            "memory",
        ],
    },
]


def setup_knowledge_base():
    """Load the in-memory knowledge base (no vector DB download)."""
    print(f"Knowledge base ready ({len(DOCS)} documents).")
    return DOCS


def _score_doc(error_message: str, doc: dict) -> int:
    haystack = error_message.lower()
    return sum(1 for kw in doc["keywords"] if kw in haystack)


def retrieve_relevant_docs(error_message, doc_store):
    """Return the runbook whose keywords best match the error line."""
    print("\nSearching knowledge base for context regarding the error...")

    ranked = sorted(doc_store, key=lambda d: _score_doc(error_message, d), reverse=True)
    best = ranked[0]
    if _score_doc(error_message, best) == 0:
        print("No keyword match; using default database runbook.")
        return doc_store[0]["text"]

    print(f"Found relevant documentation: {best['text'][:80]}...")
    return best["text"]
