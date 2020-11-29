import click
import logging
from flask import Blueprint, render_template, request, flash, Response, url_for, redirect
from flask_login import login_required, current_user

from app.models import User, makeUserAdmin, getUsersByVisibility
from app.forms import ProfileEditForm, PasswordChangeForm
from app import db
from app.enums import Visibility

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
        current_user.profile_desc = profileEditForm.description.data
        current_user.profile_visibility = profileEditForm.profileVisibility.data

        #add tags
        tagTokens = profileEditForm.addTags.data.split(sep=",")
        for tagToken in tagTokens:
            current_user.addTag(tagToken.strip())

        #remove tags
        tagTokens = profileEditForm.removeTags.data.split(sep=",")
        for tagToken in tagTokens:
            current_user.removeTag(tagToken.strip())

        db.session().commit()
        flash("Changes saved")

    elif request.method == "GET":
        profileEditForm.description.data = current_user.profile_desc
        profileEditForm.profileVisibility.data = current_user.profile_visibility

    return render_template('users/userProfileEdit.html', title="User Profile Edit", profileEditForm=profileEditForm, passwordChangeForm=passwordChangeForm)

@bp.route('/profile/edit/changePassword', methods=["GET","POST"])
@login_required
def changePassword():
    profileEditForm = ProfileEditForm()
    passwordChangeForm = PasswordChangeForm()

    print(passwordChangeForm.is_submitted())
    if passwordChangeForm.validate_on_submit():
        #validate password
        flash("Changing Password")
        if not current_user.check_password(passwordChangeForm.oldPassword.data):
            flash("Invalid password.")
        else:
            current_user.set_password(passwordChangeForm.newPassword.data)
            db.session().commit()
            flash("Password changed")
    elif request.method == "GET":
        profileEditForm.description.data = current_user.profile_desc
        profileEditForm.profileVisibility.data = current_user.profile_visibility

    return render_template('users/userProfileEdit.html', title="User Profile Edit", profileEditForm=profileEditForm, passwordChangeForm=passwordChangeForm)

@bp.route('all')
def showUsers():
    if current_user.is_anonymous:
        users = getUsersByVisibility(Visibility.PUBLIC)
    else:
        users = User.query.all()

    return render_template('users/showUsers.html', title='Users', users=users)

@bp.route('<username>/AdminDelete')
def adminDeleteUser(username):
    if current_user.isAdmin():
        userQuery = User.query.filter_by(username=username)
        user = User.query.filter_by(username=username).first_or_404()
        userQuery.delete()
        db.session.commit()
        logging.info(f"Deleted user {username}.")
        return redirect(url_for('index'))
    else:
        return Response(status=403)

###commands###
@bp.cli.command("delete-all")
def delete_all():
    User.query.delete()
    db.session.commit()
    logging.info("Deleted all users.")

@bp.cli.command("promote-to-admin")
@click.argument('username')
def promote_to_admin(username):
    user = User.query.filter_by(username=username).first()
    if user:
        if makeUserAdmin(user):
            logging.info(f"User {username} is now admin.")
            db.session.commit()
        else:
            logging.warning(f"User {username} is already admin.")
    else:
        logging.error(f"User {username} doesn't exist.")

@bp.cli.command("info")
@click.argument('username')
def get_user_info(username):
    user = User.query.filter_by(username=username).first()
    if user:
        logging.info(f"<User {username}| is_admin={user.is_admin}>")
    else:
         logging.error(f"User {username} doesn't exist.")

@bp.cli.command("create")
@click.argument('username')
@click.argument('password')
@click.argument('profile_visibility', type=int)
def create_user(username, password, profile_visibility):
    user = User.query.filter_by(username=username).first()
    if user:
        logging.error(f"User {username} already exists.")
    else:
        newUser = User(
            username=username,
            profile_desc="",
            profile_visibility=profile_visibility
        )
        newUser.set_password(password)
        db.session.add(newUser)
        db.session.commit()
        logging.info(f"Created user {username}")