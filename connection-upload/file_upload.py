import time
import json
import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
import dotenv

dotenv.load_dotenv()
COSMOSDB_CONNECTION_STRING = os.getenv("COSMOSDB_CONNECTION_STRING")
DB_NAME = os.environ.get("DB_NAME")
COLLECTION_NAME = os.environ.get("COSMOS_COLLECTION_NAME")
EMBEDDINGS_FOLDER = r"C:\Users\szyme\to_be_parsed\output\embeddings\pdf"


def log_time(operation_name, start_time, end_time):
    duration = end_time - start_time
    print(f"{operation_name} took {duration:.4f} seconds")


def connect_to_cosmosdb(connection_string):
    start_time = time.time()
    try:
        client = MongoClient(connection_string)
        client.admin.command('ismaster')
        print("MongoDB connection established successfully.")
        return client
    except (ConnectionFailure, OperationFailure) as e:
        print(f"MongoDB connection or operation failed: {e}")
    finally:
        end_time = time.time()
        log_time("Connection", start_time, end_time)
    return None


def get_or_create_collection(client, db_name, collection_name):
    start_time = time.time()
    try:
        db = client[db_name]
        if collection_name not in db.list_collection_names():
            print(f"Creating new collection: {collection_name}")
            db.create_collection(collection_name)
        collection = db[collection_name]
        return collection
    except Exception as e:
        print(f"An error occurred while getting/creating the collection: {e}")
        return None
    finally:
        end_time = time.time()
        log_time("Get/Create Collection", start_time, end_time)


def load_embeddings(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
    except Exception as e:
        print(f"Error loading embeddings file: {e}")
        return None


def insert_documents(collection, documents):
    start_time = time.time()
    try:
        result = collection.insert_many(documents)
        print(f"Inserted {len(result.inserted_ids)} documents")
    except Exception as e:
        print(f"An error occurred while inserting documents: {e}")
    finally:
        end_time = time.time()
        log_time("Insert Documents", start_time, end_time)


def process_json_files(folder_path, collection):
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)
            print(f"Processing file: {filename}")
            embeddings_data = load_embeddings(file_path)
            if embeddings_data:
                documents = [
                    {"content": page[f"Page {i + 1}"], "vector": vector}
                    for i, (page, vector) in enumerate(zip(embeddings_data["pages"], embeddings_data["vectors"]))
                ]
                insert_documents(collection, documents)


def main():
    client = connect_to_cosmosdb(COSMOSDB_CONNECTION_STRING)
    if not client:
        return

    collection = get_or_create_collection(client, DB_NAME, COLLECTION_NAME)
    if collection is None:
        return

    process_json_files(EMBEDDINGS_FOLDER, collection)

    client.close()


if __name__ == "__main__":
    main()
