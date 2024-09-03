from flask import Flask, request
import requests
import os
from pprint import pprint

# Load environment variables
WEBHOOK_VERIFY_TOKEN = os.environ.get('WEBHOOK_VERIFY_TOKEN')
PHONE_NUMBER_ID = os.environ.get('PHONE_NUMBER_ID')
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
META_ENDPOINT = os.environ.get('META_ENDPOINT')
PORT = os.environ.get('PORT', 5000)

app = Flask(__name__)
chat_history = []


def send_ai_response(ai_response, sender_phone_number):
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

    # Make http request
    response = requests.post(url, json=payload, headers=headers)

    # Check if the request was successful
    if response.ok:
        print('✅ AI answer sent successfully!')
    else:
        print(f'❌ Failed to process the request: {response.status_code} {response.reason}.')


@app.post('/webhook')
def get_ai_response():
    try:
        data = request.get_json()

        try:
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

                    # Get AI answer
                    ai_answer = 'tbc'

                    # Send POST request with AI answer
                    send_ai_response(ai_answer, sender_phone_number)
                else:
                    print(f"⚙️ Received POST request doesn't contain text.\n"
                          f'\t📩 Message type: {incoming_message.get("type")}.')

        except Exception as e:
            print(f"❌ Error accessing a main request body.\n"
                  f"\tError message: {e}")
        finally:
            return '✅', 200

    except Exception as e:
        print(f'❌ An error occurred during processing the request.\n'
              f'\tError messages {e}.')
        return '❌', 400


@app.get('/webhook')
def verify_webhook():
    try:
        mode = request.args.get('hub.mode')
        verify_token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if mode == 'subscribe' and verify_token == WEBHOOK_VERIFY_TOKEN:
            print('✅ Webhook verified successfully!')
            return challenge, 200
        else:
            print('❌ Webhook verification failed :( Webhook verification tokens do not match.')
            return 'Webhook verification tokens do not match.', 400

    except Exception as e:
        print(f'❌ Error processing the verification request. Error: {e} ❌')
        return 'Error processing the verification request', 400


if __name__ == '__main__':
    app.run(port=PORT, debug=False)
