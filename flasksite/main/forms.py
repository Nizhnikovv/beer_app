from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField
from flasksite.models import Order


class BuyForm(FlaskForm):
    choices_beer=[(k,v + " " + str(Order.key_price[k]//2) + "₽") for k,v in Order.key_beer.items()]
    item = SelectField("Какое пиво?", choices=choices_beer)
    quantity = SelectField("Сколько литров?", choices=[0.5, 1, 1.5, 2])
    submit = SubmitField("Купить пиво!")
