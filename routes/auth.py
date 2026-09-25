from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
from forms import RegisterForm, LoginForm

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=["GET", "POST"])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        check_email = db.session.execute(db.select(User).where(User.email == register_form.email.data)).scalar()
        if not check_email:
            hashed_password = generate_password_hash(register_form.password.data, method='scrypt', salt_length=16)
            user = User(
                email=register_form.email.data,
                name=register_form.name.data,
                password=hashed_password
            )
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('posts.get_all_posts'))
        else:
            flash("Email already registered", "error")
            return redirect(url_for('auth.register'))
    return render_template("register.html", form=register_form)


@auth_bp.route('/login', methods=["GET", "POST"])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        email = login_form.email.data
        password = login_form.password.data
        user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('posts.get_all_posts'))
        else:
            flash("Invalid username or password", "error")
            return redirect(url_for('auth.login'))
    return render_template("login.html", form=login_form)


@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('posts.get_all_posts'))