"""
Friendship Repository
======================

All database operations relating to friend requests and friendships.
Called only by FriendshipService — never directly by controllers.

Methods
-------
- send_request(requester_id, addressee_id) → Friendship
- accept_request(requester_id, addressee_id) → Friendship
- decline_or_cancel_request(requester_id, addressee_id) → bool
- block_user(requester_id, addressee_id) → Friendship
- unfriend(user_id, friend_id) → bool
- get_friends(user_id) → list[User]
- get_pending_received(user_id) → list[Friendship]
- get_pending_sent(user_id) → list[Friendship]
- are_friends(user_id, other_id) → bool
- get_friendship(user_id, other_id) → Friendship | None
"""

import logging
from typing import Optional

from sqlalchemy.exc import IntegrityError

from backend.extensions import db
from backend.models.friendship import Friendship, FriendshipStatus
from backend.models.user import User

logger = logging.getLogger(__name__)


class FriendshipRepository:
    """Data-access layer for friendship records."""

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    @staticmethod
    def send_request(requester_id: int, addressee_id: int) -> Friendship:
        """
        Create a new pending friend request.

        Parameters
        ----------
        requester_id : int  — The user sending the request.
        addressee_id : int  — The user receiving the request.

        Returns
        -------
        Friendship — the newly created record.

        Raises
        ------
        ValueError  — if the users are the same, or a request already exists.
        """
        if requester_id == addressee_id:
            raise ValueError("A user cannot send a friend request to themselves.")

        # Check if a relationship already exists in either direction
        existing = FriendshipRepository.get_friendship(requester_id, addressee_id)
        if existing:
            raise ValueError(
                f"A friendship/request already exists between {requester_id} and {addressee_id}."
            )

        friendship = Friendship(
            requester_id=requester_id,
            addressee_id=addressee_id,
            status=FriendshipStatus.PENDING,
        )
        db.session.add(friendship)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise ValueError("Duplicate friend request — already exists.")

        logger.info("Friend request sent: %d → %d", requester_id, addressee_id)
        return friendship

    @staticmethod
    def accept_request(requester_id: int, addressee_id: int) -> Friendship:
        """
        Accept a pending friend request.

        The addressee calls this to confirm acceptance.

        Parameters
        ----------
        requester_id : int  — Who originally sent the request.
        addressee_id : int  — The current user (who is accepting).

        Raises
        ------
        ValueError — if no pending request is found.
        """
        friendship = Friendship.query.filter_by(
            requester_id=requester_id,
            addressee_id=addressee_id,
            status=FriendshipStatus.PENDING,
        ).first()

        if not friendship:
            raise ValueError(
                f"No pending request from {requester_id} to {addressee_id}."
            )

        friendship.status = FriendshipStatus.ACCEPTED
        db.session.commit()
        logger.info("Friend request accepted: %d ↔ %d", requester_id, addressee_id)
        return friendship

    @staticmethod
    def decline_or_cancel_request(requester_id: int, addressee_id: int) -> bool:
        """
        Delete a pending friend request.

        Can be called by either the requester (cancel) or the addressee (decline).

        Returns True if a record was deleted, False if not found.
        """
        friendship = Friendship.query.filter_by(
            requester_id=requester_id,
            addressee_id=addressee_id,
            status=FriendshipStatus.PENDING,
        ).first()

        if not friendship:
            return False

        db.session.delete(friendship)
        db.session.commit()
        logger.info("Friend request declined/cancelled: %d ↔ %d", requester_id, addressee_id)
        return True

    @staticmethod
    def unfriend(user_id: int, friend_id: int) -> bool:
        """
        Remove an accepted friendship between two users.

        Checks both directions (since either user could be the requester).

        Returns True if deleted, False if not found.
        """
        friendship = Friendship.query.filter(
            db.or_(
                db.and_(
                    Friendship.requester_id == user_id,
                    Friendship.addressee_id == friend_id,
                ),
                db.and_(
                    Friendship.requester_id == friend_id,
                    Friendship.addressee_id == user_id,
                ),
            ),
            Friendship.status == FriendshipStatus.ACCEPTED,
        ).first()

        if not friendship:
            return False

        db.session.delete(friendship)
        db.session.commit()
        logger.info("Friendship removed: %d ↔ %d", user_id, friend_id)
        return True

    @staticmethod
    def block_user(blocker_id: int, blocked_id: int) -> Friendship:
        """
        Block a user. Creates a BLOCKED record (or updates an existing one).
        """
        # Remove any existing friendship/request first
        FriendshipRepository.unfriend(blocker_id, blocked_id)

        existing = FriendshipRepository.get_friendship(blocker_id, blocked_id)
        if existing:
            existing.status = FriendshipStatus.BLOCKED
            db.session.commit()
            return existing

        block = Friendship(
            requester_id=blocker_id,
            addressee_id=blocked_id,
            status=FriendshipStatus.BLOCKED,
        )
        db.session.add(block)
        db.session.commit()
        logger.info("User %d blocked user %d", blocker_id, blocked_id)
        return block

    # ------------------------------------------------------------------
    # Read operations
    # ------------------------------------------------------------------

    @staticmethod
    def get_friendship(user_id: int, other_id: int) -> Optional[Friendship]:
        """
        Return the Friendship record between two users (either direction),
        or None if no record exists.
        """
        return Friendship.query.filter(
            db.or_(
                db.and_(
                    Friendship.requester_id == user_id,
                    Friendship.addressee_id == other_id,
                ),
                db.and_(
                    Friendship.requester_id == other_id,
                    Friendship.addressee_id == user_id,
                ),
            )
        ).first()

    @staticmethod
    def are_friends(user_id: int, other_id: int) -> bool:
        """Return True if the two users have an accepted friendship."""
        record = FriendshipRepository.get_friendship(user_id, other_id)
        return record is not None and record.status == FriendshipStatus.ACCEPTED

    @staticmethod
    def get_friends(user_id: int) -> list[User]:
        """
        Return all User objects that have an ACCEPTED friendship with user_id.
        Queries both directions.
        """
        # Friends where this user is the requester
        sent = (
            db.session.query(User)
            .join(Friendship, Friendship.addressee_id == User.id)
            .filter(
                Friendship.requester_id == user_id,
                Friendship.status == FriendshipStatus.ACCEPTED,
            )
            .all()
        )

        # Friends where this user is the addressee
        received = (
            db.session.query(User)
            .join(Friendship, Friendship.requester_id == User.id)
            .filter(
                Friendship.addressee_id == user_id,
                Friendship.status == FriendshipStatus.ACCEPTED,
            )
            .all()
        )

        # Combine and deduplicate (shouldn't be dupes, but defensive)
        seen = set()
        friends = []
        for user in sent + received:
            if user.id not in seen:
                seen.add(user.id)
                friends.append(user)

        return friends

    @staticmethod
    def get_pending_received(user_id: int) -> list[Friendship]:
        """
        Return all PENDING friend requests that this user has received
        (they need to accept or decline these).
        """
        return Friendship.query.filter_by(
            addressee_id=user_id,
            status=FriendshipStatus.PENDING,
        ).order_by(Friendship.created_at.desc()).all()

    @staticmethod
    def get_pending_sent(user_id: int) -> list[Friendship]:
        """
        Return all PENDING friend requests that this user has sent
        (waiting for the other person to respond).
        """
        return Friendship.query.filter_by(
            requester_id=user_id,
            status=FriendshipStatus.PENDING,
        ).order_by(Friendship.created_at.desc()).all()

    @staticmethod
    def get_friend_count(user_id: int) -> int:
        """Return the number of accepted friends this user has."""
        return Friendship.query.filter(
            db.or_(
                Friendship.requester_id == user_id,
                Friendship.addressee_id == user_id,
            ),
            Friendship.status == FriendshipStatus.ACCEPTED,
        ).count()
