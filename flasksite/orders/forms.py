from flask_wtf import FlaskForm
from wtforms import SubmitField

class DeleteOrder(FlaskForm):
    submit_d = SubmitField("Удалить заказ")

class ConfirmOrder(FlaskForm):
    submit_c = SubmitField("Подтвердить")