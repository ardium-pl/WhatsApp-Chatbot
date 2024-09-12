import asyncio
from quart import Quart
from hypercorn.config import Config
from hypercorn.asyncio import serve
from src.api.webhook import webhook_bp
from src.config import PORT
from src.worker import Worker
from src.logger import main_logger
from src.database.mysql_queries import initialize_connection_pool, close_connection_pool

app = Quart(__name__)
app.register_blueprint(webhook_bp)

# Initialize Worker
worker = Worker()


@app.before_serving
async def before_serving():
    await initialize_connection_pool()
    app.config['worker'] = worker


@app.after_serving
async def after_serving():
    await close_connection_pool()


async def run_quart():
    config = Config()
    config.bind = [f"0.0.0.0:{PORT}"]
    await serve(app, config)


async def main():
    main_logger.info("Starting the application")
    quart_task = asyncio.create_task(run_quart())
    worker_task = asyncio.create_task(worker.run())
    await asyncio.gather(quart_task, worker_task)
