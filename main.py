import asyncio
from flask import Flask
from hypercorn.config import Config
from hypercorn.asyncio import serve
from src.api.webhook import webhook_bp
from src.config import PORT
from src.worker import Worker, run_worker
from src.logger import main_logger

app = Flask(__name__)
app.register_blueprint(webhook_bp)

# Initialize Worker
worker = Worker()
app.worker = worker
main_logger.info("Worker initialized and attached to app context")


async def run_flask():
    config = Config()
    config.bind = [f"0.0.0.0:{PORT}"]
    await serve(app, config)


async def main():
    main_logger.info("Starting the application")
    flask_task = asyncio.create_task(run_flask())
    worker_task = asyncio.create_task(worker.run())
    await asyncio.gather(flask_task, worker_task)


if __name__ == '__main__':
    asyncio.run(main())
