from flask_wtf import FlaskForm
from wtforms import SubmitField
from flask_wtf.file import FileField, FileAllowed, FileRequired

class ZipUploadForm(FlaskForm):
    zip_file = FileField('Plik ZIP ze zdjęciami', validators=[
        FileRequired(message="Wybierz plik ZIP."),
        FileAllowed(['zip'], message="Dozwolone są tylko pliki ZIP.")
    ])
    submit = SubmitField('Prześlij')
