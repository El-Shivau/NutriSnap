"""
FoodLog Repository
==================

Handles all database access for the FoodLog model.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from backend.extensions import db
from backend.models.food_log import FoodLog

logger = logging.getLogger(__name__)


class FoodLogRepository:
    """Data access object for FoodLog model operations."""

    def find_by_id(self, log_id: int) -> Optional[FoodLog]:
        """Return a single FoodLog entry by primary key."""
        return db.session.get(FoodLog, log_id)

    def find_by_user(
        self,
        user_id: int,
        limit: int = 50,
        offset: int = 0,
    ) -> list[FoodLog]:
        """
        Return paginated food log entries for a specific user,
        ordered by most recent first.

        Parameters
        ----------
        user_id : int
            The user whose logs to retrieve.
        limit : int
            Maximum number of entries to return.
        offset : int
            Number of entries to skip (for pagination).

        Returns
        -------
        list[FoodLog]
        """
        return (
            FoodLog.query.filter_by(user_id=user_id)
            .order_by(FoodLog.logged_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

    def find_today(self, user_id: int) -> list[FoodLog]:
        """
        Return all food log entries created today (UTC) for a user.
        Used by the dashboard to compute today's nutritional totals.

        Parameters
        ----------
        user_id : int

        Returns
        -------
        list[FoodLog]
        """
        today_start = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        return (
            FoodLog.query.filter(
                FoodLog.user_id == user_id,
                FoodLog.logged_at >= today_start,
            )
            .order_by(FoodLog.logged_at.desc())
            .all()
        )

    def save(self, food_log: FoodLog) -> FoodLog:
        """Persist a new or updated FoodLog entry."""
        db.session.add(food_log)
        db.session.commit()
        logger.debug("Saved food log: %s", food_log)
        return food_log

    def delete(self, food_log: FoodLog) -> None:
        """Delete a FoodLog entry."""
        db.session.delete(food_log)
        db.session.commit()
        logger.debug("Deleted food log id=%d", food_log.id)
