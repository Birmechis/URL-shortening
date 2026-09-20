import os
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

load_dotenv()
db = SQLAlchemy()

def create_app(config=None):
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    if config:
        app.config.update(config)

    db.init_app(app)

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

    return app