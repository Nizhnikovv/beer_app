from flask import Blueprint, flash, redirect, render_template, url_for, request
from .forms import UserForm, LoginForm
from flasksite.models import User
from flasksite import db, bcrypt
from .utils import save_picture
from flask_login import login_user, logout_user, current_user

users = Blueprint("users", __name__)

@users.route("/register", methods=["GET", "POST"])
def register():
    logout_user()
    form = UserForm()
    if form.validate_on_submit():
        user = User()
        form.populate_obj(user)
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            user.image_file = picture_file
        hashed_pw = bcrypt.generate_password_hash(form.password.data)
        user.password = hashed_pw
        db.session.add(user)
        db.session.commit()
        flash("Ваш аккаунт был создан!", "success")
        return redirect(url_for("main.home"))
    return render_template("register.html", form=form, legend="Зарегестрироваться")

@users.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(nickname=form.nickname.data).first()
        if not user:
            user = User.query.filter_by(email=form.email.data).first()
        if bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("main.home"))
        else:
            flash("Не удалось зайти. Проверьте правильность пароля", "danger")
    return render_template("login.html", form=form, legend="Войти")
