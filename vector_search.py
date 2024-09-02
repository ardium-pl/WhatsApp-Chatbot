from logger import logger_main
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from tenacity import retry, wait_random_exponential, stop_after_attempt
from datetime import datetime
from pprint import pformat
from OpenAI.openai_embeddings import generate_embeddings
from OpenAI.openai_chat import system_prompt
from OpenAI.openai_config import client

# Ensure vector search index
def ensure_vector_search_index(collection):
    try:
        index_name = "vectorSearchIndex"
        existing_indexes = collection.list_indexes()
        if any(index["name"] == index_name for index in existing_indexes):
            logger_main.info(f"Vector search index {index_name} already exists")
            return

        collection.create_index(
            [("vector", "cosmosSearch")],
            name=index_name,
            cosmosSearchOptions={
                "kind": "vector-ivf",
                "numLists": 1,
                "similarity": "COS",
                "dimensions": 1536
            }
        )
        logger_main.info(f"Index {index_name} created successfully")
    except Exception as e:
        logger_main.error(f"Error creating vector search index: {e}")
        raise


# Vector search function
def vector_search(collection, query, num_results=10):
    query_embedding = generate_embeddings(query)
    try:
        results = collection.aggregate([
            {
                "$search": {
                    "cosmosSearch": {
                        "vector": query_embedding,
                        "path": "vector",
                        "k": num_results
                    }
                }
            },
            {
                "$project": {
                    "similarityScore": {"$meta": "searchScore"},
                    "content": 1,
                    "_id": 1,
                    "title": 1,
                    "pageNumber": 1,
                    "createdAt": 1,
                    "wordCount": {"$size": {"$split": ["$content", " "]}}
                }
            }
        ])

        results_list = list(results)
        logger_main.info(f"Vector search results for query: '{query}'")
        for i, result in enumerate(results_list, 1):
            logger_main.info(f"Result {i}:")
            logger_main.info(f"Similarity Score: {result.get('similarityScore', 'N/A')}")
            logger_main.info(f"Document ID: {result.get('_id', 'N/A')}")
            logger_main.info(f"Title: {result.get('title', 'N/A')}")
            logger_main.info(f"Page Number: {result.get('pageNumber', 'N/A')}")
            logger_main.info(f"Content: {result.get('content', 'N/A')[:100]}...")

            created_at = result.get('createdAt')
            if created_at:
                if isinstance(created_at, datetime):
                    created_at_str = created_at.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    created_at_str = str(created_at)
            else:
                created_at_str = 'N/A'
            logger_main.info(f"Created At: {created_at_str}")

            logger_main.info(f"Word Count: {result.get('wordCount', 'N/A')}")
            logger_main.info("Full result structure:")
            logger_main.info(pformat(result))
            logger_main.info("-" * 50)

        return results_list
    except Exception as e:
        logger_main.error(f"Vector search operation failed: {e}")
        return []


# RAG function
def rag_with_vector_search(collection, question, num_results=10):
    results = vector_search(collection, question, num_results=num_results)
    context = ""
    for result in results:
        context += f"Title: {result.get('title', 'N/A')}\n"
        context += f"Page: {result.get('pageNumber', 'N/A')}\n"
        context += f"Content: {result.get('content', 'N/A')}\n"
        context += f"Created At: {result.get('createdAt', 'N/A')}\n"
        context += f"Word Count: {result.get('wordCount', 'N/A')}\n\n"
    messages = [
        {"role": "system", "content": system_prompt + context},
        {"role": "user", "content": question}
    ]

    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
        return completion.choices[0].message.content
    except Exception as e:
        logger_main.error(f"Error with OpenAI ChatCompletion: {e}")
        return "An error occurred while generating the response."
