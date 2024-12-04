#app/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, EqualTo, Length

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RouteForm(FlaskForm):
    name = StringField('Route Name', validators=[DataRequired()])
    grade = SelectField('Grade', choices=[
                                        ('4a', '4a'), ('4a+', '4a+'), ('4b', '4b'), ('4b+', '4b+'),
                                        ('4c', '4c'), ('4c+', '4c+'), ('5a', '5a'), ('5a+', '5a+'),
                                        ('5b', '5b'), ('5b+', '5b+'), ('5c', '5c'), ('5c+', '5c+'),
                                        ('6a', '6a'), ('6a+', '6a+'), ('6b', '6b'), ('6b+', '6b+'),
                                        ('6c', '6c'), ('6c+', '6c+'), ('7a', '7a'), ('7a+', '7a+'),
                                        ('7b', '7b'), ('7b+', '7b+'), ('7c', '7c'), ('7c+', '7c+'),
                                        ('8a', '8a'), ('8a+', '8a+'), ('8b', '8b'), ('8b+', '8b+'),
                                        ('8c', '8c'), ('8c+', '8c+'), ('9a', '9a'), ('9a+', '9a+'),
                                        ('9b', '9b'), ('9b+', '9b+'), ('9c', '9c'), ('Project','Project')],
                        validators=[DataRequired()])
    wall = SelectField('Wall', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Add Route')
