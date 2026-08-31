import string
import secrets
from flask import Blueprint, request, jsonify
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
    data = request.get_json() or {}
    original_url = data.get("url")

    if not original_url:
        return jsonify({"error": "URL parameter is required"}), 400

    generate_code = generate_short_code()

    new_url = ShortURL(url=original_url, shortCode=generate_code, accessCount=0)


    try:
        db.session.add(new_url)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Database entry creation failed"}), 500

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
        return jsonify({"error": "URL parameter is required"}), 400
    return jsonify(
        {
            "id": data.id,
            "url": data.url,
            "createdAt": data.createdAt.isoformat() if data.createdAt else None,
            "updatedAt": data.updatedAt.isoformat() if data.updatedAt else None
        }
    ), 404

@api_bp.route('/shorten/<shortCode>', methods=['PUT'])
def update_short_url(shortCode):
    data = request.get_json() or {}
    original_url = data.get("url")

    if not original_url:
        return jsonify({"error": "URL parameter is required"}), 400

    updates = ShortURL(url=original_url, shortCode=shortCode, accessCount=0)

    try:
        updates.url = request.json['url']

        db.session.commit()
        return jsonify(
            {
                "url": updates.url
            }
        ), 200
    except Exception:
        db.session.rollback()
        return jsonify({"error"}), 400

@api_bp.route('/shorten/<shortCode>', methods=['DELETE'])
def delete_short_url(shortCode):
    deletes = ShortURL.query.filter_by(shortCode=shortCode).first()

    if not deletes:
        return jsonify({"error": "URL parameter is not found"}), 404
    db.session.delete(deletes)
    db.session.commit()

    return jsonify({"success": True}), 200