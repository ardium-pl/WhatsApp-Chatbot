import asyncmy
from src.logger import mysql_logger
from src.config import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE
from functools import wraps
from typing import Callable, Any, List
import asyncio

# Lista pul połączeń
pools: List[asyncmy.Pool] = []
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


async def get_pool():
    global current_pool
    if not pools:
        await initialize_pools()
    pool = pools[current_pool]
    current_pool = (current_pool + 1) % MAX_POOLS
    return pool


def with_connection(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        pool = await get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                return await func(cur, *args, **kwargs)

    return wrapper


@with_connection
async def insert_user(cur, whatsapp_number_id: int) -> int:
    await cur.execute("INSERT INTO users (whatsapp_number_id) VALUES (%s)", (whatsapp_number_id,))
    await cur.execute("SELECT LAST_INSERT_ID()")
    return (await cur.fetchone())[0]


@with_connection
async def get_user_id(cur, whatsapp_number_id: int) -> int:
    await cur.execute("SELECT id FROM users WHERE whatsapp_number_id = %s", (whatsapp_number_id,))
    result = await cur.fetchone()
    return result[0] if result else None


@with_connection
async def insert_query(cur, user_id: int, query: str, answer: str) -> None:
    await cur.execute("INSERT INTO queries (user_id, query, answer) VALUES (%s, %s, %s)",
                      (user_id, query, answer))


@with_connection
async def get_recent_queries(cur, whatsapp_number_id: int) -> list:
    await cur.execute("""
        SELECT q.query, q.answer
        FROM queries q
        JOIN users u ON q.user_id = u.id
        WHERE u.whatsapp_number_id = %s
        AND q.created_at >= NOW() - INTERVAL 2 HOUR
        ORDER BY q.created_at ASC
        LIMIT 5
    """, (whatsapp_number_id,))
    results = await cur.fetchall()
    return [{"query": query, "answer": answer} for query, answer in results]


async def insert_data_mysql(sender_phone_number: str, user_query: str, ai_answer: str) -> None:
    try:
        whatsapp_number_id = int(sender_phone_number)
    except ValueError:
        mysql_logger.error(f"❌ Invalid phone number format: {sender_phone_number}")
        return

    user_id = await get_user_id(whatsapp_number_id)
    if user_id is None:
        mysql_logger.info("🔧 Message was sent by the unknown user. Adding new user to the database...")
        user_id = await insert_user(whatsapp_number_id)
        mysql_logger.info("✅ New user added!")

    await insert_query(user_id, user_query, ai_answer)
    mysql_logger.info("✅ New record inserted successfully into MySQL.")


async def get_chat_history(sender_phone_number: str) -> list:
    try:
        whatsapp_number_id = int(sender_phone_number)
    except ValueError:
        mysql_logger.error(f"❌ Invalid phone number format: {sender_phone_number}")
        return []

    return await get_recent_queries(whatsapp_number_id)


# Funkcja do zamykania pul połączeń
async def close_pools():
    for pool in pools:
        await pool.close()


# Inicjalizacja pul przy starcie aplikacji
async def initialize_app():
    await initialize_pools()


# Zamykanie pul przy zamykaniu aplikacji
async def shutdown_app():
    await close_pools()
