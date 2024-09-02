from logger import logger_cosmos
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
import os

load_dotenv()

# MongoDB connection details
CONNECTION_STRING = os.environ.get("COSMOSDB_CONNECTION_STRING")
DB_NAME = os.environ.get("DB_NAME")
COLLECTION_NAME = os.environ.get("COSMOS_COLLECTION_NAME")

# MongoDB connection function
def connect_to_cosmosdb(connection_string):
    try:
        client = MongoClient(connection_string)
        client.admin.command("ismaster")
        logger_cosmos.info("MongoDB connection established successfully.")
        return client
    except ConnectionFailure as e:
        logger_cosmos.error(f"Could not connect to MongoDB due to: {e}")
        # return None
        raise ConnectionError("Failed to connect to MongoDB.") from e
