import json
import os
from pymongo import MongoClient, UpdateOne
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv
from openai import AzureOpenAI

# Load environment variables
load_dotenv()

# MongoDB connection details
CONNECTION_STRING = os.environ.get("COSMOSDB_CONNECTION_STRING")
DB_NAME = os.environ.get("DB_NAME")
COLLECTION_NAME = os.environ.get("COSMOS_COLLECTION_NAME")

# Azure OpenAI API details
AOAI_ENDPOINT = os.environ.get("AOAI_ENDPOINT")
AOAI_KEY = os.environ.get("AOAI_KEY")
COMPLETIONS_DEPLOYMENT_NAME = "completions"
AOAI_API_VERSION = "2023-05-15"


def connect_to_cosmosdb(connection_string):
    try:
        client = MongoClient(connection_string)
        client.admin.command("ismaster")
        print("MongoDB connection established successfully.")
        return client
    except ConnectionFailure as e:
        print(f"Could not connect to MongoDB due to: {e}")
        return None


def create_vector_index(collection_name: str):
    db.command({
        'createIndexes': collection_name,
        'indexes': [
            {
                'name': 'VectorSearchIndex',
                'key': {
                    "contentVector": "cosmosSearch"
                },
                'cosmosSearchOptions': {
                    'kind': 'vector-ivf',
                    'numLists': 1,
                    'similarity': 'COS',
                    'dimensions': 1536
                }
            }
        ]
    })


def vector_search(collection_name, query_embedding, num_results=3):
    collection = db[collection_name]
    pipeline = [
        {
            '$search': {
                "cosmosSearch": {
                    "vector": query_embedding,
                    "path": "contentVector",
                    "k": num_results
                },
                "returnStoredSource": True}},
        {'$project': {'similarityScore': {'$meta': 'searchScore'}, 'document': '$$ROOT'}}
    ]
    results = collection.aggregate(pipeline)
    return results


def print_page_search_result(result):
    print(f"Similarity Score: {result['similarityScore']}")
    page_number = result['document']['page_number']
    print(f"Page: {page_number}")
    print(f"Content: {result['document']['content']}")
    print(f"_id: {result['document']['_id']}\n")


if __name__ == "__main__":
    # Debugging output for environment variables
    print("COSMOS_CONNECTION_STRING:", CONNECTION_STRING)
    print("COSMOS_DB_NAME:", DB_NAME)
    print("COSMOS_COLLECTION_NAME:", COLLECTION_NAME)

    # Connect to MongoDB
    client_org = connect_to_cosmosdb(CONNECTION_STRING)

    if client_org is not None:
        db = client_org[DB_NAME]
        collection = db[COLLECTION_NAME]

        # Load presentation data with pre-computed embeddings from the local JSON file
        file_path = r'C:\Users\szyme\PycharmProjects\Azure-db-test2\json_embeddings_azure\output_with_embeddings.json'
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)

        # Process and insert pages with embeddings
        bulk_operations = []
        for page, vector in zip(raw_data["pages"], raw_data["vectors"]):
            for page_number, content in page.items():
                document = {
                    "_id": page_number,
                    "page_number": page_number,
                    "content": content,
                    "contentVector": vector
                }
                bulk_operations.append(
                    UpdateOne(
                        {"_id": page_number},
                        {"$set": document},
                        upsert=True
                    )
                )

        if bulk_operations:
            result = collection.bulk_write(bulk_operations)
            print(
                f"Inserted: {result.upserted_count}, Matched: {result.matched_count}, Modified: {result.modified_count}")
        else:
            print("No valid pages to insert or update.")

        # Create vector indexes for collections
        create_vector_index("presentation")

        # Example queries (using pre-computed embeddings)
        query_embeddings = {
            "What is Euvic Services?": raw_data["vectors"][0],  # Using the first vector as an example
            "What are the key values of collaboration with Euvic?": raw_data["vectors"][-1]
            # Using the last vector as an example
        }

        for query, embedding in query_embeddings.items():
            print(f"Query: {query}")
            results = vector_search("presentation", embedding, num_results=3)
            for result in results:
                print_page_search_result(result)

        # Closing the MongoDB connection
        client_org.close()
    else:
        print("Failed to connect to MongoDB. Exiting...")
