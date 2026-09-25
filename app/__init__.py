import os
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .extensions import limiter, jwt

load_dotenv()
db = SQLAlchemy()
migrate = Migrate()

def create_app(config=None):
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

    if config:
        app.config.update(config)

    db.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)
    jwt.init_app(app)

    from app.routes import api_bp
    app.register_blueprint(api_bp)

    @app.errorhandler(404)
    def handler_404(error):
        return jsonify({
            "error": "Resource not found"
        }), 404

    @app.errorhandler(500)
    def handler_500(error):
        return jsonify({
            "error": "Internal server error"
        }), 500

    @app.errorhandler(429)
    def handle_rate_limit(error):
        return jsonify({
            "error": "Too many requests"
        }), 429

    return app