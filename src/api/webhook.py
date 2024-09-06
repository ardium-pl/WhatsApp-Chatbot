from flask import Blueprint, request
from src.config import WEBHOOK_VERIFY_TOKEN
from src.ai.rag_engine import RAGEngine
from src.whatsapp.whatsapp_client import WhatsAppClient
from src.database.mysql_queries import insert_data_mysql
from src.logger import main_logger, whatsapp_logger, mysql_logger

webhook_bp = Blueprint('webhook', __name__)
rag_engine = RAGEngine()


@webhook_bp.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        main_request_body = data['entry'][0]['changes'][0]['value']

        errors = main_request_body.get('errors')
        statuses = main_request_body.get('statuses')
        messages = main_request_body.get('messages')

        if errors:
            print(f"⚙️ Request contained an errors field:"
                  f"\tErrors: {errors}")
        if statuses:
            print(f'⚙️ Message status: {statuses[0].get("status")}')
        if messages:
            incoming_message = messages[0]
            sender_phone_number = incoming_message.get("from")

            # Check if the incoming message contains text
            if incoming_message.get('type') == 'text':
                user_query = incoming_message['text'].get('body')

                print(f'✅ Received a POST request containing a text message:\n'
                      f'\t📩 Message text: {user_query}\n'
                      f'\t📞 Sender phone number: {sender_phone_number}')

                # Respond with AI answer
                ai_answer = rag_engine.process_query(user_query)
                WhatsAppClient.send_message(ai_answer, sender_phone_number)
                whatsapp_logger.info('AI answer sent successfully')

                # Insert the query-answer pair into MySQL database
                insert_data_mysql(sender_phone_number, user_query, ai_answer)

            else:
                print(f"⚙️ Received POST request doesn't contain text.\n"
                      f'\t📩 Message type: {incoming_message.get("type")}.')

    except Exception as e:
        print(f"❌ Error processing a user POST request.\n"
              f"\tError message: {e}")
    finally:
        return '✅', 200


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
        main_logger.error(f'Error processing the verification request: {e}')
        return 'Error processing the verification request', 400
