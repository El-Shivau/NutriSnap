"""
Leaderboard Controller
=======================

Routes:
  GET /leaderboard          → Leaderboard page (global, filterable by period)
  GET /leaderboard/friends  → Friends-only leaderboard

Query params:
  ?period=today | week | month   (default: week)
  ?scope=global | friends        (default: global)
"""

import logging
from datetime import date, datetime, timedelta, timezone

from flask import Blueprint, render_template, request
from flask_login import current_user, login_required

from backend.extensions import db
from backend.models.food_log import FoodLog
from backend.models.friendship import Friendship, FriendshipStatus
from backend.models.user import User

logger = logging.getLogger(__name__)

leaderboard_bp = Blueprint("leaderboard", __name__, url_prefix="/leaderboard")


def _period_bounds(period: str) -> tuple[datetime, datetime]:
    """Return UTC (start, end) datetimes for the requested period."""
    now = datetime.now(timezone.utc)
    if period == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "month":
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    else:  # week (default)
        days_since_monday = now.weekday()
        start = (now - timedelta(days=days_since_monday)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
    return start, now


def _build_leaderboard(period: str, user_ids: list[int] | None = None) -> list[dict]:
    """
    Aggregate food_logs for the period and return a ranked list.

    Parameters
    ----------
    period   : 'today' | 'week' | 'month'
    user_ids : If given, restrict to these user IDs (friends scope).
               If None, include all users (global scope).
    """
    start, end = _period_bounds(period)

    query = (
        db.session.query(
            User.id.label("user_id"),
            User.username.label("username"),
            User.avatar_url.label("avatar_url"),
            db.func.count(FoodLog.id).label("total_logs"),
            db.func.coalesce(db.func.sum(FoodLog.calories), 0).label("total_calories"),
            db.func.coalesce(db.func.sum(FoodLog.protein_g), 0).label("total_protein_g"),
            db.func.coalesce(db.func.sum(FoodLog.carbs_g), 0).label("total_carbs_g"),
            db.func.coalesce(db.func.sum(FoodLog.fat_g), 0).label("total_fat_g"),
        )
        .join(FoodLog, FoodLog.user_id == User.id)
        .filter(
            FoodLog.logged_at >= start,
            FoodLog.logged_at <= end,
        )
    )

    if user_ids is not None:
        query = query.filter(User.id.in_(user_ids))

    rows = (
        query.group_by(User.id, User.username, User.avatar_url)
        .order_by(
            db.func.count(FoodLog.id).desc(),
            db.func.coalesce(db.func.sum(FoodLog.calories), 0).asc(),
        )
        .limit(50)
        .all()
    )

    result = []
    for rank, row in enumerate(rows, start=1):
        result.append({
            "rank": rank,
            "user_id": row.user_id,
            "username": row.username,
            "avatar_url": row.avatar_url,
            "total_logs": row.total_logs,
            "total_calories": round(float(row.total_calories), 1),
            "total_protein_g": round(float(row.total_protein_g), 1),
            "is_self": row.user_id == current_user.id,
        })
    return result


def _friend_ids(user_id: int) -> list[int]:
    """Return IDs of accepted friends + the user themselves."""
    sent = (
        db.session.query(Friendship.addressee_id)
        .filter(
            Friendship.requester_id == user_id,
            Friendship.status == FriendshipStatus.ACCEPTED,
        )
    )
    received = (
        db.session.query(Friendship.requester_id)
        .filter(
            Friendship.addressee_id == user_id,
            Friendship.status == FriendshipStatus.ACCEPTED,
        )
    )
    ids = {row[0] for row in sent.union(received).all()}
    ids.add(user_id)
    return list(ids)


@leaderboard_bp.route("/")
@login_required
def leaderboard():
    """Leaderboard page — global or friends, filterable by period."""
    period = request.args.get("period", "week")
    scope = request.args.get("scope", "global")

    if period not in ("today", "week", "month"):
        period = "week"
    if scope not in ("global", "friends"):
        scope = "global"

    if scope == "friends":
        allowed_ids = _friend_ids(current_user.id)
        entries = _build_leaderboard(period, user_ids=allowed_ids)
    else:
        entries = _build_leaderboard(period, user_ids=None)

    # Find the current user's own entry for the "your rank" badge
    my_entry = next((e for e in entries if e["is_self"]), None)

    period_labels = {"today": "Today", "week": "This Week", "month": "This Month"}

    return render_template(
        "leaderboard/leaderboard.html",
        title="Leaderboard",
        entries=entries,
        period=period,
        scope=scope,
        period_label=period_labels.get(period, "This Week"),
        my_entry=my_entry,
    )
