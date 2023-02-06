from flasksite import db, login_manager, mail, celery
from flask_login import UserMixin, current_user
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
from flask import current_app, url_for
from flask_mail import Message
from datetime import datetime, timedelta
import pytz

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
    date_since = db.Column(db.DateTime, nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    orders = db.relationship("Order", backref="author", lazy=True)

    def get_reset_token(self):
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

    @staticmethod
    @celery.task
    def send_reset_email(user_id):
        user = User.query.get(user_id)
        if not user:
            return
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
    @celery.task
    def send_order_notif(order_id):
        order = Order.query.get(order_id)
        if not order:
            return
        for user in User.query.filter_by(admin=True):
            msg = Message("Новый заказ пива", sender="dmitrix_n@mail.ru",recipients=[user.email])
            msg.body = f'''Заказ номер {order.id}.
{order.author.nickname} заказал {order.quantity}L пива "{order.get_beer()}" {order.date_ordered.strftime("%-d.%m.%Y в %-H:%M:%S")} на сумму {order.unit_price * order.quantity} рублей.
Ссылка на заказ: {url_for("orders.order", id=order.id, _external=True)}
'''
            mail.send(msg)

    @staticmethod
    @celery.task
    def send_order_deletion(order_id, order_quantity, order_beer, order_user_id):
        for user in User.query.filter_by(admin=True):
            msg = Message("Заказ пива был удален", sender="dmitrix_n@mail.ru", recipients=[user.email])
            msg.body = f'''Заказ номер {order_id}({order_quantity}L "{order_beer}") был удален''' 
            mail.send(msg)
        user = User.query.get(order_user_id)
        if user and user.admin != True:
            msg = Message("Заказ пива был удален", sender="dmitrix_n@mail.ru", recipients=[user.email])
            msg.body = f'''Ваш заказ номер {order_id}({order_quantity}L "{order_beer}") был удален''' 
            mail.send(msg)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_ordered = db.Column(db.DateTime, nullable=False)
    item = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, default=current_user)
    completed = db.Column(db.Boolean, nullable=False, default=False)

    key_beer = {1:"Hoegaarden", 2:"Bud"}
    key_price = {1:180, 2:180}

    def get_price(self):
        return self.key_price[self.item]

    def get_beer(self):
        return self.key_beer[self.item]
    
    @staticmethod
    @celery.task
    def check_orders_exp():
        orders = Order.query.filter_by(completed=False)
        msc_tz = pytz.timezone("Europe/Moscow")
        for order in orders:
            if msc_tz.localize(order.date_ordered) + timedelta(days=1) < datetime.now(tz=pytz.timezone("Europe/Moscow")):
                User.send_order_deletion(order.id, order.quantity, order.get_beer(), order.user_id)
                db.session.delete(order)
        db.session.commit()
