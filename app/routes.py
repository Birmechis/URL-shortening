import string
import secrets
from urllib.parse import urlparse
from  datetime import datetime, timezone
from flask import Blueprint, request, jsonify, redirect
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from sqlalchemy import text
from .extensions import limiter
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

from app import db
from app.models import ShortURL, User, URLVisit

api_bp = Blueprint('api', __name__)

def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits
    while True:
        code = ''.join(secrets.choice(characters) for _ in range(length))
        if not ShortURL.query.filter_by(shortCode=code).first():
            return code

@api_bp.route('/shorten', methods=['POST'])
@limiter.limit("3 per minute")
@jwt_required()
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

    expires_at = data.get("expiresAt")

    if expires_at:
        try:
            expires_at = datetime.fromisoformat(expires_at)
        except ValueError:
            return jsonify({
                "error": "Invalid expiration date format"
            }), 400

    if expires_at:
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if expires_at <= datetime.now(timezone.utc):
            return jsonify({
                "error": "Expiration date must be in the future"
            }), 400

    user_id = get_jwt_identity()

    generate_code = generate_short_code()

    new_url = ShortURL(
        url=original_url,
        shortCode=generate_code,
        accessCount=0,
        expiresAt=expires_at,
        user_id = user_id
    )


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
            "expiresAt": new_url.expiresAt.isoformat() if new_url.expiresAt else None
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
@jwt_required()
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

    user_id = int(get_jwt_identity())
    short_url = ShortURL.query.filter_by(shortCode=shortCode).first()

    print("JWT USER ID:", user_id)
    print("JWT USER ID TYPE:", type(user_id))

    print("URL OWNER ID:", short_url.user_id)
    print("URL OWNER ID TYPE:", type(short_url.user_id))

    if short_url.user_id != user_id:
        return jsonify({
            "error": "You do not have permission to modify this URL"
        }), 403

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
@jwt_required()
def delete_short_url(shortCode):

    user_id = int(get_jwt_identity())
    short_url = ShortURL.query.filter_by(shortCode=shortCode).first()

    if not short_url:
        return jsonify({
            'error': 'Short URL not found'
        }), 401

    if short_url.user_id != user_id:
        return jsonify({
            "error": "You do not have permission to delete this URL"
        }), 403

    db.session.delete(short_url)
    db.session.commit()

    return jsonify({"success": True}), 200

@api_bp.route('/shorten/<shortCode>/stats', methods=['GET'])
@jwt_required()
def get_stats(shortCode):

    user_id = int(get_jwt_identity())
    code = ShortURL.query.filter_by(shortCode=shortCode).first()
    if not code:
        return jsonify({"error": "Short URL not found"}), 404

    if code.user_id != user_id:
        return jsonify({
            "error": "You do not have permission to see this URL"
        }), 403


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

    if shortUrl.expiresAt:
        expires_at = shortUrl.expiresAt

        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if expires_at <= datetime.now(timezone.utc):
            return jsonify({
                "error": "Short URL has expired"
            }), 410

    shortUrl.accessCount += 1

    visit = URLVisit(
        short_url_id=shortUrl.id,
        visited_at=datetime.now(timezone.utc),
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent'),
        referrer=request.referrer
    )

    db.session.add(visit)
    db.session.commit()

    return redirect(shortUrl.url, code=302)

@api_bp.route('/register', methods=['POST'])
def register():

    if not request.is_json:
        return jsonify({
            "error": "Request body must be JSON"
        }), 400

    data = request.get_json()

    print('PARSED DATA:', data)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body must be a JSON object"
        }), 400

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({
            "error": "Email or password is required"
        }), 400

    if not isinstance(email, str):
        return jsonify({
            "error": "Email must be string"
        }), 400

    email = email.strip().lower()

    if not isinstance(password, str):
        return jsonify({
            "error": "Password must be string"
        }), 400

    if len(password) < 8:
        return jsonify({
            "error": "Password must be at least 8 characters"
        }), 400

    exiting_user = User.query.filter_by(email=email).first()

    if exiting_user:
        return jsonify({
            "error": "Email address already exists"
        }), 409

    hashed_password = generate_password_hash(password)

    users = User(
        email=email,
        password_hash=hashed_password
    )

    db.session.add(users)
    db.session.commit()

    return jsonify({
        'message': 'User created successfully',
    }), 201

@api_bp.route('/login', methods=['POST'])
def login():

    if not request.is_json:
        return jsonify({
            "error": "Request body must be JSON"
        })

    data = request.get_json()

    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body must be json object"
        })

    email = request.json.get('email')
    password = request.json.get('password')

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({
            "error": "Invalid email or password"
        }), 401

    if not check_password_hash(user.password_hash, password):
        return jsonify({
            "error": "Invalid email or password"
        }), 401

    token = create_access_token(identity=str(user.id))

    return jsonify({
        'message': 'Successfully logged in',
        'access_token': token
    }), 200

@api_bp.route("/shorten/<shortCode>/analytics", methods=['GET'])
@jwt_required()
def analytics(shortCode):

    current_user_id = int(get_jwt_identity())

    url_record = ShortURL.query.filter_by(shortCode=shortCode).first()

    if not url_record:
        return jsonify({
            "error": "Short URL not found"
        }), 404

    if url_record.user_id != current_user_id:
        return jsonify({
            "error": "You are authenticated, but you're not allowed to do this "
        }), 403

    visits =  URLVisit.query.filter_by(
        short_url_id=url_record.id
    ).order_by(
        URLVisit.visited_at.desc()
    ).limit(20).all()

    return jsonify({
        "totalVisits": url_record.accessCount,
        "recentVisits":[
            {
                "visitedAt": visit.visited_at.isoformat(),
                "ipAddress": visit.ip_address,
                "userAgent": visit.user_agent,
                "referrer": visit.referrer
            }
            for visit in visits
        ]
    }), 200

@api_bp.route("/health")
def health():
    db.session.execute(text("SELECT 1"))

    return jsonify({
        "status": "healthy"
    }), 200