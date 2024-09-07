import asyncio
from flask import Flask, g
from hypercorn.config import Config
from hypercorn.asyncio import serve
from src.api.webhook import webhook_bp
from src.config import PORT
from src.worker import Worker, run_worker
from src.logger import main_logger
from src.database.mysql_queries import initialize_pools, close_pools

app = Flask(__name__)
app.register_blueprint(webhook_bp)

# Initialize Worker
worker = Worker()


@app.before_request
def before_request():
    g.worker = worker


async def run_flask():
    config = Config()
    config.bind = [f"0.0.0.0:{PORT}"]
    await serve(app, config)


async def initialize_app():
    main_logger.info("🔥Initializing MySQL connection pools")
    await initialize_pools()


async def shutdown_app():
    main_logger.info(" 👋 Closing MySQL connection pools")
    await close_pools()


async def main():
    main_logger.info("Starting the application")
    await initialize_app()
    try:
        flask_task = asyncio.create_task(run_flask())
        worker_task = asyncio.create_task(worker.run())
        await asyncio.gather(flask_task, worker_task)
    finally:
        await shutdown_app()


if __name__ == '__main__':
    asyncio.run(main())
