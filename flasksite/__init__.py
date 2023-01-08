from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flasksite.config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "users.login"
login_manager.login_message_category = "info"
mail = Mail()

@login_manager.user_loader
def load_user(user_id):
    pass

def create_app(config_class = Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from flasksite.main.routes import main
    app.register_blueprint(main)

    with app.app_context():
        db.create_all()

    return app
    