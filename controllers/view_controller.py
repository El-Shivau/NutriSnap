from flask import Blueprint, render_template

view_bp = Blueprint('view', __name__)

@view_bp.route('/')
def landing():
    return render_template('landing.html')

@view_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@view_bp.route('/scan')
def scan_page():
    return render_template('scan.html')

@view_bp.route('/feed')
def feed_page():
    return render_template('feed.html')

@view_bp.route('/leaderboard')
def leaderboard_page():
    return render_template('leaderboard.html')

@view_bp.route('/friends')
def friends_page():
    return render_template('friends.html')

@view_bp.route('/friends/<int:friend_id>')
def friend_analytics_page(friend_id):
    return render_template('friend_analytics.html')

@view_bp.route('/profile')
def profile_page():
    return render_template('profile.html')

@view_bp.route('/login')
def login_page():
    return render_template('login.html')

@view_bp.route('/register')
def register_page():
    return render_template('register.html')
