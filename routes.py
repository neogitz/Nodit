import os
import uuid
from datetime import date

from flask import Flask, render_template, redirect, abort, request, url_for
from werkzeug.utils import secure_filename

from ext import app, db, UPLOAD_FOLDER
from forms import RegisterForm, EditUserForm, LoginForm, CreateThreadForm, CreatePostForm, PostCommentForm, FeedbackForm
from os import path
from models import User, Thread, Post, Comment, Nod
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash
from ext import migrate


@app.route("/")
def home():
    threads = Thread.query.order_by(Thread.date.desc()).all()
    trending_threads = threads[:5]
    return render_template(
        "index.html",
        threads=threads,
        trending_threads=trending_threads
    )


@app.route("/edit_user/<int:user_id>", methods=["GET", "POST"])
@login_required
def edit_user(user_id):
    user = User.query.get(user_id)
    form = EditUserForm(username=user.username,
                        gender=user.gender,
                        birthday=user.birthday,
                        country=user.country
                        )

    if form.validate_on_submit():
        user.username = form.username.data
        user.gender = form.gender.data
        user.birthday = form.birthday.data
        user.country = form.country.data

        db.session.commit()

        return redirect(f"/profile/{user_id}")

    return render_template("edit_user.html", form=form)


@app.route("/delete_user/<int:user_id>", methods=["GET", "POST"])
@login_required
def delete_user(user_id):
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()

    return redirect("/")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(User.username == form.username.data).first()

        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect("/")

        print(form.username.data)
    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():

        file = form.pfp.data

        if file == None:
            filename = "emptypfp.png"
        else:
            filename = file.filename
            file.save(path.join(UPLOAD_FOLDER, file.filename))

        new_user = User(username=form.username.data,
                        password=generate_password_hash(form.password.data),
                        gender=form.gender.data,
                        birthday=form.birthday.data,
                        country=form.country.data,
                        pfp=filename,
                        role="user")

        db.session.add(new_user)
        db.session.commit()

        return redirect("/")

    print(form.errors)
    return render_template("register.html", form=form)


@app.route("/profile/<int:user_id>")
def userprofile(user_id):
    user = User.query.get(user_id)
    posts = user.posts
    threads = user.threads
    comments = user.comments
    pfp = user.pfp
    return render_template("profile.html", userinfo=user, posts=posts, threads=threads, comments=comments)


@app.route("/userlist", methods=["GET"])
def userlist():
    search_query = request.args.get('search', '').lower()
    if search_query:
        if search_query.startswith('#'):
            user_id = search_query[1:]
            users = User.query.filter(User.id == user_id).all()
        else:
            users = User.query.filter(User.username.ilike(f"%{search_query}%")).all()
    else:
        users = User.query.all()

    return render_template("userslist.html", users=users)


@app.route("/profile")
@login_required
def profile():
    return render_template("current_profile.html", userinfo=current_user)


@app.route("/create_thread", methods=["GET", "POST"])
@login_required
def create_thread():
    form = CreateThreadForm()
    if form.validate_on_submit():
        new_thread = Thread(
            title=form.threadname.data,
            description=form.description.data,
            creatorID=current_user.id,
            date=date.today()
        )
        db.session.add(new_thread)
        db.session.commit()
        return redirect(url_for("view_thread", thread_id=new_thread.threadID))
    return render_template("createThread.html", form=form)


@app.route("/thread/<int:thread_id>/create_post", methods=["GET", "POST"])
@login_required
def create_post(thread_id):
    form = CreatePostForm()
    if form.validate_on_submit():
        filename = None
        if form.img.data:
            original = secure_filename(form.img.data.filename)
            ext = os.path.splitext(original)[1]
            filename = f"{uuid.uuid4().hex}{ext}"
            form.img.data.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        new_post = Post(
            title=form.postTitle.data,
            text=form.text.data,
            img=filename,
            threadID=thread_id,
            creatorID=current_user.id,
            date=date.today()
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("view_thread", thread_id=thread_id))

    return render_template("create_post.html", form=form)


@app.route("/thread/<int:thread_id>/post/<int:post_id>/comment", methods=["GET", "POST"])
@login_required
def create_comment(thread_id, post_id):
    form = PostCommentForm()
    post = Post.query.filter_by(postID=post_id, threadID=thread_id).first_or_404()

    if form.validate_on_submit():
        filename = None
        if form.img.data:
            ext = os.path.splitext(secure_filename(form.img.data.filename))[1]
            filename = f"{uuid.uuid4().hex}{ext}"
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            form.img.data.save(filepath)

        new_comment = Comment(
            text=form.text.data,
            img=filename,
            threadID=thread_id,
            postID=post_id,
            userID=current_user.id,
            date=date.today()
        )
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for("view_post", thread_id=thread_id, post_id=post_id))

    return render_template("create_comment.html", form=form, post=post)



@app.route("/thread/<int:thread_id>")
def view_thread(thread_id):
    thread = Thread.query.get_or_404(thread_id)
    posts = Post.query.filter_by(threadID=thread_id).order_by(Post.date.desc()).all()
    return render_template("view_thread.html", thread=thread, posts=posts)


@app.route("/thread/<int:thread_id>/post/<int:post_id>")
def view_post(thread_id, post_id):
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(postID=post_id).order_by(Comment.date.asc()).all()
    form = PostCommentForm()
    if form.validate_on_submit():
        new_comment = Comment(
            text=form.text.data,
            postID=post_id,
            userID=current_user.id
        )
        db.session.add(new_comment)
        db.session.commit()
        return redirect(f"/thread/{thread_id}/post/{post_id}")
    return render_template("view_post.html", post=post, comments=comments, form=form)


@app.route("/thread/<int:thread_id>/delete", methods=["POST"])
@login_required
def delete_thread(thread_id):
    thread = Thread.query.get_or_404(thread_id)
    if current_user.role != "Admin":
        abort(403)
    db.session.delete(thread)
    db.session.commit()
    return redirect("/")


@app.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if current_user.role != "Admin":
        abort(403)
    thread_id = post.threadID
    db.session.delete(post)
    db.session.commit()
    return redirect(f"/thread/{thread_id}")


@app.route("/comment/<int:comment_id>/delete", methods=["POST", "GET"])
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)

    if current_user.role != "Admin":
        abort(403)

    thread = Thread.query.get_or_404(comment.threadID)
    post = Post.query.get_or_404(comment.postID)

    db.session.delete(comment)
    db.session.commit()

    return redirect(f"/thread/{thread.threadID}/post/{post.postID}")


@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("query", "")

    threads = Thread.query.filter(Thread.title.ilike(f"%{query}%")).all()
    posts = Post.query.filter(Post.title.ilike(f"%{query}%") | Post.text.ilike(f"%{query}%")).all()

    return render_template("search_results.html", threads=threads, posts=posts, query=query)


@app.route("/nod", methods=["POST"])
@login_required
def nod():
    post_id = request.form.get("post_id")
    comment_id = request.form.get("comment_id")

    if not post_id and not comment_id:
        return redirect(request.referrer or "/")

    query_kwargs = dict(user_id=current_user.id,
                        post_id=post_id if post_id else None,
                        comment_id=comment_id if comment_id else None)

    existing = Nod.query.filter_by(**query_kwargs).first()

    if existing:
        db.session.delete(existing)
    else:
        db.session.add(Nod(**query_kwargs))

    db.session.commit()
    return redirect(request.referrer or "/")


@app.route("/feedback", methods=["GET", "POST"])
def feedback():
    form = FeedbackForm()
    return render_template("feedback.html", form=form)
