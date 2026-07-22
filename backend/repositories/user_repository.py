"""
User Repository
===============

Handles all database access for the User model.

Repositories are the ONLY layer that should perform SQLAlchemy queries.
Services call repositories; controllers never call repositories directly.

This keeps database logic isolated and makes it easy to:
  - Unit test services with a mock repository.
  - Switch the database layer without touching business logic.
"""

import logging
from typing import Optional

from backend.extensions import db
from backend.models.user import User

logger = logging.getLogger(__name__)


class UserRepository:
    """Data access object for User model operations."""

    def find_by_id(self, user_id: int) -> Optional[User]:
        """
        Find a user by their primary key.

        Parameters
        ----------
        user_id : int
            The user's database ID.

        Returns
        -------
        User | None
        """
        return db.session.get(User, user_id)

    def find_by_email(self, email: str) -> Optional[User]:
        """
        Find a user by their email address.

        Parameters
        ----------
        email : str
            The email to search for (case-insensitive).

        Returns
        -------
        User | None
        """
        return User.query.filter_by(email=email.lower()).first()

    def find_by_username(self, username: str) -> Optional[User]:
        """
        Find a user by their username.

        Parameters
        ----------
        username : str
            The username to search for.

        Returns
        -------
        User | None
        """
        return User.query.filter_by(username=username).first()

    def save(self, user: User) -> User:
        """
        Persist a new or updated User to the database.

        Parameters
        ----------
        user : User
            The User object to save.

        Returns
        -------
        User
            The saved user with any database-generated fields populated.
        """
        db.session.add(user)
        db.session.commit()
        logger.debug("Saved user: %s", user)
        return user

    def delete(self, user: User) -> None:
        """
        Delete a user from the database.

        Parameters
        ----------
        user : User
            The User object to delete.
        """
        db.session.delete(user)
        db.session.commit()
        logger.debug("Deleted user id=%d", user.id)
