"""SQLAlchemy models for Cocktail Application."""

from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()


def connect_db(app):
    """Connect this database to provided Flask app.
    Call from app.py.
    """

    db.app = app
    db.init_app(app)


class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    password = db.Column(
        db.Text,
        nullable=False
    )

    handle_recently_viewed_drink = db.relationship(
        "RecentlyViewedDrink",
        backref='user',
        passive_deletes=True
    )

    saved_drinks = db.relationship(
        "UserDrink",
        cascade="all,delete",
        backref='user',
        passive_deletes=True
    )

    recently_viewed_ingredients = db.relationship(
        "RecentlyViewedIngredient",
        backref='user',
        passive_deletes=True
    )

    def __repr__(self):
        u = self
        return f"<User #{u.id}: {u.username}, {u.email}>"

    @classmethod
    def signup(cls, username, email, password):
        """Sign up user.
        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`."""

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


class RecentlyViewedDrink(db.Model):
    """Save the users' recently viewed drinks"""

    __tablename__ = 'recently_viewed_drinks'

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )

    drink_id = db.Column(
        db.Integer,
        primary_key=True
    )


class RecentlyViewedIngredient(db.Model):
    """Save the users' recently viewed drinks"""

    __tablename__ = 'recenetly_viewed_ingredients'

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )

    ingredient = db.Column(
        db.Text,
        primary_key=True
    )


class UserDrink(db.Model):
    """User saved coktails"""

    __tablename__ = 'user_drinks'

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )

    drink_id = db.Column(
        db.Integer,
        primary_key=True
    )


class UserIngredient(db.Model):
    """User saved coktails"""

    __tablename__ = 'user_ingredients'

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        primary_key=True
    )

    ingredient = db.Column(
        db.Text,
        primary_key=True
    )


class Original(db.Model):
    """Original recipe made by a user"""

    __tablename__ = 'originals'

    idDrink = db.Column(
        db.Integer,
        primary_key=True
    )

    user = db.Column(
        db.Integer,
        db.ForeignKey("users.id")
    )

    strDrink = db.Column(
        db.Text
    )

    strVideo = db.Column(
        db.Text
    )

    strCategory = db.Column(
        db.Text
    )

    strIBA = db.Column(
        db.Text
    )

    strGlass = db.Column(
        db.Text
    )

    strInstructions = db.Column(
        db.Text
    )

    strDrinkThumb = db.Column(
        db.Text,
        default="/static/images/default-drink.png"
    )

    strIngredient1 = db.Column(
        db.Text
    )

    strMeasure1 = db.Column(
        db.Text
    )

    strIngredient2 = db.Column(
        db.Text
    )

    strMeasure2 = db.Column(
        db.Text
    )

    strIngredient3 = db.Column(
        db.Text
    )

    strMeasure3 = db.Column(
        db.Text
    )

    strIngredient4 = db.Column(
        db.Text
    )

    strMeasure4 = db.Column(
        db.Text
    )

    strIngredient5 = db.Column(
        db.Text
    )

    strMeasure5 = db.Column(
        db.Text
    )

    strIngredient6 = db.Column(
        db.Text
    )

    strMeasure6 = db.Column(
        db.Text
    )

    strIngredient7 = db.Column(
        db.Text
    )

    strMeasure7 = db.Column(
        db.Text
    )

    strIngredient8 = db.Column(
        db.Text
    )

    strMeasure8 = db.Column(
        db.Text
    )

    strIngredient9 = db.Column(
        db.Text
    )

    strMeasure9 = db.Column(
        db.Text
    )

    strIngredient10 = db.Column(
        db.Text
    )

    strMeasure10 = db.Column(
        db.Text
    )
