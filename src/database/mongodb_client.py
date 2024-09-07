from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import logging
from src.config import COSMOSDB_CONNECTION_STRING, DB_NAME, COSMOS_COLLECTION_NAME


class MongoDBClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDBClient, cls).__new__(cls)
            cls._instance.__initialized = False
        return cls._instance

    def __init__(self):
        if self.__initialized:
            return
        self.client = None
        self.db = None
        self.collection = None
        self.__initialized = True

    def connect(self):
        if self.client is None:
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
        if self.client is None:
            self.connect()
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
        if self.client is None:
            self.connect()
        try:
            k = int(num_results)
            results = self.collection.aggregate([
                {
                    "$search": {
                        "cosmosSearch": {
                            "vector": query_embedding,
                            "path": "vector",
                            "k": k
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
            logging.error(f"Vector search operation failed: {e}", exc_info=True)
            return []
