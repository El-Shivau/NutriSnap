"""
User Model
==========

Represents a registered user of NutriSnap.

Table: users
------------
- id            : Primary key (auto-incremented integer).
- username      : Unique display name (max 80 chars).
- email         : Unique email address (max 120 chars).
- password_hash : Bcrypt-hashed password (NEVER store plaintext).
- created_at    : Timestamp of account creation (UTC).
- is_active     : Soft-disable account without deleting it.

Flask-Login Integration
-----------------------
The UserMixin provides the required properties and methods:
  - is_authenticated
  - is_active
  - is_anonymous
  - get_id()
"""

from datetime import datetime, timezone

from flask_login import UserMixin

from backend.extensions import db


class User(UserMixin, db.Model):
    """SQLAlchemy model for NutriSnap user accounts."""

    __tablename__ = "users"

    # Primary key
    id: int = db.Column(db.Integer, primary_key=True)

    # User identity
    username: str = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email: str = db.Column(db.String(120), unique=True, nullable=False, index=True)

    # Security — only the HASH is stored, never the plaintext password
    password_hash: str = db.Column(db.String(255), nullable=False)

    # Metadata
    created_at: datetime = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    is_active: bool = db.Column(db.Boolean, nullable=False, default=True)

    # Profile
    bio: str | None = db.Column(db.Text, nullable=True)
    avatar_url: str | None = db.Column(db.String(512), nullable=True)

    # Relationships
    food_logs = db.relationship(
        "FoodLog",
        backref="user",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username!r}>"

    def to_dict(self) -> dict:
        """Serialise the user to a safe dictionary (excludes password_hash)."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat(),
            "is_active": self.is_active,
            "bio": self.bio,
            "avatar_url": self.avatar_url,
        }
