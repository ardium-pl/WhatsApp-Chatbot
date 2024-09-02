from logger import logger_openai
from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()


# OpenAI API key
OPENAI_API_KEY = os.getenv("OPEN_AI_KEY")
if not OPENAI_API_KEY:
    raise ValueError("No OpenAI API key found. Please set the OPEN_AI_KEY environment variable.")

# Initialize the OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)
