import time
import json
import openai
from openai import OpenAI
import pymongo
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
import numpy as np
import dotenv
import os
from sklearn.metrics.pairwise import cosine_similarity

dotenv.load_dotenv()

# Get the API key from the environment variable
OPENAI_API_KEY = os.getenv("OPEN_AI_KEY")
if not OPENAI_API_KEY:
    raise ValueError("No OpenAI API key found. Please set the OPEN_AI_KEY environment variable.")

# Initialize the OpenAI client with the API key
client = OpenAI(api_key=OPENAI_API_KEY)

# FILE_PATH = os.getenv("INPUT_PATH_FILE")
# if not FILE_PATH:
#     raise ValueError("No input file path found. Please set the INPUT_PATH_FILE environment variable.")

COSMOSDB_CONNECTION_STRING = os.getenv("COSMOSDB_CONNECTION_STRING")
DB_NAME = os.environ.get("DB_NAME")
COLLECTION_NAME = os.environ.get("COSMOS_COLLECTION_NAME")
EMBEDDINGS_FILE = os.environ.get("EMBEDDINGS_FILE")

# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

"""
This code here is a demo of how to use RAG-like capabilities to perform semantic search and generate responses based on data from DB.
Based on ceratain changes it should perform better than the previous code because it uses indexing and search capabilities of MongoDB.
"""


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
        if not isinstance(db_name, str):
            raise TypeError(f"db_name must be a string, got {type(db_name)}")
        if not isinstance(collection_name, str):
            raise TypeError(f"collection_name must be a string, got {type(collection_name)}")

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


def vector_search(collection, query_vector, top_k=5):
    start_time = time.time()
    try:
        results = list(collection.aggregate([
            {
                "$search": {
                    "cosmosSearch": {
                        "vector": query_vector,
                        "path": "vector",
                        "k": top_k
                    }
                }
            },
            {
                "$project": {
                    "content": 1,
                    "score": {"$meta": "searchScore"}
                }
            }
        ]))
        return results
    except Exception as e:
        print(f"An error occurred during vector search: {e}")
        return []
    finally:
        end_time = time.time()
        log_time("Vector Search", start_time, end_time)


def semantic_search(collection, query_text, top_k=5):
    start_time = time.time()
    try:
        results = list(collection.aggregate([
            {
                "$search": {
                    "text": {
                        "query": query_text,
                        "path": "content"
                    }
                }
            },
            {
                "$limit": top_k
            },
            {
                "$project": {
                    "content": 1,
                    "score": {"$meta": "searchScore"}
                }
            }
        ]))
        return results
    except Exception as e:
        print(f"An error occurred during semantic search: {e}")
        return []
    finally:
        end_time = time.time()
        log_time("Semantic Search", start_time, end_time)


def get_openai_response(query, search_results):
    client = OpenAI(api_key=OPENAI_API_KEY)

    # Prepare the prompt
    prompt = f"Query: {query}\n\nSearch Results:\n"
    for doc in search_results:
        prompt += f"- {doc['content'][:400]}... (Score: {doc['score']})\n"
    prompt += "\nBased on the query and search results, please provide a coherent and relevant response:"

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system",
                 "content": "You are a helpful assistant that provides coherent responses based on given search results."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"An error occurred while getting OpenAI response: {e}")
        return None


def generate_query_vector(query_text):
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.embeddings.create(input=query_text, model="text-embedding-ada-002")
    return response.data[0].embedding


def print_menu():
    print("\n--- Menu ---")
    print("1. Perform vector search")
    print("2. Perform semantic search")
    print("3. Get OpenAI response based on search results")
    print("4. Exit")
    return input("Enter your choice (1-4): ")


def main():
    client = connect_to_cosmosdb(COSMOSDB_CONNECTION_STRING)
    if not client:
        return

    collection = get_or_create_collection(client, DB_NAME, COLLECTION_NAME)
    if collection is None:
        return

    while True:
        choice = print_menu()

        if choice == '1':
            query_text = input("Enter your search query: ")
            query_vector = generate_query_vector(query_text)
            results = vector_search(collection, query_vector)
            for doc in results:
                print(f"Content: {doc['content'][:500]}..., Score: {doc['score']}")
        elif choice == '2':
            query_text = input("Enter your search query: ")
            results = semantic_search(collection, query_text)
            for doc in results:
                print(f"Content: {doc['content'][:500]}..., Score: {doc['score']}")
        elif choice == '3':
            query_text = input("Enter your search query: ")
            results = semantic_search(collection, query_text)
            for doc in results:
                print(f"Content: {doc['content'][:500]}..., Score: {doc['score']}")

            openai_response = get_openai_response(query_text, results)
            if openai_response:
                print("\nOpenAI Response:")
                print(openai_response)
        elif choice == '4':
            break
        else:
            print("Invalid choice. Please try again.")

    client.close()


if __name__ == "__main__":
    main()
