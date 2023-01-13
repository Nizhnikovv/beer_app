from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, HiddenField, EmailField, SubmitField, BooleanField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Length, ValidationError, Email, EqualTo
from flasksite.models import User

class UserForm(FlaskForm):
    nickname = StringField("Введите никнейм", [DataRequired("Введите никнейм"), Length(message="Никнейм должен не должен превышать 10 символов", max=10)])
    email = EmailField("Введите вашу почту", [Email("Введите корректный адрес электронной почты")])
    password = PasswordField("Введите пароль", [DataRequired("Введите пароль")])
    con_password = PasswordField("Повторите пароль", [EqualTo(message="Пароли не совпадают", fieldname="password")])
    picture = FileField("Фото профиля(по желанию)", [FileAllowed(["jpg", "png"], "Только jpg и png файлы")])
    submit = SubmitField("Создать аккаунт")

    def validate_nickname(form, field):
        if " " in field.data:
            raise ValidationError("Никнейм не должен содержать пробелы")
        if "@" in field.data:
            raise ValidationError("Никнейм не должен содержать @")
        if User.query.filter_by(nickname=field.data).first():
            raise ValidationError("Никнейм уже занят")

    def validate_email(form, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("Электронная почта уже занята другим пользователем")

class LoginForm(FlaskForm):
    nickname_or_email = StringField("Введите никнейм или почту")
    # email = EmailField("Введите вашу почту")
    password = PasswordField("Введите пароль", [DataRequired("Введите пароль")])
    remember = BooleanField("Запомнить меня")
    submit = SubmitField("Войти")

    def validate_nickname_or_email(form, field):
        try:
            Email()(form, field)
        except ValidationError:
            if field.data == "":
                raise ValidationError("Введите либо никнейм, либо почту")
            if " " in field.data and len(field.data) > 10:
                raise ValidationError("Никнейм не должен содержать пробелы и быть больше 10 символов")
            if not User.query.filter_by(nickname=field.data).first():
                raise ValidationError("Никнейм не существует")
        else:
            if not User.query.filter_by(email=field.data).first():
                raise ValidationError("Аккаунт с такой почтой не существует")

class DeleteUserForm(FlaskForm):
    submit = SubmitField("Удалить")            

class UpdateUser(FlaskForm):
    email = EmailField("Введите новую почту", [Email("Введите корректный адрес электронной почты")])
    picture = FileField("Фото профиля", [FileAllowed(["jpg", "png"], "Только jpg и png файлы")])
    submit = SubmitField("Обновить аккаунт")
    user_id = HiddenField()

    def validate_email(self, email):
        if User.query.get(int(self.user_id.data)).email != email.data:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

class RequestResetForm(FlaskForm):
    email = StringField('Почта')
    submit = SubmitField('Запросить сброс пароля')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('Аккаунта с такой почтой нет')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Пароль', validators=[DataRequired()])
    confirm_password = PasswordField('Повторить пароль',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Сбросить пароль')