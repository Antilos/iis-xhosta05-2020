from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app.visibility import Visibility

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

friend_groups_assoc = db.Table('friend_groups_assoc',
    db.Column('group1_id', db.Integer, db.ForeignKey('group.id'), primary_key=True),
    db.Column('group2_id', db.Integer, db.ForeignKey('group.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    profile_desc = db.Column(db.Text)
    profile_visibility = db.Column(db.Integer, nullable=False, default=0)

    owned_groups = db.relationship('Group', backref='owner', lazy='dynamic')
    moderated_groups = db.relationship('Group', secondary=group_moderators_assoc, backref=db.backref('moderators', lazy='dynamic'), lazy='dynamic')
    joined_groups = db.relationship('Group', secondary=group_members_assoc, backref=db.backref('members', lazy='dynamic'), lazy='dynamic')

    opened_threads = db.relationship('Thread', backref='opener', lazy='dynamic')

    authored_posts = db.relationship('Post', backref='author', lazy='dynamic')

    authored_comments = db.relationship('Comment', backref='author', lazy='dynamic')

    upvoted_posts = db.relationship('Post', secondary=upvotes_assoc, backref='upvoters', lazy='dynamic')
    downvoted_posts = db.relationship('Post', secondary=downvotes_assoc, backref='downvoters', lazy='dynamic')

    def __repr__(self):
        return f"<User {self.username}>"

    #authentification
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def isOwnerOf(self, group):
        return group.owner.id == self.id

    def isModeratorOf(self, group):
        return (group.owner.id == self.id) or group.moderators.filter_by(id=self.id).first()

    def isMemberOf(self, group):
        
        return False or self == group.owner or group.members.filter_by(id=self.id).first()

    def isMemberOfFriendGroupOf(self, group):
        #TODO: too many queries, needs to be optimized
        for friend in group.friends.all():
            if friend.members.query.filter_by(id=self.id):
                return True
        return False

    def isInMutualGroup(self, user):
        return False or self.joined_groups.query.join(user.joined_groups).first()

    def isInMutualFriendGroup(self, user):
        ...

    def hasPermissionToViewGroup(self, group):
        visibility = group.visibility
        return \
            (visibility == Visibility.PUBLIC) or \
            (visibility == Visibility.REGISTERED) or \
            (visibility == Visibility.GROUP and self.isMemberOf(group)) or \
            (visibility == Visibility.FRIEND_GROUP and (self.isMemberOf(group) or self.isMemberOfFriendGroupOf(group)))

    def hasPermissionToViewUser(self, user):
        visibility = user.profile_visibility
        return \
            (visibility == Visibility.PUBLIC) or \
            (visibility == Visibility.REGISTERED) or \
            (visibility == visibility.GROUP and self.isInMutualGroup(user)) or \
            (visibility == visibility.FRIEND_GROUP and ((self.isInMutualGroup(user)) or self.isInMutualFriendGroup(user)))

    def hasPublicProfile(self):
        return self.profile_visibility == Visibility.PUBLIC

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), unique=True)
    description = db.Column(db.Text)
    founded_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    visibility = db.Column(db.Integer, nullable=False, default=0)
    join_permission = db.Column(db.Integer, nullable=False, default=0)

    friends = db.relationship(
        'Group',
        secondary=friend_groups_assoc,
        primaryjoin=id==friend_groups_assoc.c.group1_id,
        secondaryjoin=id==friend_groups_assoc.c.group2_id
    )

    threads = db.relationship('Thread', backref='group', lazy='dynamic')

    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def isPublic(self):
        return self.visibility == Visibility.PUBLIC

class Thread(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(160))
    opened_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    description = db.Column(db.Text)

    posts = db.relationship('Post', backref='thread', lazy='dynamic')

    opener_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))

    def createPost(self, post):
        self.posts.append(post)

    def removePost(self, post):
        self.posts.remove(post)

    def getPostsChronological(self):
        return self.posts.order_by(Post.timestamp.desc())

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ranking = db.Column(db.Integer, nullable=False, default=0)

    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    thread_id = db.Column(db.Integer, db.ForeignKey('thread.id'))

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) 

    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))