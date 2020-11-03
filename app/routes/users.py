from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user

from app.models import User
from app.forms import ProfileEditForm, PasswordChangeForm
from app import db

bp = Blueprint('users', __name__, url_prefix="/user")

@bp.route('/__all')
def allUsers():
    users = User.query.all()
    return render_template('users/allUsers.html', title="All Users", users = users)

@bp.route('/<username>/profile')
def userProfile(username):
    #get the user if it exists
    user = User.query.filter_by(username=username).first_or_404()
    
    #verify current user has permission to view this profile
    if current_user.hasPermissionToViewUser(user):
        return render_template('users/userProfile.html', title="User Profile", user = user)
    else:
        return render_template('users/unauthorizedProfileView.html', title="Unauthorized Profile View", user=user)

@bp.route('/profile/edit/editProfile', methods=["GET","POST"])
@login_required
def editUserProfile():
    profileEditForm = ProfileEditForm()
    passwordChangeForm = PasswordChangeForm()

    if profileEditForm.validate_on_submit():
        print("DING")
        print(profileEditForm.submitProfileEdit.data)
        print(passwordChangeForm.submitPasswordChange.data)
        current_user.profile_desc = profileEditForm.description.data
        current_user.profile_visibility = profileEditForm.profileVisibility.data
        db.session().commit()
        flash("Changes saved")

    elif request.method == "GET":
        profileEditForm.description.data = current_user.profile_desc
        profileEditForm.profileVisibility.data = current_user.profile_visibility

    return render_template('users/userProfileEdit.html', title="User Profile Edit", profileEditForm=profileEditForm, passwordChangeForm=passwordChangeForm)

@bp.route('/profile/edit/changePassword', methods=["GET","POST"])
@login_required
def changePassword():
    print("DING, Changing Password")
    profileEditForm = ProfileEditForm()
    passwordChangeForm = PasswordChangeForm()

    print(passwordChangeForm.is_submitted())
    if passwordChangeForm.validate_on_submit():
        print("DONG")
        #validate password
        flash("Changing Password")
        if not current_user.check_password(passwordChangeForm.oldPassword.data):
            flash("Invalid password.")
        else:
            current_user.set_password(passwordChangeForm.newPassword.data)
            db.session().commit()
            flash("Password changed")
    elif request.method == "GET":
        print("DING, GET")
        profileEditForm.description.data = current_user.profile_desc
        profileEditForm.profileVisibility.data = current_user.profile_visibility

    return render_template('users/userProfileEdit.html', title="User Profile Edit", profileEditForm=profileEditForm, passwordChangeForm=passwordChangeForm)