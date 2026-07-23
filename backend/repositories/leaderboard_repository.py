"""
Leaderboard Repository
=======================

All database operations for weekly leaderboard data.
Called only by LeaderboardService — never directly by controllers.

Methods
-------
- upsert_user_score(user_id, week_start, log_entry)  — update weekly totals when a log is saved
- get_weekly_leaderboard(week_start, limit)           — top N users for a given week
- get_friends_leaderboard(user_id, week_start)        — leaderboard restricted to friends
- get_user_weekly_entry(user_id, week_start)          — one user's stats for a week
- get_user_rank(user_id, week_start)                  — user's position in the global leaderboard

Week Identifier
---------------
Always use the Monday date of the ISO week as `week_start`.
Use LeaderboardRepository.current_week_start() to get it automatically.
"""

import logging
from datetime import date, timedelta
from typing import Optional

from backend.extensions import db
from backend.models.leaderboard import LeaderboardEntry
from backend.models.user import User

logger = logging.getLogger(__name__)


class LeaderboardRepository:
    """Data-access layer for leaderboard entries."""

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    @staticmethod
    def current_week_start() -> date:
        """
        Return the Monday of the current ISO week.

        Example: if today is Wednesday 2024-01-10, returns 2024-01-08.
        """
        today = date.today()
        return today - timedelta(days=today.weekday())  # weekday(): Mon=0, Sun=6

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    @staticmethod
    def upsert_user_score(
        user_id: int,
        week_start: date,
        calories: float,
        protein_g: float,
        carbs_g: float,
        fat_g: float,
    ) -> LeaderboardEntry:
        """
        Add one food log's nutritional values to the user's weekly total.

        If no entry exists for this (user_id, week_start), creates one.
        If it already exists, increments the running totals.

        This is called automatically every time a FoodLog is saved.

        Parameters
        ----------
        user_id    : The user who logged the meal.
        week_start : The Monday of the week (use current_week_start()).
        calories   : Calories in the logged meal.
        protein_g  : Protein in grams.
        carbs_g    : Carbohydrates in grams.
        fat_g      : Fat in grams.
        """
        entry = LeaderboardEntry.query.filter_by(
            user_id=user_id,
            week_start=week_start,
        ).first()

        if entry:
            # Increment existing totals
            entry.total_logs += 1
            entry.total_calories += calories
            entry.total_protein_g += protein_g
            entry.total_carbs_g += carbs_g
            entry.total_fat_g += fat_g
        else:
            # Create a new entry for this week
            entry = LeaderboardEntry(
                user_id=user_id,
                week_start=week_start,
                total_logs=1,
                total_calories=calories,
                total_protein_g=protein_g,
                total_carbs_g=carbs_g,
                total_fat_g=fat_g,
            )
            db.session.add(entry)

        db.session.commit()
        logger.debug(
            "Leaderboard updated: user=%d week=%s logs=%d",
            user_id, week_start, entry.total_logs,
        )
        return entry

    # ------------------------------------------------------------------
    # Read operations
    # ------------------------------------------------------------------

    @staticmethod
    def get_weekly_leaderboard(
        week_start: date,
        limit: int = 50,
    ) -> list[dict]:
        """
        Return the top `limit` users for the given week, ranked by
        total_logs DESC, then total_calories ASC (tiebreaker).

        Returns a list of dicts with user info + rank included.

        Parameters
        ----------
        week_start : The Monday of the desired week.
        limit      : Maximum number of entries to return. Default: 50.
        """
        entries = (
            db.session.query(LeaderboardEntry, User)
            .join(User, User.id == LeaderboardEntry.user_id)
            .filter(LeaderboardEntry.week_start == week_start)
            .order_by(
                LeaderboardEntry.total_logs.desc(),
                LeaderboardEntry.total_calories.asc(),
            )
            .limit(limit)
            .all()
        )

        result = []
        for rank, (entry, user) in enumerate(entries, start=1):
            result.append({
                "rank": rank,
                "user_id": user.id,
                "username": user.username,
                "avatar_url": user.avatar_url,
                "total_logs": entry.total_logs,
                "total_calories": round(entry.total_calories, 1),
                "total_protein_g": round(entry.total_protein_g, 1),
                "week_start": entry.week_start.isoformat(),
            })

        return result

    @staticmethod
    def get_friends_leaderboard(
        user_id: int,
        week_start: date,
    ) -> list[dict]:
        """
        Return the leaderboard restricted to the user's accepted friends
        (plus the user themselves), ranked as in get_weekly_leaderboard.

        Parameters
        ----------
        user_id    : The current user — their friends define the scope.
        week_start : The Monday of the desired week.
        """
        from backend.models.friendship import Friendship, FriendshipStatus

        # Get IDs of all accepted friends
        sent_ids = (
            db.session.query(Friendship.addressee_id)
            .filter(
                Friendship.requester_id == user_id,
                Friendship.status == FriendshipStatus.ACCEPTED,
            )
        )
        received_ids = (
            db.session.query(Friendship.requester_id)
            .filter(
                Friendship.addressee_id == user_id,
                Friendship.status == FriendshipStatus.ACCEPTED,
            )
        )

        # Combine friend IDs + the user themselves
        friend_ids_subq = sent_ids.union(received_ids).subquery()

        entries = (
            db.session.query(LeaderboardEntry, User)
            .join(User, User.id == LeaderboardEntry.user_id)
            .filter(
                LeaderboardEntry.week_start == week_start,
                db.or_(
                    LeaderboardEntry.user_id == user_id,
                    LeaderboardEntry.user_id.in_(friend_ids_subq),
                ),
            )
            .order_by(
                LeaderboardEntry.total_logs.desc(),
                LeaderboardEntry.total_calories.asc(),
            )
            .all()
        )

        result = []
        for rank, (entry, user) in enumerate(entries, start=1):
            result.append({
                "rank": rank,
                "user_id": user.id,
                "username": user.username,
                "avatar_url": user.avatar_url,
                "total_logs": entry.total_logs,
                "total_calories": round(entry.total_calories, 1),
                "is_self": (user.id == user_id),
                "week_start": entry.week_start.isoformat(),
            })

        return result

    @staticmethod
    def get_user_weekly_entry(user_id: int, week_start: date) -> Optional[LeaderboardEntry]:
        """Return a user's LeaderboardEntry for a specific week, or None."""
        return LeaderboardEntry.query.filter_by(
            user_id=user_id,
            week_start=week_start,
        ).first()

    @staticmethod
    def get_user_rank(user_id: int, week_start: date) -> Optional[int]:
        """
        Return the user's rank (1-based) in the global leaderboard for a week.
        Returns None if the user has no entry for that week.
        """
        # Count how many users have MORE logs than this user (or same logs + lower calories)
        entry = LeaderboardRepository.get_user_weekly_entry(user_id, week_start)
        if not entry:
            return None

        rank = (
            db.session.query(LeaderboardEntry)
            .filter(
                LeaderboardEntry.week_start == week_start,
                db.or_(
                    LeaderboardEntry.total_logs > entry.total_logs,
                    db.and_(
                        LeaderboardEntry.total_logs == entry.total_logs,
                        LeaderboardEntry.total_calories < entry.total_calories,
                    ),
                ),
            )
            .count()
        )
        return rank + 1  # +1 because rank is 1-based
