import asyncio
import psutil
from concurrent.futures import ThreadPoolExecutor
from src.queue.inmem_queue import InMemoryQueue
from src.ai.rag_engine import RAGEngine
from src.whatsapp.whatsapp_client import WhatsAppClient
from src.database.mysql_queries import insert_data_mysql
from src.logger import main_logger, whatsapp_logger, mysql_logger
from src.utils.resource_monitor import ResourceMonitor


class Worker:
    def __init__(self):
        self.request_queue = InMemoryQueue()
        self.rag_engine = RAGEngine()
        self.cpu_bound_executor = ThreadPoolExecutor(max_workers=9)  # 8 vCPU + 1
        self.io_bound_executor = ThreadPoolExecutor(max_workers=16)  # 2 * 8 vCPU
        self.resource_monitor = ResourceMonitor(interval=10)

    async def process_single_request(self, item):
        try:
            sender_phone_number = item['sender_phone_number']
            user_query = item['query']

            # Use thread pool for CPU-bound RAG processing
            ai_answer = await asyncio.get_event_loop().run_in_executor(
                self.cpu_bound_executor,
                self.rag_engine.process_query,
                user_query
            )

            # These operations can be done concurrently
            await asyncio.gather(
                self.io_bound_executor.submit(WhatsAppClient.send_message, ai_answer, sender_phone_number),
                self.io_bound_executor.submit(insert_data_mysql, sender_phone_number, user_query, ai_answer)
            )

            whatsapp_logger.info('AI answer sent and data inserted into MySQL')

        except Exception as e:
            main_logger.error(f'Error processing request: {e}')

    async def process_queue(self):
        while True:
            if self.resource_monitor.is_overloaded():
                await asyncio.sleep(1)  # Wait if system is overloaded
                continue

            tasks = []
            # Process up to 10 items concurrently (adjust based on your needs)
            for _ in range(10):
                item = self.request_queue.dequeue()
                if item:
                    tasks.append(asyncio.create_task(self.process_single_request(item)))
                else:
                    break

            if tasks:
                await asyncio.gather(*tasks)
            else:
                await asyncio.sleep(0.1)  # Short sleep if queue is empty

    async def run(self):
        main_logger.info("Starting optimized queue worker")
        self.resource_monitor.start()
        await self.process_queue()


async def main():
    worker = Worker()
    await worker.run()


def run_worker():
    asyncio.run(main())


if __name__ == "__main__":
    run_worker()
