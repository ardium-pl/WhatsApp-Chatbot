import os
import time
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from dotenv import load_dotenv
from openai import OpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt
from flask import Flask, render_template, request, jsonify
import logging
from pprint import pformat
from datetime import datetime


# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'

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

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def connect_to_cosmosdb(connection_string):
    try:
        client = MongoClient(connection_string)
        client.admin.command("ismaster")
        logging.info("MongoDB connection established successfully.")
        return client
    except ConnectionFailure as e:
        logging.error(f"Could not connect to MongoDB due to: {e}")
        return None


def ensure_vector_search_index(collection):
    try:
        index_name = "vectorSearchIndex"
        existing_indexes = collection.list_indexes()
        if any(index["name"] == index_name for index in existing_indexes):
            logging.info(f"Vector search index {index_name} already exists")
            return

# The numLists parameter determines the number of clusters to be created. A single cluster implies that the search is
# conducted against all vectors in the database, akin to a brute-force or kNN search. This setting provides
# the highest accuracy but also the highest latency.

        collection.create_index(
            [("vector", "cosmosSearch")],
            name=index_name,
            cosmosSearchOptions={
                "kind": "vector-ivf",  # HNSW is also supported but works from M40 tier
                "numLists": 1,  # Dostosuj tę wartość w zależności od rozmiaru kolekcji
                "similarity": "COS",
                "dimensions": 1536  # Dostosuj do rzeczywistego rozmiaru wektorów
            }
        )
        logging.info(f"Index {index_name} created successfully")
    except Exception as e:
        logging.error(f"Error creating vector search index: {e}")
        raise


@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(3))
def generate_embeddings(text: str):
    try:
        response = client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        embeddings = response.data[0].embedding
        return embeddings
    except Exception as e:
        logging.error(f"Error generating embeddings: {e}")
        raise


def vector_search(collection, query, num_results=2):
    query_embedding = generate_embeddings(query)
    try:
        results = collection.aggregate([
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
    #     return list(results)
    # except Exception as e:
    #     logging.error(f"Vector search operation failed: {e}")
    #     return []

        results_list = list(results)

        # Logowanie wyników
        logging.info(f"Vector search results for query: '{query}'")
        for i, result in enumerate(results_list, 1):
            logging.info(f"Result {i}:")
            logging.info(f"Similarity Score: {result.get('similarityScore', 'N/A')}")
            logging.info(f"Document ID: {result.get('_id', 'N/A')}")
            logging.info(f"Title: {result.get('title', 'N/A')}")
            logging.info(f"Page Number: {result.get('pageNumber', 'N/A')}")
            logging.info(f"Content: {result.get('content', 'N/A')[:100]}...")  # Pokazujemy tylko pierwsze 100 znaków

            # Formatowanie daty createdAt, jeśli istnieje
            created_at = result.get('createdAt')
            if created_at:
                if isinstance(created_at, datetime):
                    created_at_str = created_at.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    created_at_str = str(created_at)
            else:
                created_at_str = 'N/A'
            logging.info(f"Created At: {created_at_str}")

            logging.info(f"Word Count: {result.get('wordCount', 'N/A')}")
            logging.info("Full result structure:")
            logging.info(pformat(result))
            logging.info("-" * 50)

        return results_list
    except Exception as e:
        logging.error(f"Vector search operation failed: {e}")
        return []

def print_page_search_result(result):
    logging.info(f"Similarity Score: {result['similarityScore']}")
    page_number = result['document']['page_number']
    logging.info(f"Page: {page_number}")
    logging.info(f"Content: {result['document']['content']}")
    logging.info(f"_id: {result['document']['_id']}\n")


# Creative prompt for the RAG-like model
system_prompt = """
You are a helpful assistant designed to provide information about the Euvic Services presentations / pdf files
.
Try to answer questions based on the information provided in the presentation content below.
If you are asked a question that isn't covered in the presentation, respond based on the given information and your best judgment.

Presentation content:
"""


def rag_with_vector_search(collection, question, num_results=2):
    results = vector_search(collection, question, num_results=num_results)
    context = ""
    for result in results:
        context += f"Title: {result.get('title', 'N/A')}\n"
        context += f"Page: {result.get('pageNumber', 'N/A')}\n"
        context += f"Content: {result.get('content', 'N/A')}\n"
        context += f"Created At: {result.get('createdAt', 'N/A')}\n"
        context += f"Word Count: {result.get('wordCount', 'N/A')}\n\n"
    messages = [
        {"role": "system", "content": system_prompt + context},
        {"role": "user", "content": question}
    ]

    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
        return completion.choices[0].message.content
    except Exception as e:
        logging.error(f"Error with OpenAI ChatCompletion: {e}")
        return "An error occurred while generating the response."


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        logging.info("POST request received")
        question = request.form['question']
        num_results = int(request.form['num_results'])
        logging.info(f"Received question: {question} with num_results: {num_results}")

        start_time = time.time()
        logging.info("=" * 50)
        logging.info(f"Processing query: {question}")

        client_org = connect_to_cosmosdb(CONNECTION_STRING)
        if client_org is not None:
            db = client_org[DB_NAME]
            collection = db[COLLECTION_NAME]
            ensure_vector_search_index(collection)  # Ensure the index exists
            try:
                results = vector_search(collection, question, num_results)
                for result in results:
                    logging.info(f"Similarity Score: {result['similarityScore']}")
                    logging.info(f"Content: {result['content']}")
                response = rag_with_vector_search(collection, question, num_results)
            except Exception as e:
                logging.error(f"Error processing query: {e}")
                response = "An error occurred during processing."
            finally:
                client_org.close()
        else:
            response = "Failed to connect to MongoDB."

        end_time = time.time()
        logging.info(f"Query processed in {end_time - start_time:.2f} seconds")
        logging.info("=" * 50)
        return jsonify({'response': response}), 200
    logging.info("GET request received")
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True, port=8080)
