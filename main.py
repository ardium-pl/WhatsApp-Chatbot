import asyncio
from functools import wraps
from flask import Flask, g, request
from hypercorn.config import Config
from hypercorn.asyncio import serve
from quart import Quart
from quart_flask_patch import patch_quart
from src.api.webhook import webhook_bp
from src.config import PORT
from src.worker import Worker
from src.logger import main_logger
from src.database.mysql_queries import initialize_pools, close_pools, get_pool

# Tworzymy aplikację Quart zamiast Flask
app = Quart(__name__)
patch_quart(app)  # Pozwala na używanie rozszerzeń Flask z Quart
app.register_blueprint(webhook_bp)

# Initialize Worker
worker = Worker()

def async_to_sync(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapper

@app.before_request
async def before_request():
    g.worker = worker
    g.pool = await get_pool()

@app.after_request
async def after_request(response):
    if hasattr(g, 'pool'):
        await g.pool.release()
    return response

async def run_quart():
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
        quart_task = asyncio.create_task(run_quart())
        worker_task = asyncio.create_task(worker.run())
        await asyncio.gather(quart_task, worker_task)
    finally:
        await shutdown_app()


if __name__ == '__main__':
    asyncio.run(main())
