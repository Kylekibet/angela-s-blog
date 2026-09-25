from datetime import date
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import current_user, login_required
from models import db, BlogPost, Comment
from forms import CreatePostForm, CommentForm
from decorators import admin_only

posts_bp = Blueprint('posts', __name__)


@posts_bp.route('/')
def get_all_posts():
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()
    return render_template("index.html", all_posts=posts)


@posts_bp.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    requested_post = db.get_or_404(BlogPost, post_id)
    comment_form = CommentForm()
    if comment_form.validate_on_submit():
        if current_user.is_authenticated:
            comment = Comment(
                author_id=current_user.id,
                text=comment_form.text.data,
                post_id=post_id,
            )
            db.session.add(comment)
            db.session.commit()
        else:
            flash("You need to login or register to comment.")
            return redirect(url_for("auth.login"))
    return render_template("post.html", post=requested_post, form=comment_form, comments=requested_post.comments)


@posts_bp.route("/new-post", methods=["GET", "POST"])
@login_required
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("posts.get_all_posts"))
    return render_template("make-post.html", form=form)


@posts_bp.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@login_required
@admin_only
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = current_user
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("posts.show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True)


@posts_bp.route("/delete/<int:post_id>")
@login_required
@admin_only
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('posts.get_all_posts'))