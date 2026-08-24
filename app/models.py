from datetime import datetime, timezone
from app import db

class ShortURL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.Text, nullable=False)
    shortCode = db.Column(db.String(20), nullable=False)
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
    accessCount = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<ShortURL {self.shortCode}>"
