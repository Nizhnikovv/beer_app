from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField
from flasksite.models import Order


class BuyForm(FlaskForm):
    item = SelectField("Какое пиво?", choices=[(k,v) for k,v in Order.key_beer.items()])
    quantity = SelectField("Сколько литров?", choices=[0.5, 1, 1.5, 2])
    submit = SubmitField("Купить пиво!")
