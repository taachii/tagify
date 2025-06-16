from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length
from app.models import UserRole

class EditUserForm(FlaskForm):
    username = StringField('Nazwa użytkownika', validators=[
        DataRequired(message="Podaj nazwę użytkownika"), 
        Length(min=3, message="Nazwa użytkownika powinna się składać z co najmniej 3 znaków"),
    ])
    
    email = StringField('Email', validators=[
        DataRequired(message="Podaj adres email"),
        Email(message="Podaj poprawny adres e-mail")
    ])
    
    role = SelectField('Rola', choices=[
        (UserRole.ADMIN.value, 'Admin'),
        (UserRole.REGULAR.value, 'Użytkownik'),
        (UserRole.RESEARCHER.value, 'Badacz')
    ], validators=[DataRequired()])
    
    submit = SubmitField('Zapisz zmiany')
