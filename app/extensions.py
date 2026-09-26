from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_migrate import Migrate
from flask_limiter.util import get_remote_address
import redis

db = SQLAlchemy()

limiter = Limiter(
    key_func=get_remote_address,
)

migrate = Migrate()

jwt = JWTManager()

def create_redis_client(redis_url):
    return redis.Redis.from_url(
        redis_url,
        decode_responses=True,
    )