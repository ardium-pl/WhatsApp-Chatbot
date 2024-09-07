from quart import g
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


def with_connection(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        pool = await get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                return await func(cur, conn, *args, **kwargs)

    return wrapper


@with_connection
async def insert_user(cur, conn, whatsapp_number_id: int) -> int:
    await cur.execute("INSERT INTO users (whatsapp_number_id) VALUES (%s)", (whatsapp_number_id,))
    await cur.execute("SELECT LAST_INSERT_ID()")
    await conn.commit()
    return (await cur.fetchone())[0]


@with_connection
async def get_user_id(cur, conn, whatsapp_number_id: int) -> int:
    await cur.execute("SELECT id FROM users WHERE whatsapp_number_id = %s", (whatsapp_number_id,))
    result = await cur.fetchone()
    return result[0] if result else None


@with_connection
async def insert_query(cur, conn, user_id: int, query: str, answer: str) -> None:
    await cur.execute("INSERT INTO queries (user_id, query, answer) VALUES (%s, %s, %s)",
                      (user_id, query, answer))
    await conn.commit()


@with_connection
async def get_recent_queries(cur, conn, whatsapp_number_id: int) -> list:
    await cur.execute("""
        SELECT q.query, q.answer
        FROM queries q
        JOIN users u ON q.user_id = u.id
        WHERE u.whatsapp_number_id = %s
        AND q.created_at >= NOW() - INTERVAL 2 HOUR
        ORDER BY q.created_at DESC
        LIMIT 5
    """, (whatsapp_number_id,))
    results = await cur.fetchall()
    return [{"query": query, "answer": answer} for query, answer in results]


@with_connection
async def insert_data_mysql(cur, conn, sender_phone_number: str, user_query: str, ai_answer: str) -> None:
    try:
        whatsapp_number_id = int(sender_phone_number)
    except ValueError:
        mysql_logger.error(f"❌ Invalid phone number format: {sender_phone_number}")
        return

    await cur.execute("SELECT id FROM users WHERE whatsapp_number_id = %s", (whatsapp_number_id,))
    result = await cur.fetchone()

    if not result:
        mysql_logger.info("🔧 Message was sent by the unknown user. Adding new user to the database...")
        await cur.execute("INSERT INTO users (whatsapp_number_id) VALUES (%s)", (whatsapp_number_id,))
        user_id = cur.lastrowid
        mysql_logger.info("✅ New user added!")
    else:
        user_id = result[0]

    await cur.execute("INSERT INTO queries (user_id, query, answer) VALUES (%s, %s, %s)",
                      (user_id, user_query, ai_answer))
    await conn.commit()
    mysql_logger.info("✅ New record inserted successfully into MySQL.")


async def get_chat_history(sender_phone_number: str) -> list:
    try:
        whatsapp_number_id = int(sender_phone_number)
    except ValueError:
        mysql_logger.error(f"❌ Invalid phone number format: {sender_phone_number}")
        return []

    return await get_recent_queries(whatsapp_number_id)
