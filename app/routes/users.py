from flask import Blueprint, render_template
from app.models import User

bp = Blueprint('users', __name__, url_prefix="/users")

@bp.route('/__all')
def allUsers():
    users = User.query.all()
    return render_template('users/allUsers.html', title="All Users", users = users)

@bp.route('/profile/<username>')
def userProfile(username):
    user = User.query.filter_by(username=username).first()
    return render_template('users/userProfile.html', title="User Profile", user = user)

