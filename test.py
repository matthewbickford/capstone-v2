"""Model tests."""

# run these tests like:
# python -m unittest test.py

from app import app
import os
from unittest import TestCase

from models import db, connect_db, User, RecentlyViewedDrink, RecentlyViewedIngredient, UserDrink, UserIngredient, Original

os.environ["DATABASE_URL"] = "postgresql:///cocktails_test"

db.drop_all()
db.create_all()


class UserModelTestCase(TestCase):
    """Test user model"""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        u1 = User.signup("test1", "email1@email.com", "password")
        uid1 = 1111
        u1.id = uid1

        u2 = User.signup("test2", "email2@email.com", "password")
        uid2 = 2222
        u2.id = uid2

        db.session.commit()

        u1 = User.query.get(uid1)
        u2 = User.query.get(uid2)

        self.u1 = u1
        self.uid1 = uid1

        self.u2 = u2
        self.uid2 = uid2

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does basic model work?"""

        user1 = User(
            email="test@test.com", username="testuser", password="HASHED_PASSWORD"
        )

        db.session.add(user1)
        db.session.commit()

        # User should have no saved drinks or ingredients
        self.assertEqual(len(user1.saved_drinks), 0)
        self.assertEqual(len(user1.recently_viewed_ingredients), 0)

    def test_repr(self):
        """Does the repr method work as expected?"""

        user1 = User(
            email="test@test.com", username="testuser", password="HASHED_PASSWORD"
        )

        db.session.add(user1)
        db.session.commit()

        # User repr should match
        self.assertEqual(
            repr(user1), f"<User #{user1.id}: {user1.username}, {user1.email}>"
        )

    def test_signup_user(self):
        """Does User.create successfully create new user when given valid credentials?"""

        new_user = User.signup(
            "new_user", "testemail@email.com", "password")
        uid = 666
        new_user.id = uid

        db.session.commit()

        self.assertTrue(new_user)

        u_test = User.query.get(uid)
        self.assertIsNotNone(u_test)
        self.assertEqual(u_test.username, "new_user")
        self.assertEqual(u_test.email, "testemail@email.com")
        self.assertNotEqual(u_test.password, "password")

    def test_valid_authentication(self):
        u = User.authenticate(self.u1.username, "password")
        self.assertIsNotNone(u)
        self.assertEqual(u.id, self.uid1)

    def test_invalid_username(self):
        self.assertFalse(User.authenticate("badusername", "password"))

    def test_wrong_password(self):
        self.assertFalse(User.authenticate(self.u1.username, "badpassword"))


