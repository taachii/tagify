from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_login import current_user

class ZipUploadForm(FlaskForm):
    zip_file = FileField('Plik ZIP ze zdjęciami', validators=[
        FileRequired(message="Wybierz plik ZIP."),
        FileAllowed(['zip'], message="Dozwolone są tylko pliki ZIP.")
    ])
    submit = SubmitField('Prześlij')

class ModelSelectionForm(FlaskForm):
    model = SelectField('Wybierz model', choices=[], validators=[
        DataRequired(message="Wybierz model z listy.")
    ])
    submit = SubmitField('Rozpocznij klasyfikację')

class EditProfileForm(FlaskForm):
    username = StringField('Nazwa użytkownika', validators=[
        DataRequired(message="Podaj nazwę użytkownika"), 
        Length(min=3, message="Nazwa użytkownika powinna się składać z co najmniej 3 znaków")
    ])
    email = StringField('Email', validators=[
        DataRequired(message="Podaj adres e-mail"),
        Email(message="Podaj poprawny adres e-mail")
    ])
    submit = SubmitField('Zapisz zmiany')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Obecne hasło', validators=[
        DataRequired(message="Podaj obecne hasło")
    ])
    new_password = PasswordField('Nowe hasło', validators=[
        DataRequired(message="Podaj nowe hasło"), 
        Length(min=6, message="Nowe hasło powinno się składać z co najmniej 6 znaków")
    ])
    confirm_password = PasswordField('Potwierdź nowe hasło', validators=[
        DataRequired(message="Powtórz hasło"), 
        EqualTo('new_password', message='Hasła muszą być takie same')
    ])
    submit = SubmitField('Zmień hasło')

class UserPathsForm(FlaskForm):
    people = StringField('Lokalizacja dla "people"')
    animals = StringField('Lokalizacja dla "animals"')
    landscape = StringField('Lokalizacja dla "landscape"')
    vehicles = StringField('Lokalizacja dla "vehicles"')
    buildings = StringField('Lokalizacja dla "buildings"')
    plants = StringField('Lokalizacja dla "plants"')
    food = StringField('Lokalizacja dla "food"')
    other = StringField('Lokalizacja dla "other"')
    submit = SubmitField('Zapisz ścieżki')
