from src.database.mongodb_client import MongoDBClient
from src.ai.openai_client import OpenAIClient
from datetime import datetime


def prepare_context(results):
    context = ""
    for result in results:
        context += f"Title: {result.get('title', 'N/A')}\n"
        context += f"Page: {result.get('pageNumber', 'N/A')}\n"
        context += f"Content: {result.get('content', 'N/A')}\n"
        created_at = result.get('createdAt')
        if created_at:
            if isinstance(created_at, datetime):
                created_at_str = created_at.strftime("%Y-%m-%d %H:%M:%S")
            else:
                created_at_str = str(created_at)
        else:
            created_at_str = 'N/A'
        context += f"Created At: {created_at_str}\n"
        context += f"Word Count: {result.get('wordCount', 'N/A')}\n\n"
    return context


def prepare_messages(context, question):
    system_prompt = """
    You are a helpful assistant designed to provide information about the Euvic Services presentations / pdf files.
    Try to answer questions based on the information provided in the presentation content below.
    If you are asked a question that isn't covered in the presentation, respond based on the given information and your best judgment.

    Presentation content:
    """
    return [
        {"role": "system", "content": system_prompt + context},
        {"role": "user", "content": question}
    ]


class RAGEngine:
    def __init__(self):
        self.mongodb_client = MongoDBClient()
        self.openai_client = OpenAIClient()

    def process_query(self, question, num_results=10):
        self.mongodb_client.connect()
        try:
            self.mongodb_client.ensure_vector_search_index()
            query_embedding = self.openai_client.generate_embeddings(question)
            results = self.mongodb_client.vector_search(query_embedding, num_results)
            context = prepare_context(results)
            messages = prepare_messages(context, question)
            return self.openai_client.generate_chat_completion(messages)
        finally:
            self.mongodb_client.close()
