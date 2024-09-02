from flask import Blueprint, request, jsonify
import logging
from config import WEBHOOK_VERIFY_TOKEN
from ai.rag_engine import RAGEngine
from whatsapp.whatsapp_client import WhatsAppClient

webhook_bp = Blueprint('webhook', __name__)
rag_engine = RAGEngine()


@webhook_bp.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        incoming_message = data['entry'][0]['changes'][0]['value']['messages'][0]
        sender_phone_number = incoming_message['from']

        if incoming_message['type'] == 'text':
            user_query = incoming_message['text']['body']
            logging.info(f'Received message: {user_query}')

            ai_answer = rag_engine.process_query(user_query)
            WhatsAppClient.send_message(ai_answer, sender_phone_number)
        else:
            logging.info(f'Received a non-text message of type: {incoming_message["type"]}.')

        return '✅ POST request processed successfully.', 200
    except Exception as e:
        logging.error(f'❌ An error occurred during processing the request: {e}')
        return '❌ An error occurred during processing the request.', 400


@webhook_bp.route('/webhook', methods=['GET'])
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
