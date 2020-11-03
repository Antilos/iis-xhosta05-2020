from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user

from app.models import User, Group, Thread, Post
from app import db
from app.forms import CreateGroupForm

bp = Blueprint('groups', __name__, url_prefix="/groups")

@bp.route('/showMyGroups')
def showJoinedGroups():
    groups = current_user.joined_groups.all() + current_user.owned_groups.all()
    return render_template("groups/joinedGroups.html", title="My Groups", groups=groups)

@bp.route('/createGroup', methods=["GET","POST"])
def createGroup():
    form = CreateGroupForm()

    if form.validate_on_submit():
        group = Group(
            name=form.name.data,
            description=form.description.data,
            visibility=form.groupVisibility.data,
            join_permission = form.joinPermission.data,
            owner=current_user
        )

        db.session.add(group)
        db.session.commit()
        flash("Group created!") #prob won't be seen
        return redirect(url_for('groups.showGroup', groupName=group.name))

    return render_template("groups/createGroup.html", title="Create new group", form=form)

@bp.route('/<groupName>')
def showGroup(groupName):
    #get the group if it exists
    group = Group.query.filter_by(name=groupName).first_or_404()

    #verify current user has permission to view this profile
    print(group.visibility)
    if current_user.hasPermissionToViewGroup(group):
        return render_template("groups/showGroup.html", title=groupName, group=group, threads=group.threads.all())
    else:
        return render_template('groups/unauthorizedGroupView.html', title="Unauthorized Group View", group=group)