import time

import pymongo
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
import numpy as np
import dotenv
import os

dotenv.load_dotenv()
# Replace with your actual connection string
COSMOSDB_CONNECTION_STRING = os.getenv("COSMOSDB_CONNECTION_STRING")
DB_NAME = os.environ.get("COSMOS_DB_NAME")
COLLECTION_NAME = os.environ.get("COSMOS_COLLECTION_NAME")


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
    except ConnectionFailure as e:
        print(f"MongoDB connection failed: {e}")
    except OperationFailure as e:
        print(f"MongoDB operation failed: {e}")
    finally:
        end_time = time.time()
        log_time("Connection", start_time, end_time)
    return None


def get_collection(client, db_name, collection_name):
    start_time = time.time()
    try:
        db = client[db_name]
        collection = db[collection_name]
        return collection
    except Exception as e:
        print(f"An error occurred while getting the collection: {e}")
        return None
    finally:
        end_time = time.time()
        log_time("Get Collection", start_time, end_time)


def insert_document(collection, document):
    start_time = time.time()
    try:
        result = collection.insert_one(document)
        print(f"Document inserted with _id: {result.inserted_id}")
    except Exception as e:
        print(f"An error occurred while inserting the document: {e}")
    finally:
        end_time = time.time()
        log_time("Insert Document", start_time, end_time)


def read_documents(collection, query):
    start_time = time.time()
    try:
        documents = collection.find(query)
        for doc in documents:
            print(doc)
    except Exception as e:
        print(f"An error occurred while reading documents: {e}")
    finally:
        end_time = time.time()
        log_time("Read Documents", start_time, end_time)


def update_document(collection, query, new_values):
    start_time = time.time()
    try:
        result = collection.update_one(query, {"$set": new_values})
        print(f"Matched {result.matched_count} document(s) and modified {result.modified_count} document(s)")
    except Exception as e:
        print(f"An error occurred while updating the document: {e}")
    finally:
        end_time = time.time()
        log_time("Update Document", start_time, end_time)


def delete_document(collection, query):
    start_time = time.time()
    try:
        result = collection.delete_one(query)
        print(f"Deleted {result.deleted_count} document(s)")
    except Exception as e:
        print(f"An error occurred while deleting the document: {e}")
    finally:
        end_time = time.time()
        log_time("Delete Document", start_time, end_time)


def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


def find_similar_documents_v2(collection, query_vector):
    start_time = time.time()
    try:
        documents = collection.find({})
        similarities = []
        for doc in documents:
            doc_vector = doc["vector"]
            similarity = cosine_similarity(query_vector, doc_vector)
            similarities.append((doc, similarity))
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities
    except Exception as e:
        print(f"An error occurred while finding similar documents: {e}")
        return None
    finally:
        end_time = time.time()
        log_time("Find Similar Documents", start_time, end_time)


def find_similar_documents(collection, embedding, threshold=0.9):
    start_time = time.time()
    try:
        documents = collection.find()
        similar_docs = []
        for doc in documents:
            if 'embedding' in doc:
                similarity = cosine_similarity(embedding, np.array(doc['embedding']))
                if similarity > threshold:
                    similar_docs.append(doc)
        for doc in similar_docs:
            print(doc)
    except Exception as e:
        print(f"An error occurred while finding similar documents: {e}")
    finally:
        end_time = time.time()
        log_time("Find Similar Documents", start_time, end_time)


if __name__ == "__main__":
    client_org = connect_to_cosmosdb(COSMOSDB_CONNECTION_STRING)

    if client_org:
        db_name = DB_NAME  # replace with your actual database name
        collection_name = COLLECTION_NAME  # replace with your actual collection name

        collection_org = get_collection(client_org, db_name, collection_name)

        if collection_org is not None:
            # Insert a document
            embedding = np.random.rand(128).tolist()
            # Here instead of dummy_doc you can pass the actual document you want to insert -> only for testing purposes bc we dont have embeddings using ada-002 here
            document = {"name": "John Doe", "age": 30, "city": "New York"}
            insert_document(collection_org, document)

            # Read documents
            query = {"name": "John Doe"}
            read_documents(collection_org, query)

            # Update a document
            new_values = {"age": 31}
            update_document(collection_org, query, new_values)

            # Delete a document
            delete_document(collection_org, query)

            # Find similar documents
            new_embedding = np.random.rand(128)
            find_similar_documents(collection_org, new_embedding)
