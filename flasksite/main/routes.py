from flask import render_template, Blueprint, flash, redirect, url_for
from flasksite.models import User, Order
from flasksite import db
from flask_login import login_required
from .forms import BuyForm

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
        form.populate_obj(order)
        db.session.add(order)
        db.session.commit()
        flash("Заказ был сделан!", "success")
        return redirect(url_for("main.home"))
    return render_template("buy.html", form=form)
        
        
