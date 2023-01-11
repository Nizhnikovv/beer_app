from flask import render_template, Blueprint, flash, redirect, url_for
from flasksite.models import User, Order
from flasksite import db
from flask_login import login_required, current_user
from .forms import BuyForm
from datetime import datetime, timedelta
import pytz

main = Blueprint("main", __name__)

@main.route("/")
def home():
    users = User.query.order_by(User.volume.desc()).all()
    length = len(users)
    return render_template("HomePage.html", users=users, length=length) 

@main.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    form = BuyForm()
    if form.validate_on_submit():
        order = Order()
        user = current_user
        if Order.query.filter_by(author=user, completed=False).first():
            flash("Вы не можете иметь более одного не выполненного заказа", "warning")
            return redirect(url_for("users.user_orders", nickname=user.nickname))
        form.populate_obj(order)
        order.author = user
        db.session.add(order)
        db.session.commit()
        User.send_order_notif(order)
        flash("Заказ был сделан!", "success")
        return redirect(url_for("orders.order", id=order.id))
    return render_template("buy.html", form=form)

@main.before_request
def before():
    orders = Order.query.filter_by(completed=False)
    msc_tz = pytz.timezone("Europe/Moscow")
    for order in orders:
        if msc_tz.localize(order.date_ordered) - timedelta(days=1) > datetime.now(tz=pytz.timezone("Europe/Moscow")):
            User.send_order_deletion(order)
            db.session.delete(order)
    db.session.commit()

        
