from flask import Blueprint, request, g
from src.logger import whatsapp_logger, main_logger
from src.config import WEBHOOK_VERIFY_TOKEN
from src.ai import RAGEngine
from src.whatsapp.whatsapp_client import WhatsAppClient
from src.database.mysql_queries import insert_data_mysql, get_recent_queries
import traceback
import asyncio

webhook_bp = Blueprint('webhook', __name__)
rag_engine = RAGEngine()


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
                    whatsapp_logger.info(f'✅ Received message: {user_query} from {sender_phone_number}')

                    whatsapp_logger.info(f'✅ Received a POST request containing a text message:\n'
                                         f'\t📩 Message text: {user_query}\n'
                                         f'\t📞 Sender phone number: {sender_phone_number}')

                    # Pobierz historię zapytań
                    chat_history = await get_recent_queries(sender_phone_number)
                    whatsapp_logger.info(f'Retrieved chat history with {len(chat_history)} entries')

                    # Przetwórz zapytanie z uwzględnieniem historii
                    ai_answer = rag_engine.process_query(user_query, chat_history=chat_history)
                    whatsapp_logger.info('RAGEngine processed query with chat history')

                    # Use asyncio to run these potentially blocking operations concurrently
                    await asyncio.gather(
                        WhatsAppClient.send_message(ai_answer, sender_phone_number),
                        insert_data_mysql(sender_phone_number, user_query, ai_answer)
                    )

                    whatsapp_logger.info('AI answer sent and data inserted into MySQL')

                    # Add the processed request to the worker's queue for any additional background tasks
                    await g.worker.request_queue.enqueue({
                        'sender_phone_number': sender_phone_number,
                        'query': user_query,
                        'answer': ai_answer
                    })

                else:
                    whatsapp_logger.warn(f"Received non-text message type: {incoming_message.get('type')}")
        except Exception as e:
            whatsapp_logger.critical(f"Error in webhook processing: {e}")
            whatsapp_logger.error(traceback.format_exc())
        finally:
            return '✅', 200

    except Exception as e:
        whatsapp_logger.error(f'Error processing HTTP request: {e}')
        whatsapp_logger.error(traceback.format_exc())
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
