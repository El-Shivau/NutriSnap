from extensions import db
from datetime import datetime


class Friendship(db.Model):
    __tablename__ = 'friendships'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    friend_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='friendships_initiated')
    friend = db.relationship('User', foreign_keys=[friend_id])

    def __repr__(self):
        return f'<Friendship {self.user_id} <-> {self.friend_id}>'
