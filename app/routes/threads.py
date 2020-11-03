from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user

from app.models import User, Group, Thread, Post
from app import db
from app.forms import CreateThreadForm, CreatePostForm

bp = Blueprint('threads', __name__, url_prefix="/threads")

@bp.route("/showThread/<threadId>")
def showThread(threadId):
    postsPerPage = 2
    page = request.args.get('page', 1, type=int)

    thread = Thread.query.filter_by(id=threadId).first()
    posts = thread.getPostsChronological().paginate(page, postsPerPage, False)
    nextUrl = url_for('threads.showThread', threadId=threadId, page=posts.next_num) if posts.has_next else None
    prevUrl = url_for('threads.showThread', threadId=threadId, page=posts.prev_num) if posts.has_prev else None

    return render_template("threads/showThread.html", title=f"{thread.group.name}|{thread.subject}", thread=thread, posts=posts.items, nextUrl=nextUrl, prevUrl=prevUrl, createPostForm=CreatePostForm())

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
