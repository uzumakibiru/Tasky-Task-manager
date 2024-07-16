from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField

class RegisterForm(FlaskForm):
    name=StringField("Name",validators=[DataRequired()])
    email=StringField("Email",validators=[DataRequired()])
    password=PasswordField("Password",validators=[DataRequired()])
    
    submit=SubmitField("Sign up")

# Create a form to login existing users
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class TaskForm(FlaskForm):
    task=CKEditorField("Task",validators=[DataRequired()])
    submit=SubmitField("ADD")
class ProjectForm(FlaskForm):
    task=CKEditorField("Task",validators=[DataRequired()])
    submit=SubmitField("ADD")

class Add(FlaskForm):
    mail = StringField("Email", validators=[DataRequired()])
    submit = SubmitField("Search")