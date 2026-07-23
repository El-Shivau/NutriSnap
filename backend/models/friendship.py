"""
Friendship Model
=================

Represents a directional friend request or established friendship
between two NutriSnap users.

Table: friendships
------------------
Each row represents one relationship from user → friend.
Status transitions:
  1. User A sends a request   → status='pending',  requester=A, addressee=B
  2. User B accepts           → status='accepted'
  3. Either user unfriends    → row is deleted

To find all of User A's friends, query for rows where:
  (requester_id=A OR addressee_id=A) AND status='accepted'

Design Decision — Directional Rows
------------------------------------
We store one row per directional request (not two rows per friendship).
This keeps the pending/accepted state in one place and avoids duplicates.
The repository layer handles querying both directions transparently.
"""

from datetime import datetime, timezone
from enum import Enum as PyEnum

from backend.extensions import db


class FriendshipStatus(PyEnum):
    """Possible states of a friendship record."""
    PENDING  = "pending"   # Request sent, not yet accepted
    ACCEPTED = "accepted"  # Both users are friends
    BLOCKED  = "blocked"   # Requester has blocked the addressee


class Friendship(db.Model):
    """
    SQLAlchemy model representing a friend request or friendship.

    Constraints
    -----------
    - A user cannot send a request to themselves (enforced in repository).
    - Duplicate requests are prevented by a unique constraint on
      (requester_id, addressee_id).
    """

    __tablename__ = "friendships"

    # Unique constraint: one row per (requester, addressee) pair
    __table_args__ = (
        db.UniqueConstraint("requester_id", "addressee_id", name="uq_friendship_pair"),
    )

    # Primary key
    id: int = db.Column(db.Integer, primary_key=True)

    # The user who initiated the request
    requester_id: int = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # The user who received the request
    addressee_id: int = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Current relationship status
    status: str = db.Column(
        db.Enum(FriendshipStatus),
        nullable=False,
        default=FriendshipStatus.PENDING,
    )

    # Timestamps
    created_at: datetime = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: datetime = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships — access the actual User objects
    requester = db.relationship(
        "User",
        foreign_keys=[requester_id],
        backref=db.backref("sent_requests", lazy="dynamic", cascade="all, delete-orphan"),
    )
    addressee = db.relationship(
        "User",
        foreign_keys=[addressee_id],
        backref=db.backref("received_requests", lazy="dynamic", cascade="all, delete-orphan"),
    )

    def __repr__(self) -> str:
        return (
            f"<Friendship requester={self.requester_id} "
            f"addressee={self.addressee_id} status={self.status.value!r}>"
        )

    def to_dict(self) -> dict:
        """Serialise the friendship record to a dictionary."""
        return {
            "id": self.id,
            "requester_id": self.requester_id,
            "addressee_id": self.addressee_id,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
