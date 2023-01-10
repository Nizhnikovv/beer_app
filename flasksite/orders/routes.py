from flask import Blueprint, render_template, abort, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from flasksite.models import Order
from .forms import DeleteOrder, ConfirmOrder
from flasksite import db

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

@orders.route("/order/<int:id>", methods=["GET", "POST"])
@login_required
def order(id):
    order = Order.query.get_or_404(id)
    user = order.author
    if current_user.admin != True and current_user != user:
        abort(403)
    form_d = DeleteOrder()
    form_c = ConfirmOrder()
    if form_d.validate_on_submit():
        db.session.delete(order)
        db.session.commit()
        flash("Заказ был удален", "seccess")
        return redirect(url_for("users.user_orders", nickname=user.nickname))
    if form_c.validate_on_submit():
        if current_user.admin != True:
            abort(403)
        order.completed = True
        user.volume += float(order.quantity)
        db.session.commit()
        return redirect(url_for("users.user_orders", nickname=user.nickname))
    return render_template("order.html", form_d=form_d, order=order, form_c=form_c)
    