from flask import Flask
from flask_cors import CORS
from api.routes import api_bp
from config import Config
import logging

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def create_app():
    """Factory для створення Flask додатку"""
    app = Flask(__name__)
    app.config.from_object(Config)

    # CORS для API
    CORS(app)

    # Реєстрація blueprints
    app.register_blueprint(api_bp)

    logger.info("Application initialized")

    return app

if __name__ == '__main__':
    app = create_app()
    logger.info(f"Starting server on http://localhost:5000")
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=Config.DEBUG
    )
