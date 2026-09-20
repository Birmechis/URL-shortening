import string
import secrets
from urllib.parse import urlparse

from flask import Blueprint, request, jsonify, redirect
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import ShortURL

api_bp = Blueprint('api', __name__)

def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits
    while True:
        code = ''.join(secrets.choice(characters) for _ in range(length))
        if not ShortURL.query.filter_by(shortCode=code).first():
            return code

@api_bp.route('/shorten', methods=['POST'])
def shorten_url():

    if not request.is_json:
        return jsonify({
            "error": "Request body must be JSON"
        }), 400

    data = request.get_json()

    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body must be a JSON object"
        }), 400

    original_url = data.get("url")

    if not original_url:
        return jsonify({"error": "URL parameter is required"}), 400

    if  not isinstance(original_url, str):
        return jsonify({"error": "URL must be a string"}), 400

    original_url = original_url.strip()

    if not original_url:
        return jsonify({"error": "URL cannot be empty"}), 400

    parsed_url = urlparse(original_url)

    if parsed_url.scheme not in ("http", "https"):
        return jsonify({"error": "URL scheme must be http or https"}), 400

    if not parsed_url.netloc:
        return jsonify({"error": "URL must contain a valid domain"}), 400


    generate_code = generate_short_code()

    new_url = ShortURL(url=original_url, shortCode=generate_code, accessCount=0)


    try:
        db.session.add(new_url)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "error": "Short code already exists"
        }), 409

    return jsonify(
        {
            "id": new_url.id,
            "url": new_url.url,
            "shortCode": new_url.shortCode,
            "createdAt": new_url.createdAt.isoformat() if new_url.createdAt else None,
            "updatedAt": new_url.updatedAt.isoformat() if new_url.updatedAt else None
        }
    ), 201
@api_bp.route('/shorten/<shortCode>', methods=['GET'])
def get_original_url(shortCode=None):
    data = ShortURL.query.filter_by(shortCode=shortCode).first()
    if not data:
        return jsonify({
            "error": "Short URL not found"
        }), 404
    return jsonify(
        {
            "id": data.id,
            "url": data.url,
            "createdAt": data.createdAt.isoformat() if data.createdAt else None,
            "updatedAt": data.updatedAt.isoformat() if data.updatedAt else None,
            "accessCount": data.accessCount if data.accessCount else 0
        }
    ), 200

@api_bp.route('/shorten/<shortCode>', methods=['PUT'])
def update_short_url(shortCode):

    if not request.is_json:
        return jsonify({
            "error": "Request body must be JSON"
        }), 400

    data = request.get_json()

    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body must be a JSON object"
        }), 400

    original_url = data.get("url")

    if not original_url:
        return jsonify({"error": "URL parameter is required"}), 400

    if not isinstance(original_url, str):
        return jsonify({"error": "URL must be a string"}), 400

    original_url = original_url.strip()

    if not original_url:
        return jsonify({"error": "URL cannot be empty"}), 400

    parsed_url = urlparse(original_url)

    if parsed_url.scheme not in ("http", "https"):
        return jsonify({"error": "URL schema must be http or https"}), 400

    if not parsed_url.netloc:
        return jsonify({"error": "URL must contain a valid domain"}), 400

    short_url = ShortURL.query.filter_by(shortCode=shortCode).first()

    if not short_url:
        return jsonify({"error": "Short URL not found"}), 404

    short_url.url = original_url

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({
            "error": "Database update failed"
        }), 500

    return jsonify({
        "id": short_url.id,
        "url": short_url.url,
        "shortCode": short_url.shortCode,
        "createdAt": short_url.createdAt.isoformat()
        if short_url.createdAt else None,
        "updatedAt": short_url.updatedAt.isoformat()
        if short_url.updatedAt else None,
        "accessCount": short_url.accessCount
    }), 200

@api_bp.route('/shorten/<shortCode>', methods=['DELETE'])
def delete_short_url(shortCode):
    deletes = ShortURL.query.filter_by(shortCode=shortCode).first()

    if not deletes:
        return jsonify({"error": "Short URL not found"}), 404
    db.session.delete(deletes)
    db.session.commit()

    return jsonify({"success": True}), 200

@api_bp.route('/shorten/<shortCode>/stats', methods=['GET'])
def get_stats(shortCode):
    code = ShortURL.query.filter_by(shortCode=shortCode).first()
    if not code:
        return jsonify({"error": "Short URL not found"}), 404


    return jsonify({
        "id": code.id,
        "url": code.url,
        "shortCode": code.shortCode,
        "createdAt": code.createdAt.isoformat() if code.createdAt else None,
        "updatedAt": code.updatedAt.isoformat() if code.updatedAt else None,
        "accessCount": code.accessCount if code.accessCount else 0
    }), 200

@api_bp.route("/<shortCode>", methods=['GET'])
def redirect_url(shortCode):
    shortUrl = ShortURL.query.filter_by(shortCode=shortCode).first()

    if not shortUrl:
        return jsonify({
            "error": "Short URL not found"
        }), 404

    shortUrl.accessCount += 1
    db.session.commit()

    return redirect(shortUrl.url, code=302)