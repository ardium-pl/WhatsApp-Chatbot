from OpenAI.openai_embeddings import generate_embeddings
from Database.MySQL.mysql_queries import insert_data_mysql
from Database.CosmosDB.cosmos_db_config import connect_to_cosmosdb
from vector_search import ensure_vector_search_index, vector_search, rag_with_vector_search
from logger import logger_main
import os
from dotenv import load_dotenv
from flask import Flask, request
import requests

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'


# WhatsApp API details
WEBHOOK_VERIFY_TOKEN = os.environ.get('WEBHOOK_VERIFY_TOKEN')
PHONE_NUMBER_ID = os.environ.get('PHONE_NUMBER_ID')
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
META_ENDPOINT = os.environ.get('META_ENDPOINT')
PORT = int(os.environ.get('PORT', 8080))

# MongoDB connection details
CONNECTION_STRING = os.environ.get("COSMOSDB_CONNECTION_STRING")
DB_NAME = os.environ.get("DB_NAME")
COLLECTION_NAME = os.environ.get("COSMOS_COLLECTION_NAME")



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
        logger_main.info('✅ AI answer sent successfully!')
    else:
        logger_main.error(f'❌ Failed to send message: {response.status_code} {response.reason}.')


# Webhook route for incoming messages
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        try:
            incoming_message = data['entry'][0]['changes'][0]['value']['messages'][0]
        except Exception as e:
            logger_main.error(f'❌ Error accessing user message: {e}')
            return '❌ Error accessing user message.', 400

        sender_phone_number = incoming_message['from']
        if incoming_message['type'] == 'text':
            user_query = incoming_message['text']['body']
            logger_main.info(f'Received message: {user_query}')

            # Process the query using RAG
            client_org = connect_to_cosmosdb(CONNECTION_STRING)
            if client_org is not None:
                db = client_org[DB_NAME]
                collection = db[COLLECTION_NAME]
                ensure_vector_search_index(collection)
                try:
                    ai_answer = rag_with_vector_search(collection, user_query)
                except Exception as e:
                    logger_main.error(f"Error processing query: {e}")
                    ai_answer = "An error occurred during processing."
                finally:
                    client_org.close()
            else:
                ai_answer = "Failed to connect to the database."

            # Send the AI response back to WhatsApp
            send_whatsapp_message(ai_answer, sender_phone_number)

            # Insert a query - answer pair at the end of the chain
            insert_data_mysql("TBC", user_query, ai_answer)

        else:
            logger_main.info(f'Received a non-text message of type: {incoming_message["type"]}.')
        return '✅ POST request processed successfully.', 200
    except Exception as e:
        logger_main.error(f'❌ An error occurred during processing the request: {e}')
        return '❌ An error occurred during processing the request.', 400


# Webhook verification route
@app.route('/webhook', methods=['GET'])
def verify_webhook():
    try:
        mode = request.args.get('hub.mode')
        verify_token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        if mode == 'subscribe' and verify_token == WEBHOOK_VERIFY_TOKEN:
            logger_main.info('✅ Webhook verified successfully!')
            return challenge, 200
        else:
            logger_main.warning('❌ Webhook verification failed. Tokens do not match.')
            return 'Webhook verification tokens do not match.', 400
    except Exception as e:
        logger_main.error(f'❌ Error processing the verification request: {e}')
        return 'Error processing the verification request', 400


if __name__ == '__main__':
    app.run(port=PORT, debug=False)
