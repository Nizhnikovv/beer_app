from flask import render_template, Blueprint

main = Blueprint("main", __name__)

@main.route("/")
def home():
    return render_template("layout.html") 