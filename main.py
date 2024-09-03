import asyncio
from flask import Flask, render_template, request, jsonify
from hypercorn.config import Config
from hypercorn.asyncio import serve
from src.api.webhook import webhook_bp
from src.config import PORT
from src.worker import Worker, run_worker
from src.logger import main_logger

app = Flask(__name__, template_folder='template')
app.register_blueprint(webhook_bp)

# Inicjalizacja Worker'a
worker = Worker()


@app.route('/')
async def index():
    return render_template('template.html')


# @app.route('/api/query', methods=['POST'])
# async def process_query():
#     data = request.json
#     query = data.get('query')
#
#     # Użyj metody process_single_request z Worker'a
#     try:
#         # Symulujemy request, dodając sztuczny sender_phone_number
#         item = {'sender_phone_number': 'test', 'query': query}
#         await worker.process_single_request(item)
#         response = "Query processed successfully"  # Tutaj możesz dodać rzeczywistą odpowiedź
#     except Exception as e:
#         main_logger.error(f"Error processing query: {e}")
#         response = f"Error: {str(e)}"
#
#     return jsonify({'response': response})

@app.route('/api/query', methods=['POST'])
async def process_query():
    data = request.json
    query = data.get('query')

    try:
        # Symulujemy request, dodając sztuczny sender_phone_number
        item = {'sender_phone_number': 'test', 'query': query}
        await worker.process_single_request(item)
        response = "Query processed successfully"
    except Exception as e:
        main_logger.error(f"Error processing query: {e}")
        response = f"Error: {str(e)}"

    return jsonify({'response': response})


async def run_flask():
    config = Config()
    config.bind = [f"0.0.0.0:{PORT}"]
    await serve(app, config)


async def main():
    main_logger.info("Starting the application")
    flask_task = asyncio.create_task(run_flask())
    worker_task = asyncio.create_task(asyncio.to_thread(run_worker))
    await asyncio.gather(flask_task, worker_task)


if __name__ == '__main__':
    asyncio.run(main())
