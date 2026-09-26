from datetime import datetime, timezone
from app import db

class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self):
        return f"<User {self.email}>"

class ShortURL(db.Model):
    __tablename__ = "short_urls"

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.Text, nullable=False)
    shortCode = db.Column(db.String(20), unique=True, nullable=False)
    createdAt = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updatedAt = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    accessCount = db.Column(db.Integer, default=0, nullable=False)
    expiresAt = db.Column(
        db.DateTime,
        nullable=True,
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey(User.id),
        nullable=False
    )

    user = db.relationship("User", backref="short_urls")

    visits = db.relationship(
        "URLVisit",
        backref="short_urls",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<ShortURL {self.shortCode}>"

class URLVisit(db.Model):
    id=db.Column(db.Integer, primary_key=True)

    short_url_id=db.Column(db.Integer, db.ForeignKey(ShortURL.id), nullable=False)

    visited_at=db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    ip_address=db.Column(db.String(100), nullable=True)

    user_agent=db.Column(db.Text, nullable=True)

    referrer=db.Column(db.Text, nullable=True)