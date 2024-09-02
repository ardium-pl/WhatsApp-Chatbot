from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import logging
from config import COSMOSDB_CONNECTION_STRING, DB_NAME, COSMOS_COLLECTION_NAME


class MongoDBClient:
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None

    def connect(self):
        try:
            self.client = MongoClient(COSMOSDB_CONNECTION_STRING)
            self.client.admin.command("ismaster")
            self.db = self.client[DB_NAME]
            self.collection = self.db[COSMOS_COLLECTION_NAME]
            logging.info("MongoDB connection established successfully.")
        except ConnectionFailure as e:
            logging.error(f"Could not connect to MongoDB due to: {e}")
            raise ConnectionError("Failed to connect to MongoDB.") from e

    def ensure_vector_search_index(self):
        try:
            index_name = "vectorSearchIndex"
            existing_indexes = self.collection.list_indexes()
            if any(index["name"] == index_name for index in existing_indexes):
                logging.info(f"Vector search index {index_name} already exists")
                return

            self.collection.create_index(
                [("vector", "cosmosSearch")],
                name=index_name,
                cosmosSearchOptions={
                    "kind": "vector-ivf",
                    "numLists": 1,
                    "similarity": "COS",
                    "dimensions": 1536
                }
            )
            logging.info(f"Index {index_name} created successfully")
        except Exception as e:
            logging.error(f"Error creating vector search index: {e}")
            raise

    def vector_search(self, query_embedding, num_results=10):
        try:
            results = self.collection.aggregate([
                {
                    "$search": {
                        "cosmosSearch": {
                            "vector": query_embedding,
                            "path": "vector",
                            "k": num_results
                        }
                    }
                },
                {
                    "$project": {
                        "similarityScore": {"$meta": "searchScore"},
                        "content": 1,
                        "_id": 1,
                        "title": 1,
                        "pageNumber": 1,
                        "createdAt": 1,
                        "wordCount": {"$size": {"$split": ["$content", " "]}}
                    }
                }
            ])

            return list(results)
        except Exception as e:
            logging.error(f"Vector search operation failed: {e}")
            return []

    def close(self):
        if self.client:
            self.client.close()
