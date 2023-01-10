from flask import Blueprint, flash, redirect, render_template, url_for
from .forms import UserForm
from flasksite.models import User
from flasksite import db
from .utils import save_picture

users = Blueprint("users", __name__)

@users.route("/register", methods=["GET", "POST"])
def register():
    form = UserForm()
    if form.validate_on_submit():
        user = User()
        form.populate_obj(user)
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            user.image_file = picture_file
        db.session.add(user)
        db.session.commit()
        flash("Ваш аккаунт был создан!", "success")
        return redirect(url_for("main.home"))
    return render_template("register.html", form=form)

