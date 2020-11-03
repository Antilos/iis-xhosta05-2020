from flask import Blueprint, render_template, request, flash, redirect, url_for, Response
from flask_login import login_required, current_user

from app.models import User, Group, Thread, Post, Group_Join_Request
from app import db
from app.forms import CreateGroupForm
from app.enums import JoinPermission

bp = Blueprint('groups', __name__, url_prefix="/groups")

@bp.route('/showMyGroups')
@login_required
def showJoinedGroups():
    groups = current_user.joined_groups.all() + current_user.owned_groups.all()
    return render_template("groups/joinedGroups.html", title="My Groups", groups=groups)

@bp.route('/createGroup', methods=["GET","POST"])
@login_required
def createGroup():
    form = CreateGroupForm()

    if form.validate_on_submit():
        group = Group(
            name=form.name.data,
            description=form.description.data,
            visibility=form.groupVisibility.data,
            isOpen = form.isOpen.data,
            owner=current_user
        )

        group.addMember(current_user)

        db.session.add(group)
        db.session.commit()
        flash("Group created!") #prob won't be seen
        return redirect(url_for('groups.showGroup', groupName=group.name))

    return render_template("groups/createGroup.html", title="Create new group", form=form)

@bp.route('/<groupName>')
def showGroup(groupName):
    #get the group if it exists
    group = Group.query.filter_by(name=groupName).first_or_404()

    threadsPerPage = 2
    page = request.args.get('page', 1, type=int)

    #verify current user has permission to view this group
    if current_user.hasPermissionToViewGroup(group):
        threads = group.getThreadsChronological().paginate(page, threadsPerPage, False)
        nextUrl = url_for('groups.showGroup', groupName=groupName, page=threads.next_num) if threads.has_next else None
        prevUrl = url_for('groups.showGroup', groupName=groupName, page=threads.prev_num) if threads.has_prev else None

        return render_template("groups/showGroup.html", title=groupName, group=group, threads=threads.items)
    else:
        return render_template('groups/unauthorizedGroupView.html', title="Unauthorized Group View", group=group)

@bp.route('/<groupName>/members')
def showMembers(groupName):
    #get the group if it exists
    group = Group.query.filter_by(name=groupName).first_or_404()

    membersPerPage = 2
    page = request.args.get('page', 1, type=int)

    #verify current user has permission to view this group
    if current_user.hasPermissionToViewGroup(group):
        #TODO
        print(group.members.all())
        members = group.members.paginate(page, membersPerPage, False)
        print(members.items)
        nextUrl = url_for('groups.showMembers', groupName=groupName, page=members.next_num) if members.has_next else None
        prevUrl = url_for('groups.showMembers', groupName=groupName, page=members.prev_num) if members.has_prev else None
        return render_template("groups/showMembers.html", title=f"Members of {groupName}", members=members.items, group=group)
    else:
        return render_template('groups/unauthorizedGroupView.html', title="Unauthorized Group View", group=group)

@bp.route('/<groupName>/join')
@login_required
def joinGroup(groupName):
    #get the group if it exists
    group = Group.query.filter_by(name=groupName).first_or_404()

    if group.isOpen():
        group.addMember(current_user)
        db.session.commit()
    else:
        # create join request
        joinRequest = Group_Join_Request(user = current_user, group = group)

        db.session.add(joinRequest)
        db.session.commit()
        flash(f"Your request to join group {groupName} was registered. It must be approved by a moderator.")

    return redirect(url_for('groups.showGroup', groupName=groupName))

@bp.route('/<groupName>/joinRequests')
@login_required
def showJoinRequests(groupName):
    return Response(status=501)

@bp.route('/<groupName>/joinRequests')
@login_required
def requestPromotionToModerator(groupName):
    return Response(status=501)

@bp.route('/<groupName>/joinRequests')
@login_required
def showModeratorPromotionRequests(groupName):
    return Response(status=501)