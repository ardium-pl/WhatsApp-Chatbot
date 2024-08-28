import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv
from openai import OpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt

# Load environment variables
load_dotenv()

# MongoDB connection details
CONNECTION_STRING = os.environ.get("COSMOSDB_CONNECTION_STRING")
DB_NAME = os.environ.get("DB_NAME")
COLLECTION_NAME = os.environ.get("COSMOS_COLLECTION_NAME")

# Get the API key from the environment variable
OPENAI_API_KEY = os.getenv("OPEN_AI_KEY")
if not OPENAI_API_KEY:
    raise ValueError("No OpenAI API key found. Please set the OPEN_AI_KEY environment variable.")

# Initialize the OpenAI client with the API key
client = OpenAI(api_key=OPENAI_API_KEY)


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
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    embeddings = response.data[0].embedding
    return embeddings


def vector_search(collection, query, num_results=2):
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


# Strict prompt for the RAG-like model
# system_prompt = """
# You are a helpful assistant designed to provide information about the Euvic Services presentation.
# Only answer questions related to the information provided in the presentation content below.
# If you are asked a question that is not in the presentation, respond with "I don't have that information in the presentation."
#
# Presentation content:
# """

# Creative prompt for the RAG-like model
system_prompt = """
You are a helpful assistant designed to provide information about the Euvic Services presentation.
Try to answer questions based on the information provided in the presentation content below.
If you are asked a question that isn't covered in the presentation, respond based on the given information and your best judgment.

Presentation content:
"""


def rag_with_vector_search(collection, question: str, num_results: int = 2):
    results = vector_search(collection, question, num_results=num_results)
    presentation_content = ""
    for result in results:
        if "contentVector" in result["document"]:
            del result["document"]["contentVector"]
        page_number = result["document"]["page_number"]
        presentation_content += f"Page {page_number}: {result['document']['content']}\n\n"

    formatted_prompt = system_prompt + presentation_content

    messages = [
        {"role": "system", "content": formatted_prompt},
        {"role": "user", "content": question}
    ]

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )
    return completion.choices[0].message.content


if __name__ == "__main__":
    client_org = connect_to_cosmosdb(CONNECTION_STRING)

    if client_org is not None:
        db = client_org[DB_NAME]
        collection = db[COLLECTION_NAME]

        # Example queries
        queries = [
            "What is Euvic Services?",
            "What are the key values of collaboration with Euvic?",
            "Based on the ROI 1Y 2Y and 3Y create a prediction for the ROI 4Y"
        ]

        for query in queries:
            print(f"Query: {query}")
            results = vector_search(collection, query, num_results=2)
            print("Vector Search Results:")
            for result in results:
                print_page_search_result(result)

            print("RAG Response:")
            rag_response = rag_with_vector_search(collection, query)
            print(rag_response)
            print("\n" + "=" * 50 + "\n")

        # Closing the MongoDB connection
        client_org.close()
    else:
        print("Failed to connect to MongoDB. Exiting...")
