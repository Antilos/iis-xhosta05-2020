from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

group_moderators_assoc = db.Table('group_moderators_assoc',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'), primary_key=True)
)

group_members_assoc = db.Table('group_members_assoc',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'), primary_key=True)
)

upvotes_assoc = db.Table('upvotes_assoc',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True)
)

downvotes_assoc = db.Table('downvotes_assoc',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    profile_desc = db.Column(db.Text)
    profile_visibility = db.Column(db.Integer, nullable=False, default=0)

    owned_groups = db.relationship('Group', backref='owner', foreign_keys='group.owner_id', lazy='dynamic')
    moderated_groups = db.relationship('Group', secondary=group_moderators_assoc, backref='moderators')
    joined_groups = db.relationship('Group', secondary=group_members_assoc, backref='members')

    opened_threads = db.relationship('Thread', backref='opener')

    authored_posts = db.relationship('Post', backref='author')

    upvoted_posts = db.relationship('Post', secondary=upvotes_assoc, backref='upvoters')
    downvoted_posts = db.relationship('Post', secondary=downvotes_assoc, backref='downvoters')

    def __repr__(self):
        return f"<User {self.username}>"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password) 

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), unique=True)
    founded_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    visibility = db.Column(db.Integer, nullable=False, default=0)

    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Thread(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(160))
    opened_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    description = db.Column(db.Text)

    opener_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ranking = db.Column(db.Integer, nullable=False, default=0)

    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))