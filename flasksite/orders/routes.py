from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from flasksite.models import Order

orders = Blueprint("orders", __name__)

@orders.route("/orders")
@login_required
def orders_act():
    if current_user.admin != True:
        abort(403)
    orders = Order.query.filter_by(completed=False).order_by(Order.date_ordered.desc())
    return render_template("orders.html", orders=orders, legend="Активные заказы")

@orders.route("/orders/completed")
@login_required
def orders_comp():
    if current_user.admin != True:
        abort(403)
    orders = Order.query.order_by(Order.date_ordered.desc())
    return render_template("orders.html", orders=orders, legend="Все заказы")