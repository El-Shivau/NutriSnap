"""
Friends Controller
==================

Routes:
  GET  /friends                 → Friends list + pending requests
  GET  /friends/search          → Search users by username
  POST /friends/request/<id>    → Send a friend request
  POST /friends/accept/<id>     → Accept incoming request (id = requester_id)
  POST /friends/decline/<id>    → Decline incoming request (id = requester_id)
  POST /friends/cancel/<id>     → Cancel sent request (id = addressee_id)
  POST /friends/unfriend/<id>   → Remove accepted friend

Security: all writes are validated against current_user.id — you cannot
accept/decline/unfriend on behalf of another user.
"""

import logging

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from backend.extensions import db
from backend.models.friendship import Friendship, FriendshipStatus
from backend.models.user import User
from backend.repositories.friendship_repository import FriendshipRepository

logger = logging.getLogger(__name__)

friends_bp = Blueprint("friends", __name__, url_prefix="/friends")
_repo = FriendshipRepository()


def _get_user_or_404(user_id: int) -> User:
    user = db.session.get(User, user_id)
    if not user or not user.is_active:
        from flask import abort
        abort(404)
    return user


@friends_bp.route("/")
@login_required
def friends_list():
    """Friends dashboard — shows accepted friends, pending requests in/out."""
    friends = FriendshipRepository.get_friends(current_user.id)
    received = FriendshipRepository.get_pending_received(current_user.id)
    sent = FriendshipRepository.get_pending_sent(current_user.id)

    # Enrich pending received with requester User objects
    received_with_users = [
        {"friendship": f, "user": db.session.get(User, f.requester_id)}
        for f in received
    ]
    # Enrich pending sent with addressee User objects
    sent_with_users = [
        {"friendship": f, "user": db.session.get(User, f.addressee_id)}
        for f in sent
    ]

    return render_template(
        "friends/friends.html",
        title="Friends",
        friends=friends,
        received=received_with_users,
        sent=sent_with_users,
        pending_count=len(received),
    )


@friends_bp.route("/search")
@login_required
def search():
    """Search for users by username. Returns partial results via same template."""
    query = request.args.get("q", "").strip()
    results = []

    if query and len(query) >= 2:
        users = (
            User.query
            .filter(
                User.username.ilike(f"%{query}%"),
                User.id != current_user.id,
                User.is_active == True,
            )
            .limit(20)
            .all()
        )

        for user in users:
            friendship = FriendshipRepository.get_friendship(current_user.id, user.id)
            status = friendship.status.value if friendship else None
            is_requester = friendship.requester_id == current_user.id if friendship else None
            results.append({
                "user": user,
                "status": status,
                "is_requester": is_requester,
                "friendship_id": friendship.id if friendship else None,
            })

    return render_template(
        "friends/search.html",
        title="Find Friends",
        query=query,
        results=results,
    )


@friends_bp.route("/request/<int:addressee_id>", methods=["POST"])
@login_required
def send_request(addressee_id: int):
    """Send a friend request to another user."""
    _get_user_or_404(addressee_id)

    if addressee_id == current_user.id:
        flash("You cannot send a friend request to yourself.", "warning")
        return redirect(request.referrer or url_for("friends.friends_list"))

    try:
        FriendshipRepository.send_request(current_user.id, addressee_id)
        flash("Friend request sent!", "success")
    except ValueError as e:
        flash(str(e), "warning")

    return redirect(request.referrer or url_for("friends.friends_list"))


@friends_bp.route("/accept/<int:requester_id>", methods=["POST"])
@login_required
def accept_request(requester_id: int):
    """Accept an incoming friend request. Only the addressee may call this."""
    try:
        FriendshipRepository.accept_request(requester_id, current_user.id)
        user = db.session.get(User, requester_id)
        flash(f"You and {user.username} are now friends!", "success")
    except ValueError as e:
        flash(str(e), "warning")

    return redirect(url_for("friends.friends_list"))


@friends_bp.route("/decline/<int:requester_id>", methods=["POST"])
@login_required
def decline_request(requester_id: int):
    """Decline an incoming friend request. Only the addressee may call this."""
    # Security: verify this request was actually sent TO the current user
    friendship = Friendship.query.filter_by(
        requester_id=requester_id,
        addressee_id=current_user.id,
        status=FriendshipStatus.PENDING,
    ).first()

    if not friendship:
        flash("Friend request not found.", "warning")
        return redirect(url_for("friends.friends_list"))

    db.session.delete(friendship)
    db.session.commit()
    flash("Friend request declined.", "info")
    return redirect(url_for("friends.friends_list"))


@friends_bp.route("/cancel/<int:addressee_id>", methods=["POST"])
@login_required
def cancel_request(addressee_id: int):
    """Cancel an outgoing friend request. Only the requester may call this."""
    # Security: verify this request was actually sent BY the current user
    friendship = Friendship.query.filter_by(
        requester_id=current_user.id,
        addressee_id=addressee_id,
        status=FriendshipStatus.PENDING,
    ).first()

    if not friendship:
        flash("Request not found.", "warning")
        return redirect(url_for("friends.friends_list"))

    db.session.delete(friendship)
    db.session.commit()
    flash("Friend request cancelled.", "info")
    return redirect(request.referrer or url_for("friends.friends_list"))


@friends_bp.route("/unfriend/<int:friend_id>", methods=["POST"])
@login_required
def unfriend(friend_id: int):
    """Remove an accepted friend."""
    removed = FriendshipRepository.unfriend(current_user.id, friend_id)
    if removed:
        flash("Friend removed.", "info")
    else:
        flash("Friendship not found.", "warning")
    return redirect(url_for("friends.friends_list"))
