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
    return render_template("home.html", users=users, length=length) 

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
        order.item = int(form.item.data)
        order.quantity = float(form.quantity.data)
        order.author = user
        order.unit_price = order.get_price()
        db.session.add(order)
        db.session.commit()
        User.send_order_notif(order)
        flash("Заказ был сделан!", "success")
        return redirect(url_for("orders.order", id=order.id))
    return render_template("buy.html", form=form, title="Магазин")


        
