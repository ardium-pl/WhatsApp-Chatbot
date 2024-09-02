from logger import logger_openai
from OpenAI.openai_config import client

# System prompt for RAG
system_prompt = """
You are a helpful assistant designed to provide information about the Euvic Services presentations / pdf files.
Try to answer questions based on the information provided in the presentation content below.
If you are asked a question that isn't covered in the presentation, respond based on the given information and your best judgment.

Presentation content:
"""


# Funkcja na chat completion od OpenAI
