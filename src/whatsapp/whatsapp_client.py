import requests
from src.logger import whatsapp_logger
import aiohttp
from src.config import META_ENDPOINT, PHONE_NUMBER_ID, ACCESS_TOKEN


class WhatsAppClient:
    @staticmethod
    async def send_message(ai_response, sender_phone_number):
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
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    whatsapp_logger.info('✅ AI answer sent successfully!')
                else:
                    whatsapp_logger.error(f'❌ Failed to send message: {response.status} {response.reason}.')
