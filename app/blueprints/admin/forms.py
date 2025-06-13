from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length
from app.models import UserRole

class EditUserForm(FlaskForm):
    username = StringField('Nazwa użytkownika', validators=[
        DataRequired(), Length(min=3, max=64)
    ])
    email = StringField('Email', validators=[
        DataRequired(), Email()
    ])
    role = SelectField('Rola', choices=[
        (UserRole.ADMIN.value, 'Admin'),
        (UserRole.REGULAR.value, 'Użytkownik'),
        (UserRole.RESEARCHER.value, 'Badacz')
    ], validators=[DataRequired()])
    submit = SubmitField('Zapisz zmiany')
