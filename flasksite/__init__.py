from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flasksite.config import CeleryConfig, ProductionConfig as Config
from flask_bcrypt import Bcrypt
from celery import Celery
import json

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "users.login"
login_manager.login_message = "Сначала авторизуйтесь"
login_manager.login_message_category = "info"
mail = Mail()
bcrypt = Bcrypt()
celery = Celery(__name__, broker=CeleryConfig.broker_url)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config.from_file("/etc/config_beersite.json", load=json.load)

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    bcrypt.init_app(app)
    celery.config_from_object(CeleryConfig)

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

    return app
    