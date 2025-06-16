from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class RegistrationForm(FlaskForm):
    username = StringField('Nazwa użytkownika', validators=[
        DataRequired(message="Podaj nazwę użytkownika"), 
        Length(min=3, message="Nazwa użytkownika powinna się składać z co najmniej 3 znaków")
    ])
    email = StringField('Email', validators=[
        DataRequired(message="Podaj adres e-mail"),
        Email(message="Podaj poprawny adres e-mail")
    ])
    password = PasswordField('Hasło', validators=[
        DataRequired(message="Podaj hasło"), 
        Length(min=6, message="Hasło musi się składać z co najmniej 6 znaków")
    ])
    confirm_password = PasswordField('Powtórz hasło', validators=[
        DataRequired(message="Powtórz hasło"), 
        EqualTo('password', message='Hasła muszą być takie same')
    ])
    submit = SubmitField('Zarejestruj się')

class LoginForm(FlaskForm):
    username = StringField('Nazwa użytkownika', validators=[
        DataRequired(message="Podaj nazwę użytkownika")
    ])
    password = PasswordField('Hasło', validators=[
        DataRequired(message="Podaj hasło")
    ])
    submit = SubmitField('Zaloguj się')
