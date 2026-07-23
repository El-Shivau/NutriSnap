"""
Leaderboard Model
==================

Stores weekly nutrition leaderboard snapshots for all users.

Table: leaderboard_entries
---------------------------
Each row is one user's stats for one specific week.
The week is identified by its Monday date (week_start).

How it works
------------
1. A scheduled job (or triggered on each food log) calls
   LeaderboardRepository.update_user_score() to upsert the weekly row.
2. The leaderboard page queries all rows for the current week,
   ordered by total_logs DESC (or total_calories — configurable).
3. Ranks are computed at query time, not stored (avoids stale data).

Scoring Rules (Phase 6 — configurable)
----------------------------------------
- Primary sort: total_logs DESC  (who logged the most meals this week)
- Secondary sort: total_calories ASC (lower calories = healthier = tiebreaker)
"""

from datetime import datetime, timezone

from backend.extensions import db


class LeaderboardEntry(db.Model):
    """
    One user's leaderboard stats for one week.

    Unique constraint: one row per (user_id, week_start) pair.
    """

    __tablename__ = "leaderboard_entries"

    __table_args__ = (
        db.UniqueConstraint("user_id", "week_start", name="uq_leaderboard_user_week"),
    )

    # Primary key
    id: int = db.Column(db.Integer, primary_key=True)

    # Owner
    user_id: int = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Week identifier — always the Monday of the relevant ISO week
    # Example: 2024-01-08 is the week of Jan 8–14 2024
    week_start: datetime = db.Column(
        db.Date,
        nullable=False,
        index=True,
    )

    # Aggregated stats for the week
    total_logs: int = db.Column(db.Integer, nullable=False, default=0)
    total_calories: float = db.Column(db.Float, nullable=False, default=0.0)
    total_protein_g: float = db.Column(db.Float, nullable=False, default=0.0)
    total_carbs_g: float = db.Column(db.Float, nullable=False, default=0.0)
    total_fat_g: float = db.Column(db.Float, nullable=False, default=0.0)

    # When this row was last updated
    updated_at: datetime = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationship back to the User object
    user = db.relationship(
        "User",
        backref=db.backref("leaderboard_entries", lazy="dynamic", cascade="all, delete-orphan"),
    )

    def __repr__(self) -> str:
        return (
            f"<LeaderboardEntry user={self.user_id} "
            f"week={self.week_start} logs={self.total_logs}>"
        )

    def to_dict(self) -> dict:
        """Serialise the leaderboard entry to a dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "week_start": self.week_start.isoformat(),
            "total_logs": self.total_logs,
            "total_calories": round(self.total_calories, 1),
            "total_protein_g": round(self.total_protein_g, 1),
            "total_carbs_g": round(self.total_carbs_g, 1),
            "total_fat_g": round(self.total_fat_g, 1),
            "updated_at": self.updated_at.isoformat(),
        }
