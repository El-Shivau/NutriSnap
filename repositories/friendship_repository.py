from models.friendship import Friendship
from models.friend_request import FriendRequest
from extensions import db
from datetime import datetime


class FriendshipRepository:
    @staticmethod
    def add_friend(user_id, friend_id):
        """Create mutual friendship (two rows)."""
        f1 = Friendship(user_id=user_id, friend_id=friend_id)
        f2 = Friendship(user_id=friend_id, friend_id=user_id)
        db.session.add(f1)
        db.session.add(f2)
        db.session.commit()
        return f1

    @staticmethod
    def are_friends(user_id, friend_id):
        """Check if a friendship exists."""
        return Friendship.query.filter_by(
            user_id=user_id, friend_id=friend_id
        ).first() is not None

    @staticmethod
    def get_friend_ids(user_id):
        """Return list of friend user IDs."""
        rows = Friendship.query.filter_by(user_id=user_id).all()
        return [r.friend_id for r in rows]

    @staticmethod
    def get_friends(user_id):
        """Return friendship rows with friend user objects."""
        return Friendship.query.filter_by(user_id=user_id).all()

    @staticmethod
    def remove_friend(user_id, friend_id):
        """Remove mutual friendship."""
        Friendship.query.filter_by(user_id=user_id, friend_id=friend_id).delete()
        Friendship.query.filter_by(user_id=friend_id, friend_id=user_id).delete()
        db.session.commit()

    @staticmethod
    def get_pending_request_between(user_id, friend_id):
        """Return pending request between two users, regardless of direction."""
        return FriendRequest.query.filter(
            FriendRequest.status == 'PENDING',
            db.or_(
                db.and_(FriendRequest.from_user_id == user_id, FriendRequest.to_user_id == friend_id),
                db.and_(FriendRequest.from_user_id == friend_id, FriendRequest.to_user_id == user_id)
            )
        ).first()

    @staticmethod
    def create_friend_request(from_user_id, to_user_id):
        request = FriendRequest(from_user_id=from_user_id, to_user_id=to_user_id, status='PENDING')
        db.session.add(request)
        db.session.commit()
        return request

    @staticmethod
    def get_incoming_requests(user_id):
        return FriendRequest.query.filter_by(to_user_id=user_id, status='PENDING').order_by(FriendRequest.created_at.desc()).all()

    @staticmethod
    def get_outgoing_requests(user_id):
        return FriendRequest.query.filter_by(from_user_id=user_id, status='PENDING').order_by(FriendRequest.created_at.desc()).all()

    @staticmethod
    def accept_request(request_id, current_user_id):
        request = FriendRequest.query.filter_by(id=request_id, to_user_id=current_user_id, status='PENDING').first()
        if not request:
            return None

        already_friends = FriendshipRepository.are_friends(request.from_user_id, request.to_user_id)
        if not already_friends:
            db.session.add(Friendship(user_id=request.from_user_id, friend_id=request.to_user_id))
            db.session.add(Friendship(user_id=request.to_user_id, friend_id=request.from_user_id))

        request.status = 'ACCEPTED'
        request.responded_at = datetime.utcnow()
        db.session.commit()
        return request
