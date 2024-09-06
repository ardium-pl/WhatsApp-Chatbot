from flask import Blueprint, request, current_app, g
from src.logger import whatsapp_logger, main_logger
from src.config import WEBHOOK_VERIFY_TOKEN
import traceback

webhook_bp = Blueprint('webhook', __name__)


@webhook_bp.route('/webhook', methods=['POST'])
async def webhook():
    try:
        data = request.get_json()

        try:
            main_request_body = data['entry'][0]['changes'][0]['value']

            errors = main_request_body.get('errors')
            statuses = main_request_body.get('statuses')
            messages = main_request_body.get('messages')

            if errors:
                whatsapp_logger.warn(f"⚙️ Request contained an errors field:"
                                     f"\tErrors: {errors}")
            if statuses:
                whatsapp_logger.info(f'⚙️ Message status: {statuses[0].get("status")}')
            if messages:
                incoming_message = messages[0]
                sender_phone_number = incoming_message.get("from")

                # Check if the incoming message contains text
                if incoming_message.get('type') == 'text':
                    user_query = incoming_message['text'].get('body')

                    whatsapp_logger.info(f'✅ Received a POST request containing a text message:\n'
                                         f'\t📩 Message text: {user_query}\n'
                                         f'\t📞 Sender phone number: {sender_phone_number}')

                    # Add the request to the worker's queue
                    g.worker.request_queue.enqueue({
                        'sender_phone_number': sender_phone_number,
                        'query': user_query
                    })

                else:
                    whatsapp_logger.warn(f"⚙️ Received POST request doesn't contain text.\n"
                                         f'\t📩 Message type: {incoming_message.get("type")}.')

        except Exception as e:
            whatsapp_logger.critical(f"❌ An error occurred during main app process inside of /webhook.\n"
                                     f"\tError message: {e}")
        finally:
            return '✅', 200

    except Exception as e:
        print(f'❌ Error processing a HTTP request.\n'
              f'\tError messages {e}.')
        return '❌', 400


@webhook_bp.route('/webhook', methods=['GET'])
async def verify_webhook():
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
