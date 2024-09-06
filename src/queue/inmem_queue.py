import asyncio
from asyncio import Queue


class AsyncInMemoryQueue:
    """
    Asyncio-compatible in-memory queue implementation.

    TODO: In the future, consider replacing this with a database-backed queue
    for better persistence and scalability. Potential options include:
    - Asyncio-compatible database like aiosqlite or asyncpg
    - Distributed queue systems with async support like aio-pika (RabbitMQ) or aiokafka

    When migrating, ensure to maintain the same interface (enqueue, dequeue, queue_length)
    to minimize changes in the rest of the application.
    """

    def __init__(self):
        self._queue = Queue()
        self._lock = asyncio.Lock()

    async def enqueue(self, item):
        async with self._lock:
            await self._queue.put(item)

    async def dequeue(self):
        async with self._lock:
            if not self._queue.empty():
                return await self._queue.get()
            return None

    async def queue_length(self):
        async with self._lock:
            return self._queue.qsize()
