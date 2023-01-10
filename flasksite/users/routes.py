from flask import Blueprint, flash, redirect, render_template, url_for, request, abort
from .forms import UserForm, LoginForm, DeleteUserForm, UpdateUser
from flasksite.models import User, Order
from flasksite import db, bcrypt
from .utils import save_picture, delete_picture
from flask_login import login_user, logout_user, current_user, login_required

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

@users.route("/user/<string:nickname>", methods=["GET", "POST"])
@login_required
def user_orders(nickname):
    user = User.query.filter_by(nickname=nickname).first_or_404()
    if current_user.admin != True and current_user != user:
        abort(403)
    orders = Order.query.filter_by(author=user).order_by(Order.date_ordered.desc())
    form = DeleteUserForm()
    if form.validate_on_submit():
        if current_user.admin != True:
            abort(403)
        for order in orders:
            db.session.delete(order)
        if user.image_file != "default.jpg":
            delete_picture(user.image_file)
        db.session.delete(user)
        db.session.commit()
        flash("Пользователь был удален", "success")
        return redirect(url_for("main.home"))
    return render_template("user_orders.html", orders=orders, user=user, form=form)

@users.route("/user/<string:nickname>/update", methods=["GET", "POST"])
@login_required
def update_user(nickname):
    user = User.query.filter_by(nickname=nickname).first_or_404()
    if current_user != user and current_user.admin != True:
        abort(403)
    form = UpdateUser(obj=user)
    form.user_id.data = str(user.id)
    if form.validate_on_submit():
        if form.picture.data:
            if user.image_file != "default.jpg":
                delete_picture(user.image_file)
            picture_file = save_picture(form.picture.data)
            user.image_file = picture_file
        form.populate_obj(user)
        db.session.commit()
        flash("Аккаунт был обновлен", "success")
        return redirect(url_for("users.user_orders", nickname=user.nickname))
    return render_template("update_user.html", title="Изменить " + user.nickname, form=form)
    
    
