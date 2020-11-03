from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user

from app.models import User, Group, Thread, Post
from app import db
from app.forms import CreatePostForm

bp = Blueprint('posts', __name__, url_prefix="/posts")

@bp.route("/<threadId>/createPost", methods=["GET","POST"])
def createPost(threadId):
    form = CreatePostForm()

    if form.validate_on_submit():
        #get current group
        thread = Thread.query.filter_by(id=threadId).first()

        # Create new thread
        post = Post(
            body = form.body.data,
            author = current_user,
            thread = thread
        )

        db.session.add(post)
        db.session.commit()
        flash("Post created!") #prob won't be seen
        return redirect(url_for('threads.showThread', threadId=thread.id))

    #return render_template("threads/showThread.html", title=f"{thread.group.name}|{thread.subject}", thread=thread, posts=thread.getPostsChronological().all(), createPostForm=form)
    return redirect(url_for('threads.showThread', threadId=thread.id))
