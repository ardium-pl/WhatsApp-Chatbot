import os
import time
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from dotenv import load_dotenv
from openai import OpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt
from flask import Flask, request, jsonify
import logging
from pprint import pformat
from datetime import datetime
import requests

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'

# MongoDB connection details
CONNECTION_STRING = os.environ.get("COSMOSDB_CONNECTION_STRING")
DB_NAME = os.environ.get("DB_NAME")
COLLECTION_NAME = os.environ.get("COSMOS_COLLECTION_NAME")

# OpenAI API key
OPENAI_API_KEY = os.getenv("OPEN_AI_KEY")
if not OPENAI_API_KEY:
    raise ValueError("No OpenAI API key found. Please set the OPEN_AI_KEY environment variable.")

# Initialize the OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# WhatsApp API details
WEBHOOK_VERIFY_TOKEN = os.environ.get('WEBHOOK_VERIFY_TOKEN')
PHONE_NUMBER_ID = os.environ.get('PHONE_NUMBER_ID')
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
META_ENDPOINT = os.environ.get('META_ENDPOINT')
PORT = int(os.environ.get('PORT', 8080))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# MongoDB connection function
def connect_to_cosmosdb(connection_string):
    try:
        client = MongoClient(connection_string)
        client.admin.command("ismaster")
        logging.info("MongoDB connection established successfully.")
        return client
    except ConnectionFailure as e:
        logging.error(f"Could not connect to MongoDB due to: {e}")
        # return None
        raise ConnectionError("Failed to connect to MongoDB.") from e


# Ensure vector search index
def ensure_vector_search_index(collection):
    try:
        index_name = "vectorSearchIndex"
        existing_indexes = collection.list_indexes()
        if any(index["name"] == index_name for index in existing_indexes):
            logging.info(f"Vector search index {index_name} already exists")
            return

        collection.create_index(
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


# Generate embeddings
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


# Vector search function
def vector_search(collection, query, num_results=4):
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

        results_list = list(results)
        logging.info(f"Vector search results for query: '{query}'")
        for i, result in enumerate(results_list, 1):
            logging.info(f"Result {i}:")
            logging.info(f"Similarity Score: {result.get('similarityScore', 'N/A')}")
            logging.info(f"Document ID: {result.get('_id', 'N/A')}")
            logging.info(f"Title: {result.get('title', 'N/A')}")
            logging.info(f"Page Number: {result.get('pageNumber', 'N/A')}")
            logging.info(f"Content: {result.get('content', 'N/A')[:100]}...")

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


# System prompt for RAG
system_prompt = """
You are a helpful assistant designed to provide information about the Euvic Services presentations / pdf files.
Try to answer questions based on the information provided in the presentation content below.
If you are asked a question that isn't covered in the presentation, respond based on the given information and your best judgment.

Presentation content:
"""


# RAG function
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


# Send WhatsApp message function
def send_whatsapp_message(ai_response, sender_phone_number):
    url = f'{META_ENDPOINT}{PHONE_NUMBER_ID}/messages'
    payload = {
        'messaging_product': 'whatsapp',
        'recipient_type': 'individual',
        'to': sender_phone_number,
        'type': 'text',
        'text': {
            'preview_url': False,
            'body': ai_response,
        },
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {ACCESS_TOKEN}'
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.ok:
        logging.info('✅ AI answer sent successfully!')
    else:
        logging.error(f'❌ Failed to send message: {response.status_code} {response.reason}.')


# Webhook route for incoming messages
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        try:
            incoming_message = data['entry'][0]['changes'][0]['value']['messages'][0]
        except Exception as e:
            logging.error(f'❌ Error accessing user message: {e}')
            return '❌ Error accessing user message.', 400

        sender_phone_number = incoming_message['from']
        if incoming_message['type'] == 'text':
            user_query = incoming_message['text']['body']
            logging.info(f'Received message: {user_query}')

            # Process the query using RAG
            client_org = connect_to_cosmosdb(CONNECTION_STRING)
            if client_org is not None:
                db = client_org[DB_NAME]
                collection = db[COLLECTION_NAME]
                ensure_vector_search_index(collection)
                try:
                    ai_answer = rag_with_vector_search(collection, user_query)
                except Exception as e:
                    logging.error(f"Error processing query: {e}")
                    ai_answer = "An error occurred during processing."
                finally:
                    client_org.close()
            else:
                ai_answer = "Failed to connect to the database."

            # Send the AI response back to WhatsApp
            send_whatsapp_message(ai_answer, sender_phone_number)
        else:
            logging.info(f'Received a non-text message of type: {incoming_message["type"]}.')
        return '✅ POST request processed successfully.', 200
    except Exception as e:
        logging.error(f'❌ An error occurred during processing the request: {e}')
        return '❌ An error occurred during processing the request.', 400


# Webhook verification route
@app.route('/webhook', methods=['GET'])
def verify_webhook():
    try:
        mode = request.args.get('hub.mode')
        verify_token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        if mode == 'subscribe' and verify_token == WEBHOOK_VERIFY_TOKEN:
            logging.info('✅ Webhook verified successfully!')
            return challenge, 200
        else:
            logging.warning('❌ Webhook verification failed. Tokens do not match.')
            return 'Webhook verification tokens do not match.', 400
    except Exception as e:
        logging.error(f'❌ Error processing the verification request: {e}')
        return 'Error processing the verification request', 400


if __name__ == '__main__':
    app.run(port=PORT, debug=False)
