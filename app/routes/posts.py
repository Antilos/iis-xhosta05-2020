from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
import click
import logging

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

### Commands ###
@bp.cli.command("delete-all")
def delete_all():
    Post.query.delete()
    db.session.commit()
    logging.info("Deleted all posts.")

@bp.cli.command("create")
@click.argument('author_name')
@click.argument('thread_name')
@click.argument('body')
def create_post(author_name, thread_name, body):
    author = User.query.filter_by(username=author_name).first()
    thread = Thread.query.filter_by(subject=thread_name).first()
    if not author:
        logging.error(f"User {author_name} doesn't exist.")
    elif not thread:
        logging.error(f"Thread {thread_name} doesn't exist.")
    else:
        newPost = Post(
            body=body,author=author,thread=thread
        )
        db.session.add(newPost)
        db.session.commit()
        if len(post) > 10:
            logging.info(f"Created post \"{body[:10]}...\"")
        else:
            logging.info(f"Created post \"{body}\"")