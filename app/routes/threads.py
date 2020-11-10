from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
import click
import logging

from app.models import User, Group, Thread, Post
from app import db
from app.forms import CreateThreadForm, CreatePostForm

bp = Blueprint('threads', __name__, url_prefix="/threads")

@bp.route("/showThread/<threadId>")
def showThread(threadId):
    postsPerPage = 2
    page = request.args.get('page', 1, type=int)
    
    thread = Thread.query.filter_by(id=threadId).first()

    #verify current user has permission to view this profile
    if current_user.hasPermissionToViewGroup(thread.group):
        posts = thread.getPostsChronological().paginate(page, postsPerPage, False)
        nextUrl = url_for('threads.showThread', threadId=threadId, page=posts.next_num) if posts.has_next else None
        prevUrl = url_for('threads.showThread', threadId=threadId, page=posts.prev_num) if posts.has_prev else None

        return render_template("threads/showThread.html", title=f"{thread.group.name}|{thread.subject}", thread=thread, posts=posts.items, nextUrl=nextUrl, prevUrl=prevUrl, createPostForm=CreatePostForm())
    else:
        return render_template('groups/unauthorizedGroupView.html', title="Unauthorized Group View", group=thread.group)

@bp.route("/<groupName>/createThread", methods=["GET","POST"])
def createThread(groupName):
    form = CreateThreadForm()

    if form.validate_on_submit():
        #get current group
        group = Group.query.filter_by(name=groupName).first()

        # Create new thread
        thread = Thread(
            subject = form.subject.data,
            description = form.description.data,
            opener = current_user,
            group = group
        )

        db.session.add(thread)
        db.session.commit()
        flash("Thread created!") #prob won't be seen
        return redirect(url_for('threads.showThread', threadId=thread.id))

    return render_template("threads/createThread.html", title="Create new thread", form=form)

### Commands ###
@bp.cli.command("delete-all")
def delete_all():
    Thread.query.delete()
    db.session.commit()
    logging.info("Deleted all threads.")

@bp.cli.command("create")
@click.argument('subject')
@click.argument('opener_name')
@click.argument('group_name')
def create_thread(subject, opener_name, group_name):
    thread = Thread.query.filter_by(subject=subject).first()
    group = Group.query.filter_by(name=group_name).first()
    opener = User.query.filter_by(username=opener_name).first()
    if thread:
        logging.error(f"Thread {subject} already exists.")
    elif not group:
        logging.error(f"Group {group_name} doesn't exist.")
    elif not opener:
        logging.error(f"User {opener_name} doesn't exist.")
    else:
        newThread = Thread(
            subject=subject,description="",group=group,opener=opener
        )
        db.session.add(newThread)
        db.session.commit()
        logging.info(f"Created thread {subject}")