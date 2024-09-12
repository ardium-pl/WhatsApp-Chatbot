import asyncio
from quart import Quart
from hypercorn.config import Config
from hypercorn.asyncio import serve
from src.api.webhook import webhook_bp
from src.config import PORT
from src.logger import main_logger
from src.database.mysql_queries import initialize_connection_pools, close_connection_pools

app = Quart(__name__)
app.register_blueprint(webhook_bp)


@app.before_serving
async def before_serving():
    await initialize_connection_pools()


@app.after_serving
async def after_serving():
    await close_connection_pools()


async def run_quart():
    config = Config()
    config.bind = [f"0.0.0.0:{PORT}"]
    await serve(app, config)


async def main(): # TODO delete
    main_logger.info("Starting the application")
    quart_task = asyncio.create_task(run_quart())
    await asyncio.gather(quart_task)
