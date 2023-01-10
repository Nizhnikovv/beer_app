from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField


class BuyForm(FlaskForm):
    item = SelectField("Какое пиво?", choices=[(1,"Hoegaarden"), (2,"Bud")])
    quantity = SelectField("Сколько литров?", choices=[0.5, 1, 1.5, 2])
