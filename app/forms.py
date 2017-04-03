from wtforms.validators import InputRequired
from flask_wtf.file import FileRequired
from wtforms.validators import DataRequired, Email
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import StringField,PasswordField, TextAreaField, SelectField
from app import db
from models import UserProfile
from flask_wtf import Form



class ProfileForm(FlaskForm):
    firstname = StringField('First Name', validators=[InputRequired()])
    lastname = StringField('Last Name', validators=[InputRequired()])
    username = StringField('Username', validators=[InputRequired()])
    age = StringField('Age', validators=[InputRequired()])
    biography = TextAreaField('Biography', validators=[InputRequired()])
    image = FileField(validators=[FileRequired()])
    gender = SelectField('Gender', choices = [('F', 'Female'),('M', 'Male')])

    def __init__(self, *args, **kwargs):
      FlaskForm.__init__(self, *args, **kwargs)
 
    def validate(self):
      if not FlaskForm.validate(self):
        return False
     
      # Check if username is already in the database
      user = UserProfile.query.filter_by(username=self.username.data).first()
      if user:
        # Error message
        self.username.errors.append('Username already taken.')
        return False
      else:
        return True
