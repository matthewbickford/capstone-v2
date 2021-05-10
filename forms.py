from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, Length


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])


class UpdateUserForm(FlaskForm):
    """Form for updating username and email address"""

    username = StringField('Username')
    email = StringField('E-mail', validators=[Email()])


class NewOriginalForm(FlaskForm):
    """Form for Making a new recipe"""

    name = StringField('Name', validators=[DataRequired()])
    video = StringField('Optional Link to Video')
    category = StringField('Drink Category')
    iba = StringField('IBA Category if Applicable')
    glass = StringField('Type of Glass')
    instructions = StringField('Recipe Instructions')
    drinkThumb = StringField('Optional Image URL')

    ingredient1 = StringField(
        'First Ingredient', validators=[DataRequired()])
    measure1 = StringField(
        'First Ingredient Amount', validators=[DataRequired()])

    ingredient2 = StringField('Second Ingredient')
    measure2 = StringField('Second Ingredient Amount')

    ingredient3 = StringField('Third Ingredient')
    measure3 = StringField('Third Ingredient Amount')

    ingredient4 = StringField('Fourth Ingredient')
    measure4 = StringField('Fourth Ingredient Amount')

    ingredient5 = StringField('Fifth Ingredient')
    measure5 = StringField('Fifth Ingredient Amount')

    ingredient6 = StringField('Sixth Ingredient')
    measure6 = StringField('Sixth Ingredient Amount')

    ingredient7 = StringField('Seventh Ingredient')
    measure7 = StringField('Seventh Ingredient Amount')

    ingredient8 = StringField('Eigth Ingredient')
    measure8 = StringField('Eigth Ingredient Amount')

    ingredient9 = StringField('Nineth Ingredient')
    measure9 = StringField('Nineth Ingredient Amount')

    ingredient10 = StringField('Tenth Ingredient')
    measure10 = StringField('Tenth Ingredient Amount')
