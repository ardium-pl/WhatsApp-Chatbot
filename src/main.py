from flask import Flask
from api.webhook import webhook_bp
from src.config import PORT

app = Flask(__name__)
app.register_blueprint(webhook_bp)

if __name__ == '__main__':
    app.run(port=PORT, debug=False)