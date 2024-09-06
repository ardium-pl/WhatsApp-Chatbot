from flask import Blueprint, request, current_app
from src.config import WEBHOOK_VERIFY_TOKEN
from src.logger import main_logger
import traceback
from flask import current_app
from main import worker
webhook_bp = Blueprint('webhook', __name__)


@webhook_bp.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()

        main_request_body = data['entry'][0]['changes'][0]['value']

        errors = main_request_body.get('errors')
        statuses = main_request_body.get('statuses')
        messages = main_request_body.get('messages')

        if errors:
            main_logger.warning(f"Request contained an errors field: {errors}")
        if statuses:
            main_logger.info(f'Message status: {statuses[0].get("status")}')
        if messages:
            incoming_message = messages[0]
            sender_phone_number = incoming_message.get("from")

            if incoming_message.get('type') == 'text':
                user_query = incoming_message['text'].get('body')

                main_logger.info(f'Received a POST request containing a text message:\n'
                                 f'Message text: {user_query}\n'
                                 f'Sender phone number: {sender_phone_number}')

                # Enqueue the task for processing by the Worker
                worker.request_queue.enqueue({
                    'sender_phone_number': sender_phone_number,
                    'query': user_query
                })
                main_logger.info(f"Task enqueued for processing: {user_query}")

            else:
                main_logger.info(f"Received POST request doesn't contain text.\n"
                                 f'Message type: {incoming_message.get("type")}.')

        return '✅', 200

    except Exception as e:
        error_msg = f'An error occurred during processing the request: {str(e)}\n'
        error_msg += traceback.format_exc()
        main_logger.error(error_msg)
        return '❌', 400


@webhook_bp.route('/webhook', methods=['GET'])
def verify_webhook():
    try:
        mode = request.args.get('hub.mode')
        verify_token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        if mode == 'subscribe' and verify_token == WEBHOOK_VERIFY_TOKEN:
            main_logger.info('Webhook verified successfully!')
            return challenge, 200
        else:
            main_logger.warning('Webhook verification failed. Tokens do not match.')
            return 'Webhook verification tokens do not match.', 400
    except Exception as e:
        error_msg = f'Error processing the verification request: {str(e)}\n'
        error_msg += traceback.format_exc()
        main_logger.error(error_msg)
        return 'Error processing the verification request', 400
