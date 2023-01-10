from flask_wtf import FlaskForm
from wtforms import SubmitField

class DeleteOrder(FlaskForm):
    submit = SubmitField("Удалить заказ")

class ConfirmOrder(FlaskForm):
    submit = SubmitField("Подтвердить заказ")