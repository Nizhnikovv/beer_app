from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, HiddenField, EmailField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Length, ValidationError, Email, EqualTo
from flasksite.models import User

class UserForm(FlaskForm):
    nickname = StringField("Введите никнейм", [DataRequired("Введите никнейм"), Length("Никнейм должен не должен превышать 10 символов", max=10)])
    email = EmailField("Введите вашу почту", [DataRequired("Введите почту"), Email("Введите корректный адрес электронной почты")])
    password = PasswordField("Введите пароль", [DataRequired("Введите пароль")])
    con_password = PasswordField("Повторите пароль", [EqualTo("Пароли не совпадают")])
    picture = FileField("Фото профиля", [FileAllowed(["jpg", "png"], "Только jpg и png файлы")])

    def validate_nickname(form, field):
        if " " in field.data:
            raise ValidationError("Никнейм не должен содержать пробелы")
        if User.query.filter_by(nickname=field.data).first():
            raise ValidationError("Никнейм уже занят")

    def validate_email(form, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("Электронная почта уже занята другим пользователем")
