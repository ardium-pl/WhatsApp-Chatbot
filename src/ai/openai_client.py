from openai import OpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt
import logging
from config import OPENAI_API_KEY


class OpenAIClient:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    @retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(3))
    def generate_embeddings(self, text: str):
        try:
            response = self.client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logging.error(f"Error generating embeddings: {e}")
            raise

    def generate_chat_completion(self, messages):
        try:
            completion = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages
            )
            return completion.choices[0].message.content
        except Exception as e:
            logging.error(f"Error with OpenAI ChatCompletion: {e}")
            return "An error occurred while generating the response."
