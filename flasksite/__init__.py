from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flasksite.config import Config
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "users.login"
login_manager.login_message = "Сначала авторизуйтесь"
login_manager.login_message_category = "info"
mail = Mail()
bcrypt = Bcrypt()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    bcrypt.init_app(app)

    from flasksite.main.routes import main
    from flasksite.users.routes import users
    from flasksite.orders.routes import orders
    from flasksite.errors.handlers import errors
    app.register_blueprint(main)
    app.register_blueprint(users)
    app.register_blueprint(orders)
    app.register_blueprint(errors)

    with app.app_context():
        db.create_all()

    from flasksite.models import User, Order
    from datetime import datetime, timedelta
    import pytz
    @app.before_request
    def before():
        orders = Order.query.filter_by(completed=False)
        msc_tz = pytz.timezone("Europe/Moscow")
        for order in orders:
            if msc_tz.localize(order.date_ordered) - timedelta(days=1) > datetime.now(tz=pytz.timezone("Europe/Moscow")):
                User.send_order_deletion(order)
                db.session.delete(order)
        db.session.commit()

    return app
    