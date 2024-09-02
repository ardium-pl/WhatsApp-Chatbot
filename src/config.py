import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB / Cosmos DB Configuration
COSMOSDB_CONNECTION_STRING = os.getenv("COSMOSDB_CONNECTION_STRING")
DB_NAME = os.getenv("DB_NAME")
COSMOS_COLLECTION_NAME = os.getenv("COSMOS_COLLECTION_NAME")

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPEN_AI_KEY")

# WhatsApp API Configuration
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
META_ENDPOINT = os.getenv("META_ENDPOINT")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
WEBHOOK_VERIFY_TOKEN = os.getenv("WEBHOOK_VERIFY_TOKEN")

# Flask Configuration
SECRET_KEY = os.getenv("SECRET_KEY")

# Server Configuration
PORT = int(os.getenv("PORT", 8080))