from flask import Blueprint, flash, redirect, render_template, url_for, request, abort
from .forms import UserForm, LoginForm, DeleteUserForm, UpdateUser, RequestResetForm, ResetPasswordForm
from flasksite.models import User, Order
from flasksite import db, bcrypt
from .utils import save_picture, delete_picture
from flask_login import login_user, logout_user, current_user, login_required
from datetime import datetime
import pytz

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
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user.password = hashed_pw
        user.date_since = datetime.now(tz=pytz.timezone("Europe/Moscow"))
        db.session.add(user)
        db.session.commit()
        flash("Ваш аккаунт был создан!", "success")
        return redirect(url_for("main.home"))
    return render_template("register.html", form=form, title="Регистрация")

@users.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = LoginForm()
    if form.validate_on_submit():
        if "@" in form.nickname_or_email.data:
            user = User.query.filter_by(email=form.nickname_or_email.data).first()
        else:
            user = User.query.filter_by(nickname=form.nickname_or_email.data).first()
        if bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("main.home"))
        else:
            flash("Не удалось зайти. Проверьте правильность пароля", "danger")
    return render_template("login.html", form=form, title="Войти")

@users.route("/user/<string:nickname>", methods=["GET", "POST"])
@login_required
def user_orders(nickname):
    user = User.query.filter_by(nickname=nickname).first_or_404()
    if current_user.admin != True and current_user != user:
        abort(403)
    orders = Order.query.filter_by(author=user).order_by(Order.date_ordered.desc()).all()
    length = len(orders)
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
    return render_template("user_orders.html", orders=orders, user=user, form=form, length=length, title="Заказы "+user.nickname)

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
    
@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        user.send_reset_email()
        flash('На вашу почту было отправлено письмо для восстановления пароля', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', form=form, title="Забыли пароль")
    
@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('Неправельный или просроченный токен', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Ваш пароль был обновлен', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', form=form, title="Сброс пароля")

@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.home"))
