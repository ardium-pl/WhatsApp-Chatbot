from src.database.mongodb_client import MongoDBClient
from src.ai.openai_client import OpenAIClient
from datetime import datetime
from src.logger import main_logger, cosmosdb_logger, openai_logger


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
    main_logger.debug(f"Context prepared with {len(results)} results")
    return context


def prepare_messages(context, question, chat_history=None):
    system_prompt = """You are a helpful assistant designed to provide information about the Euvic Services 
    presentations / pdf files. Try to answer questions based on the information provided in the presentation content 
    below. If you are asked a question that isn't covered in the presentation, respond based on the given information 
    and your best judgment.

    You also have access to the recent chat history. Use this history to maintain context and provide more relevant 
    answers. If the current question is related to previous questions, refer to the chat history for continuity.

    Presentation content:
    """
    messages = [
        {"role": "system", "content": system_prompt + context},
    ]

    if chat_history:
        messages.append({"role": "system", "content": "Recent chat history:"})
        for entry in chat_history:
            messages.append({"role": "user", "content": entry["query"]})
            messages.append({"role": "assistant", "content": entry["answer"]})
        messages.append({"role": "system", "content": "End of chat history. Now answer the following question:"})

    messages.append({"role": "user", "content": question})

    main_logger.debug(f"Messages prepared for chat completion. Total messages: {len(messages)}")
    return messages


class RAGEngine:
    def __init__(self):
        self.mongodb_client = MongoDBClient()
        self.openai_client = OpenAIClient()
        main_logger.info("RAGEngine initialized")

    def process_query(self, question, num_results=10, chat_history=None):
        main_logger.info(f"Processing query: {question}")
        if chat_history:
            main_logger.info(f"Chat history provided with {len(chat_history)} entries")
        else:
            main_logger.info("No chat history provided")

        self.mongodb_client.connect()
        try:
            self.mongodb_client.ensure_vector_search_index()
            query_embedding = self.openai_client.generate_embeddings(question)
            results = self.mongodb_client.vector_search(query_embedding, num_results)
            cosmosdb_logger.info(f"Vector search completed with {len(results)} results")
            context = prepare_context(results)
            messages = prepare_messages(context, question, chat_history)
            main_logger.debug(f"Prepared messages for OpenAI: {messages}")
            response = self.openai_client.generate_chat_completion(messages)
            openai_logger.info("Chat completion generated")
            main_logger.info("Query processed successfully")
            return response
        except Exception as e:
            main_logger.error(f"Error processing query: {e}")
            return "Kurza twarz! Wystąpił niezidentyfikowany błąd. 🐞"
        finally:
            self.mongodb_client.close()
