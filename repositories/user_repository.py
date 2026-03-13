from models.user import User
from extensions import db

class UserRepository:
    @staticmethod
    def get_by_email(email):
        return User.query.filter_by(email=email).first()

    @staticmethod
    def get_by_username(username):
        """Case-sensitive exact username lookup."""
        # filter_by is case-insensitive on SQLite; verify exact match in Python
        user = User.query.filter(User.username.ilike(username)).first()
        if user and user.username == username:
            return user
        return None

    @staticmethod
    def search_by_prefix(prefix, exclude_user_id=None, limit=8):
        """Return users whose username starts with prefix (case-insensitive, for suggestions)."""
        query = User.query.filter(User.username.ilike(f'{prefix}%'))
        if exclude_user_id:
            query = query.filter(User.id != exclude_user_id)
        return query.order_by(User.username).limit(limit).all()

    @staticmethod
    def get_by_id(user_id):
        return User.query.get(user_id)

    @staticmethod
    def get_all_users():
        return User.query.all()

    @staticmethod
    def create(username, email, password_hash, role='USER'):
        user = User(username=username, email=email, password_hash=password_hash, role=role)
        db.session.add(user)
        db.session.commit()
        return user
