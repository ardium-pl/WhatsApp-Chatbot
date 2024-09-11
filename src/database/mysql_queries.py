import json

from functools import wraps
import asyncmy
from src.logger import mysql_logger
from src.config import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE
from typing import Callable, Any, List
import asyncio

pools = []
MAX_POOLS = 4
current_pool = 0


async def initialize_pools():
    global pools
    for _ in range(MAX_POOLS):
        pool = await asyncmy.create_pool(
            minsize=3,
            maxsize=5,
            connect_timeout=10,
            host=MYSQL_HOST,
            port=int(MYSQL_PORT),
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            db=MYSQL_DATABASE
        )
        pools.append(pool)


async def close_pools():
    for pool in pools:
        await pool.close()


async def get_pool():
    global current_pool
    pool = pools[current_pool]
    current_pool = (current_pool + 1) % MAX_POOLS
    return pool


def with_connection(error_message="❌ A database error occurred."):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                pool = await get_pool()

                conn = await asyncio.wait_for(pool.acquire(), timeout=5)
                async with conn:
                    async with conn.cursor() as cur:
                        return await func(cur, conn, *args, **kwargs)

            except asyncio.TimeoutError:
                mysql_logger.error("⏱️ Timed out while waiting to acquire a connection from the pool.")
            except Exception as e:
                mysql_logger.error(error_message)
                mysql_logger.error(f"Error message: {e}")

            return None
        return wrapper
    return decorator


@with_connection(error_message="❌ Failed to insert a new user.")
async def insert_user(cur, conn, whatsapp_number_id: int) -> int:
    await cur.execute("INSERT INTO users (whatsapp_number_id) VALUES (%s)", (whatsapp_number_id,))
    await cur.execute("SELECT LAST_INSERT_ID()")
    await conn.commit()

    # Check if the insert was successful
    if cur.rowcount > 0:
        mysql_logger.info("➡️ New user inserted successfully.")
        mysql_logger.info(f"Type of cur.lastrowid: {type(cur.lastrowid)}")
        return cur.lastrowid
    else:
        raise RuntimeError("cur.rowcount == 0")


@with_connection(error_message="❌ Failed to retrieve a user id.")
async def get_user_id(cur, conn, whatsapp_number_id: int) -> int | None:
    await cur.execute("SELECT id FROM users WHERE whatsapp_number_id = %s", (whatsapp_number_id,))
    result = await cur.fetchone()

    if result:
        mysql_logger.info("➡️ User id retrieved successfully.")
        return result[0]
    else:
        mysql_logger.info("🥷 Message was sent by the unknown user. No user_id for the provided whatsapp_number_id")
        return None


@with_connection(error_message="❌ Failed to insert an answer-query pair.")
async def insert_query(cur, conn, user_id: int, query: str, answer: str) -> None:
    await cur.execute("INSERT INTO queries (user_id, query, answer) VALUES (%s, %s, %s)",
                      (user_id, query, answer))
    await conn.commit()

    # Check if the insert was successful
    if cur.rowcount > 0:
        mysql_logger.info("➡️ New answer-query pair inserted successfully.")
    else:
        raise RuntimeError("cur.rowcount == 0")


@with_connection(error_message="❌ Failed to retrieve recent queries form chat history.")
async def get_recent_queries(cur, conn, whatsapp_number_id: int) -> list:
    await cur.execute("""
        SELECT q.query, q.answer, q.created_at
        FROM queries q
        JOIN users u ON q.user_id = u.id
        WHERE u.whatsapp_number_id = %s
        AND q.created_at >= NOW() - INTERVAL 2 HOUR
        ORDER BY q.created_at DESC
        LIMIT 5
    """, (whatsapp_number_id,))
    results = await cur.fetchall()
    mysql_logger.info("➡️ Chat history retrieved successfully.")

    if results:
        chat_history = [{"query": query, "answer": answer, "created_at": created_at.isoformat()} for
                        query, answer, created_at in results]

        # Szczegółowe logowanie historii czatu
        log_message = f"📜 Retrieved {len(chat_history)} entries from chat history for user {whatsapp_number_id}:\n"
        for i, entry in enumerate(chat_history, 1):
            log_message += f"  {i}. 🗨️ Query: {entry['query'][:50]}{'...' if len(entry['query']) > 50 else ''}\n"
            log_message += f"     💬 Answer: {entry['answer'][:50]}{'...' if len(entry['answer']) > 50 else ''}\n"
            log_message += f"     🕒 Time: {entry['created_at']}\n"

        mysql_logger.info(log_message)
        mysql_logger.debug(f"Full chat history: {json.dumps(chat_history, indent=2)}")

        return chat_history
    else:
        mysql_logger.info("😑 Retrieved chat history is emtpy.")
        return []


async def insert_data_mysql(whatsapp_number_id: int, user_query: str, ai_answer: str) -> None:
    user_id = await get_user_id(whatsapp_number_id)
    if not user_id:
        user_id = await insert_user(whatsapp_number_id)

    await insert_query(user_id, user_query, ai_answer)