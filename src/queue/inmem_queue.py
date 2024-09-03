from queue import Queue
import threading


class InMemoryQueue:
    """
    In-memory queue implementation.

    TODO: In the future, consider replacing this with a database-backed queue
    for better persistence and scalability. Potential options include:
    - SQLite for a lightweight, file-based solution
    - PostgreSQL or MySQL for a more robust, scalable solution
    - Distributed queue systems like RabbitMQ or Apache Kafka for high-volume scenarios

    When migrating, ensure to maintain the same interface (enqueue, dequeue, queue_length)
    to minimize changes in the rest of the application.
    """

    def __init__(self):
        self._queue = Queue()
        self._lock = threading.Lock()

    def enqueue(self, item):
        with self._lock:
            self._queue.put(item)

    def dequeue(self):
        with self._lock:
            if not self._queue.empty():
                return self._queue.get()
            return None

    def queue_length(self):
        with self._lock:
            return self._queue.qsize()
