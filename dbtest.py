from qdrant_client import QdrantClient
from functions import flist

# Initialize the client
client = QdrantClient(path="./assistant.db")

# Prepare your documents, metadata, and IDs
docs = flist

metadata = [
    {"source": "Search-function"},
    {"source": "weather-function"},
    {"source": "play-function"}
]
ids = [1, 2, 3]

# Use the new add method
client.add(
    collection_name="assistant",
    documents=docs,
    metadata=metadata,
    ids=ids
)

search_result = client.query(
    collection_name="assistant",
    query_text="what is the price of current stocks of nvidia?"
)

print("Search Result:", search_result)
