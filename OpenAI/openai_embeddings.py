from tenacity import retry, wait_random_exponential, stop_after_attempt
from logger import logger_openai
from OpenAI.openai_config import client


# Generate embeddings
@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(3))
def generate_embeddings(text: str):
    try:
        response = client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        embeddings = response.data[0].embedding
        return embeddings
    except Exception as e:
        logger_openai.error(f"Error generating embeddings: {e}")
        raise

