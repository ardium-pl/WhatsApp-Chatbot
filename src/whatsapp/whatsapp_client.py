import requests
import logging
from src.config import META_ENDPOINT, PHONE_NUMBER_ID, ACCESS_TOKEN


class WhatsAppClient:
    @staticmethod
    def send_message(ai_response, sender_phone_number):
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
