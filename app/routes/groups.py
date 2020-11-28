from flask import Blueprint, render_template, request, flash, redirect, url_for, Response
from flask_login import login_required, current_user
import click
import logging

from app.models import User, Group, Thread, Post, Group_Join_Request, Group_Moderator_Promotion_Request, Tag
from app import db
from app.forms import CreateGroupForm
from app.enums import JoinPermission, RequestStatus

bp = Blueprint('groups', __name__, url_prefix="/groups")

@bp.route('/showMyGroups')
@login_required
def showJoinedGroups():
    groups = current_user.joined_groups.all() + current_user.owned_groups.all()
    return render_template("groups/joinedGroups.html", title="My Groups", groups=groups)

@bp.route('/allGroups')
def showAllGroups():
    groups = Group.query.all()
    return render_template("groups/showAllGroups.html", title="All Groups", groups=groups)

@bp.route('/createGroup', methods=["GET","POST"])
@login_required
def createGroup():
    form = CreateGroupForm()

    if form.validate_on_submit():

        #create group
        group = Group(
            name=form.name.data,
            description=form.description.data,
            visibility=form.groupVisibility.data,
            isOpen = form.isOpen.data,
            owner=current_user
        )

        #add current user as member
        group.addMember(current_user)

        #add tags
        tagTokens = form.tags.data.split(sep=",")
        for tagToken in tagTokens:
            group.addTag(tagToken)

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
    if group.isPublic or (current_user.is_authenticated and current_user.hasPermissionToViewGroup(group)): #!short circuit!
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
        group.createJoinRequest(user=current_user)
        db.session.commit()
        flash(f"Your request to join group {groupName} was registered. It must be approved by a moderator.")

    return redirect(url_for('groups.showGroup', groupName=groupName))

@bp.route('/<groupName>/joinRequests')
@login_required
def showPendingJoinRequests(groupName):
    #get group
    group = Group.query.filter_by(name=groupName).first_or_404()

    #get requests
    requests = group.join_requests.filter_by(status=RequestStatus.UNPROCESSED)

    return render_template('groups/showPendingJoinRequests.html', requests=requests)

@bp.route('/<groupName>/requestPromotionToModerator')
@login_required
def requestPromotionToModerator(groupName):
    #get group
    group = Group.query.filter_by(name=groupName).first_or_404()

    #create promote request
    group.createModeratorPromotionRequest(user = current_user)
    flash("Requested promotion to moderator.")
    db.session.commit()
    return redirect(url_for('groups.showGroup', groupName=groupName))

@bp.route('/<groupName>/promotionRequests')
@login_required
def showPendingModeratorPromotionRequests(groupName):
    #get group
    group = Group.query.filter_by(name=groupName).first_or_404()

    #get requests
    requests = group.moderator_promotion_requests.filter_by(status=RequestStatus.UNPROCESSED)

    return render_template('groups/showPendingModeratorPromotionRequests.html', requests=requests)

@bp.route('/<groupId>/approveJoinRequest/<requestId>')
@login_required
def approveJoinRequest(groupId, requestId):
    #get group
    group = Group.query.filter_by(id=groupId).first_or_404()

    #get request
    request = group.join_requests.filter_by(id=requestId).first_or_404()

    #verify current user has permission to handle requests
    if group.isModerator(current_user):
        request.approve()
        db.session.commit()
        return redirect(url_for('groups.showPendingJoinRequests', groupName=group.name))
    else:
        return Response(status=403)

@bp.route('/<groupId>/denyJoinRequest/<requestId>')
@login_required
def denyJoinRequest(groupId, requestId):
    #get group
    group = Group.query.filter_by(id=groupId).first_or_404()

    #get request
    request = group.join_requests.filter_by(id=requestId).first_or_404()

    #verify current user has permission to handle requests
    if group.isModerator(current_user):
        request.deny()
        db.session.commit()
        return redirect(url_for('groups.showPendingJoinRequests', groupName=group.name))
    else:
        return Response(status=403)

@bp.route('/<groupId>/approveModeratorPromotionRequest/<requestId>')
@login_required
def approveModeratorPromotionRequest(groupId, requestId):
    #get group
    group = Group.query.filter_by(id=groupId).first_or_404()

    #get request
    request = group.moderator_promotion_requests.filter_by(id=requestId).first_or_404()

    #verify current user has permission to handle requests
    if group.isModerator(current_user):
        request.approve()
        db.session.commit()
        return redirect(url_for('groups.showPendingModeratorPromotionRequests', groupName=group.name))
    else:
        return Response(status=403)

@bp.route('/<groupId>/approveModeratorPromotionRequest/<requestId>')
@login_required
def denyModeratorPromotionRequest(groupId, requestId):
    #get group
    group = Group.query.filter_by(id=groupId).first_or_404()

    #get request
    request = group.moderator_promotion_requests.filter_by(id=requestId).first_or_404()

    #verify current user has permission to handle requests
    if group.isModerator(current_user):
        request.deny()
        db.session.commit()
        return redirect(url_for('groups.showPendingModeratorPromotionRequests', groupName=group.name))
    else:
        return Response(status=403)

### Commands ###
@bp.cli.command("delete-all")
def delete_all():
    Group.query.delete()
    db.session.commit()
    logging.info("Deleted all groups.")

@bp.cli.command("create")
@click.argument('name')
@click.argument('visibility', type=int)
@click.argument('is_open', type=bool)
@click.argument('owner_name')
def create_group(name, visibility, is_open, owner_name):
    group = Group.query.filter_by(name=name).first()
    owner = User.query.filter_by(username=owner_name).first()
    if group:
        logging.error(f"Group {name} already exists.")
    elif not owner:
        logging.error(f"User {owner_name} doesn't exist.")
    else:
        newGroup = Group(
            name=name,
            visibility=visibility,
            description="",
            is_open = is_open,
            owner=owner
        )
        db.session.add(newGroup)
        db.session.commit()
        logging.info(f"Created group {name}")