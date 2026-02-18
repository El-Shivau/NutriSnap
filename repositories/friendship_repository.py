from models.friendship import Friendship
from extensions import db


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
