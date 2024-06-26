from app import db, login
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app.enums import Visibility, JoinPermission, RequestStatus
import logging

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

group_tag_assoc = db.Table('group_tag_assoc',
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

user_tag_assoc = db.Table('user_tag_assoc',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

class AnonymousUser(AnonymousUserMixin):
    def hasPermissionToViewGroup(self, group):
        visibility = group.visibility
        return visibility == Visibility.PUBLIC

    def hasPermissionToViewUser(self, user):
        visibility = user.profile_visibility
        return visibility == Visibility.PUBLIC

    def isAdmin(self):
        return False

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    profile_desc = db.Column(db.Text)
    profile_visibility = db.Column(db.Integer, nullable=False, default=Visibility.PUBLIC)

    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    owned_groups = db.relationship('Group', backref='owner', lazy='dynamic')
    moderated_groups = db.relationship('Group', secondary=group_moderators_assoc, backref=db.backref('moderators', lazy='dynamic'), lazy='dynamic')
    joined_groups = db.relationship('Group', secondary=group_members_assoc, backref=db.backref('members', lazy='dynamic'), lazy='dynamic')

    group_join_requests = db.relationship('Group_Join_Request', backref='user', lazy='dynamic')
    group_moderator_promotion_requests = db.relationship('Group_Moderator_Promotion_Request', backref='user', lazy='dynamic')

    opened_threads = db.relationship('Thread', backref='opener', lazy='dynamic')

    authored_posts = db.relationship('Post', backref='author', lazy='dynamic')

    authored_comments = db.relationship('Comment', backref='author', lazy='dynamic')

    upvoted_posts = db.relationship('Post', secondary=upvotes_assoc, backref=db.backref('upvoters', lazy='dynamic'), lazy='dynamic')
    downvoted_posts = db.relationship('Post', secondary=downvotes_assoc, backref=db.backref('downvoters', lazy='dynamic'), lazy='dynamic')

    followed_tags = db.relationship(
        'Tag',
        secondary=user_tag_assoc,
        backref=db.backref('users_following', lazy='dynamic'),
        lazy='dynamic'
    )

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
        
        return False or group.members.filter_by(id=self.id).first()

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
            self.is_admin or \
            (visibility == Visibility.PUBLIC) or \
            (visibility == Visibility.REGISTERED) or \
            (visibility == Visibility.GROUP and self.isMemberOf(group)) or \
            (visibility == Visibility.FRIEND_GROUP and (self.isMemberOf(group) or self.isMemberOfFriendGroupOf(group)))

    def hasPermissionToViewUser(self, user):
        visibility = user.profile_visibility
        return \
            self.is_admin or \
            (visibility == Visibility.PUBLIC) or \
            (visibility == Visibility.REGISTERED) or \
            (visibility == Visibility.GROUP and self.isInMutualGroup(user)) or \
            (visibility == Visibility.FRIEND_GROUP and ((self.isInMutualGroup(user)) or self.isInMutualFriendGroup(user)))

    def hasPublicProfile(self):
        return self.profile_visibility == Visibility.PUBLIC

    def isAdmin(self):
        return self.is_admin

    def hasVoted(self, post):
        return self.upvoted_posts.query.filter_by(id = post.id).first() or self.downvoted_posts.query.filter_by(id = post.id).first()

    def addTag(self, tagStr):
        # does the tag exist?
        tag = Tag.query.filter_by(keyword=tagStr).first()
        if not tag:
            #create tag
            tag = Tag(keyword=tagStr)
            db.session.add(tag)
            #add tag to group
            self.followed_tags.append(tag)
            return True
        else:
            #check if this user is already following this tag
            if not self.followed_tags.filter_by(id=tag.id).first():
                #add tag to user
                self.followed_tags.append(tag)
                return True
            else:
                return False

    def removeTag(self, tagStr):
        # does the tag exist?
        tag = Tag.query.filter_by(keyword=tagStr).first()
        if not tag:
            #no tag to remove
            logging.debug(f"Tag {tagStr} you are trying to remove doesn't exits.")
            return True
        else:
            #check if this user is already following this tag
            if self.followed_tags.filter_by(id=tag.id).first():
                #remove tag from user
                self.followed_tags.remove(tag)
                return True
            else:
                return False

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

def getUsersByVisibility(visibility:Visibility):
    if not visibility in Visibility.__members__.values():
        raise KeyError(f"{visibility} is not a valid profile visibility category.")
    else:
        return User.query.filter_by(profile_visibility=visibility)

def makeUserAdmin(user:User):
    if not user.is_admin:
        user.is_admin=True
        return True
    else:
        return False
    

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), unique=True)
    description = db.Column(db.Text)
    created_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    visibility = db.Column(db.Integer, nullable=False, default=0)
    is_open = db.Column(db.Boolean, nullable=False, default=True)

    join_requests = db.relationship('Group_Join_Request', backref='group', lazy='dynamic')
    moderator_promotion_requests = db.relationship('Group_Moderator_Promotion_Request', backref='group', lazy='dynamic')

    friends = db.relationship(
        'Group',
        secondary=friend_groups_assoc,
        primaryjoin=id==friend_groups_assoc.c.group1_id,
        secondaryjoin=id==friend_groups_assoc.c.group2_id
    )

    tags = db.relationship(
        'Tag',
        secondary=group_tag_assoc,
        backref=db.backref('tagged_groups', lazy='dynamic'),
        lazy='dynamic'
    )

    threads = db.relationship('Thread', backref='group', lazy='dynamic')

    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def isPublic(self):
        return self.visibility == Visibility.PUBLIC

    def isOpen(self):
        return self.is_open

    def isMember(self, user):
        return self.members.filter_by(id=user.id).count() > 0

    def addMember(self, user):
        if not self.isMember(user):
            self.members.append(user)

    def removeMember(self, user):
        if self.isMember(user):
            self.members.remove(user)

    def isModerator(self, user):
        return self.owner_id == user.id or self.moderators.filter_by(id=user.id).count() > 0

    def addModerator(self, user):
        if not self.isModerator(user):
            self.moderators.append(user)

    def isOwner(self, user):
        return self.owner_id == user.id

    def removeModerator(self, user):
        if self.isModerator(user):
            self.moderators.remove(user)

    def createJoinRequest(self, user):
        if not self.join_requests.filter_by(user_id=user.id).count > 0:
            self.join_requests.append(Group_Join_Request(user=user, group=self))

    def createModeratorPromotionRequest(self, user):
        if self.moderator_promotion_requests.filter_by(user_id=user.id).count() == 0:
            self.moderator_promotion_requests.append(Group_Moderator_Promotion_Request(user=user, group=self))

    def getThreadsChronological(self):
        return self.threads.order_by(Thread.opened_timestamp.desc())

    def addTag(self, tagStr):
        # does the tag exist?
        tag = Tag.query.filter_by(keyword=tagStr).first()
        if not tag:
            logging.debug(f"Creating Tag {tagStr}.")
            #create tag
            tag = Tag(keyword=tagStr)
            db.session.add(tag)
            #add tag to group
            logging.debug(f"Adding tag {tagStr}.")
            self.tags.append(tag)
            return True
        else:
            #check if this group is already tagged
            if not self.tags.filter_by(id=tag.id).first():
                logging.debug(f"Adding tag {tagStr}.")
                #add tag to group
                self.tags.append(tag)
                return True
            else:
                logging.debug(f"Group already has tag {tagStr}.")
                return False

    def removeTag(self, tagStr):
            # does the tag exist?
            tag = Tag.query.filter_by(keyword=tagStr).first()
            if not tag:
                #no tag to remove
                logging.debug(f"Tag {tagStr} you are trying to remove doesn't exits.")
                return True
            else:
            #check if this group is already tagged
                if self.tags.filter_by(id=tag.id).first():
                    #remove tag from group
                    logging.debug(f"Removing tag {tagStr}.")
                    self.tags.remove(tag)
                    return True
                else:
                    logging.debug(f"This group doesn't have tag {tagStr}.")
                    return False

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

    def upvote(self, user):
        #has upvoted?
        if not (self.upvoters.filter_by(id=user.id).first()):
            #has downvoted?
            if self.downvoters.filter_by(id=user.id).first():
                self.ranking += 2
                self.downvoters.remove(user)
            else:
                self.ranking += 1

            self.upvoters.append(user)
        
        return self.ranking

    def downvote(self, user):
        #has downvoted?
        if not (self.downvoters.filter_by(id=user.id).first()):
            #has upvoted?
            if self.upvoters.filter_by(id=user.id).first():
                self.ranking -= 2
                self.upvoters.remove(user)
            else:
                self.ranking -= 1

            self.downvoters.append(user)

        return self.ranking

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) 

    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

class Group_Join_Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.Integer, nullable=False, default=RequestStatus.UNPROCESSED)

    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def approve(self):
        """Approve this request and add the user to the group
        Return
        ------
        bool: True if processed succesfully, False if the request is already processed
        """
        if self.status == RequestStatus.UNPROCESSED:
            self.status = RequestStatus.APPROVED
            self.group.addMember(self.user)
            return True
        else:
            return False

    def deny(self):
        """Denies this request
        Return
        ------
        bool: True if processed succesfully, False if the request is already processed
        """
        if self.status == RequestStatus.UNPROCESSED:
            self.status = RequestStatus.DENIED
            return True
        else:
            return False

class Group_Moderator_Promotion_Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.Integer, nullable=False, default=RequestStatus.UNPROCESSED)

    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def approve(self):
        """Approve this request and makes the user a moderator
        Return
        ------
        bool: True if processed succesfully, False if the request is already processed
        """
        if self.status == RequestStatus.UNPROCESSED:
            self.status = RequestStatus.APPROVED
            self.group.addModerator(self.user)
            return True
        else:
            return False

    def deny(self):
        """Denies this request
        Return
        ------
        bool: True if processed succesfully, False if the request is already processed
        """
        if self.status == RequestStatus.UNPROCESSED:
            self.status = RequestStatus.DENIED
            return True
        else:
            return False

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(80), index=True, unique=True)