from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask_wtf.file import FileField, FileAllowed, FileRequired

class ZipUploadForm(FlaskForm):
    zip_file = FileField('Plik ZIP ze zdjęciami', validators=[
        FileRequired(message="Wybierz plik ZIP."),
        FileAllowed(['zip'], message="Dozwolone są tylko pliki ZIP.")
    ])
    submit = SubmitField('Prześlij')

class EditProfileForm(FlaskForm):
    username = StringField('Nazwa użytkownika', validators=[DataRequired(), Length(min=3, max=30)])
    email = StringField('Adres e-mail', validators=[DataRequired(), Email()])
    submit = SubmitField('Zapisz zmiany')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Obecne hasło', validators=[DataRequired()])
    new_password = PasswordField('Nowe hasło', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Potwierdź nowe hasło', validators=[
        DataRequired(), EqualTo('new_password', message='Hasła muszą być takie same')
    ])
    submit = SubmitField('Zmień hasło')
