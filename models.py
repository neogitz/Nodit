from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from ext import db, login_manager
from datetime import date


class User(db.Model, UserMixin):
    __tablename__ = "Users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    gender = db.Column(db.String)
    birthday = db.Column(db.Date)
    country = db.Column(db.String)
    pfp = db.Column(db.String)
    role = db.Column(db.String, default="user")

    posts = db.relationship("Post", back_populates="creator", lazy=True)
    comments = db.relationship("Comment", back_populates="commenter", lazy=True)

    def check_password(self, unhashed_password):
        return check_password_hash(self.password, unhashed_password)


class Thread(db.Model):
    __tablename__ = "Threads"

    threadID = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    date = db.Column(db.Date, default=date.today)
    description = db.Column(db.String, nullable=False)

    creatorID = db.Column(db.Integer, db.ForeignKey("Users.id"), nullable=False)
    creator = db.relationship("User", backref="threads", foreign_keys=[creatorID])
    posts = db.relationship("Post", backref="thread", lazy=True)


class Post(db.Model):
    __tablename__ = "Posts"

    postID = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=date.today)
    title = db.Column(db.String, nullable=False)
    text = db.Column(db.String, nullable=False)
    img = db.Column(db.String, nullable=True)

    threadID = db.Column(db.Integer, db.ForeignKey("Threads.threadID"))
    creatorID = db.Column(db.Integer, db.ForeignKey("Users.id"), nullable=False)

    creator = db.relationship("User", back_populates="posts", foreign_keys=[creatorID])

    nods = db.relationship("Nod", back_populates="post", lazy="select")


class Comment(db.Model):
    __tablename__ = "Comments"

    commentID = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String, nullable=False)
    date = db.Column(db.Date, default=date.today)
    img = db.Column(db.String, nullable=True)

    threadID = db.Column(db.Integer, db.ForeignKey("Threads.threadID"), nullable=False)
    postID = db.Column(db.Integer, db.ForeignKey("Posts.postID"), nullable=False)
    userID = db.Column(db.Integer, db.ForeignKey("Users.id"), nullable=False)

    thread = db.relationship("Thread", backref="comments")
    post = db.relationship("Post", backref="comments")
    nods = db.relationship("Nod", back_populates="comment", lazy="select")

    commenter = db.relationship("User", back_populates="comments", foreign_keys=[userID])


class Nod(db.Model):
    __tablename__ = "Nods"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("Users.id"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("Posts.postID"), nullable=True)
    comment_id = db.Column(db.Integer, db.ForeignKey("Comments.commentID"), nullable=True)

    user = db.relationship("User", backref="nods")
    post = db.relationship("Post", back_populates="nods")
    comment = db.relationship("Comment", back_populates="nods")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
