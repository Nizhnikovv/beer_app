from datetime import datetime
from flasksite import db, login_manager, mail
from flask_login import UserMixin, current_user
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
from flask import current_app, url_for
import pytz
from flask_mail import Message

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(120), nullable=False, unique=True)
    image_file = db.Column(db.String(20), nullable=False, default="default.jpg")
    password = db.Column(db.String(60), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    volume = db.Column(db.Integer, nullable=False, default=0)
    date_since = db.Column(db.DateTime, nullable=False, default=datetime.now(tz=pytz.timezone("Europe/Moscow")))
    admin = db.Column(db.Boolean, nullable=False, default=False)
    orders = db.relationship("Order", backref="author", lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps(self.id)

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, max_age=1800)
        except:
            return None
        return User.query.get_or_404(user_id)

    def send_reset_email(user):
        token = user.get_reset_token()
        msg = Message('Запрос на сброс пароля',
                    sender='dmitrix_n@mail.ru',
                    recipients=[user.email])
        msg.body = f'''Для того, чтобы сбросить ваш пароль, перейдите по следующей ссылке:
{url_for('users.reset_token', token=token, _external=True)}

Если вы не делали такого запроса, просто проигнорируйте это сообщение и ничего не изменится.
'''
        mail.send(msg)        

    @staticmethod
    def send_order_notif(order):
        for user in User.query.filter_by(admin=True):
            msg = Message("Новый заказ пива", sender="dmitrix_n@mail.ru",recipients=[user.email])
            if order.item == 1:
                drink = "Hoegaarden"
            else:
                drink = "Bud"
            msg.body = f'''Заказ номер {order.id}.
{order.author.nickname} заказал {order.quantity}l пива "{drink}" {order.date_ordered.strftime("%-d.%m.%Y в %-H:%M:%S")}.
Ссылка на заказ: {url_for("orders.order", id=order.id, _external=True)}
'''
            mail.send(msg)

    @staticmethod
    def send_order_deletion(order):
        if order.item == 1:
            drink = "Hoegaarden"
        else:
            drink = "Bud"
        for user in User.query.filter_by(admin=True):
            msg = Message("Заказ пива был удален", sender="dmitrix_n@mail.ru", recipients=[user.email])
            msg.body = f'''Заказ номер {order.id}({order.quantity}l "{drink}") был удален''' 
            mail.send(msg)
        user = order.author
        if user.admin != True:
            msg = Message("Заказ пива был удален", sender="dmitrix_n@mail.ru", recipients=[user.email])
            msg.body = f'''Ваш заказ номер {order.id}({order.quantity}l "{drink}") был удален''' 
            mail.send(msg)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_ordered = db.Column(db.DateTime, nullable=False, default=datetime.now(tz=pytz.timezone("Europe/Moscow")))
    item = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, default=current_user)
    completed = db.Column(db.Boolean, nullable=False, default=False)

    key_beer = {1:"Hoegaarden", 2:"Bud"}
    key_price = {1:90, 2:90}

    def get_price(self):
        return self.key_price[self.item]

    def get_beer(self):
        return self.key_beer[self.item]