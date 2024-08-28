import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv
from openai import AzureOpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt

# Load environment variables
load_dotenv()

# MongoDB connection details
CONNECTION_STRING = os.environ.get("COSMOSDB_CONNECTION_STRING")
DB_NAME = os.environ.get("DB_NAME")
COLLECTION_NAME = os.environ.get("COSMOS_COLLECTION_NAME")

# Azure OpenAI API details
AOAI_ENDPOINT = os.environ.get("AOAI_ENDPOINT")
AOAI_KEY = os.environ.get("AOAI_KEY")
EMBEDDINGS_DEPLOYMENT_NAME = "embeddings"
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


@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(3))
def generate_embeddings(text: str):
    response = ai_client.embeddings.create(input=text, model=EMBEDDINGS_DEPLOYMENT_NAME)
    embeddings = response.data[0].embedding
    return embeddings


def vector_search(collection, query, num_results=3):
    query_embedding = generate_embeddings(query)
    pipeline = [
        {
            '$search': {
                "cosmosSearch": {
                    "vector": query_embedding,
                    "path": "contentVector",
                    "k": num_results
                },
                "returnStoredSource": True
            }
        },
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
    client_org = connect_to_cosmosdb(CONNECTION_STRING)

    if client_org is not None:
        db = client_org[DB_NAME]
        collection = db[COLLECTION_NAME]

        # Establish Azure OpenAI connectivity
        ai_client = AzureOpenAI(
            azure_endpoint=AOAI_ENDPOINT,
            api_version=AOAI_API_VERSION,
            api_key=AOAI_KEY
        )

        # Example queries
        queries = [
            "What is Euvic Services?",
            "What are the key values of collaboration with Euvic?",
            "Describe the benefits of WEBCON BPS"
        ]

        for query in queries:
            print(f"Query: {query}")
            results = vector_search(collection, query, num_results=3)
            for result in results:
                print_page_search_result(result)

        # Closing the MongoDB connection
        client_org.close()
    else:
        print("Failed to connect to MongoDB. Exiting...")
