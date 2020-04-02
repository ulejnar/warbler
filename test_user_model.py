"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from flask_bcrypt import Bcrypt
from models import db, User, Message, Follows
from sqlalchemy import exc

bcrypt = Bcrypt()

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        #Test hashing?
        # USER1_PWD = bcrypt.generate_password_hash("test").decode('UTF-8')
        # USER2_PWD = bcrypt.generate_password_hash("secret").decode('UTF-8')

        test_user1 = User(username="TEST_USER1", 
                          email="TEST1@EMAIL.COM", 
                          image_url="TEST1_IMAGE",
                          header_image_url="TEST1_HEADER_IMAGE",
                          bio="TEST1 BIO",
                          location="TEST1 LOCATION",
                          password="test")
        
        test_user2 = User(username="TEST_USER2", 
                          email="TEST2@EMAIL.COM", 
                          image_url="TEST2_IMAGE",
                          header_image_url="TEST2_HEADER_IMAGE",
                          bio="TEST2 BIO",
                          location="TEST2 LOCATION",
                          password="secret")

        db.session.add(test_user1)
        db.session.add(test_user2)
        db.session.commit()

        self.client = app.test_client()

    def tearDown(Self):
        # super teardown?
        db.session.rollback()

    def test_user_model(self):
        """Does basic model work?"""

        u = User.query.filter(User.username == "TEST_USER1").first()
        u_id = u.id
        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
        self.assertEqual(len(u.likes), 0)
        self.assertEqual(len(u.following), 0)
        self.assertEqual(u.__repr__(), f"<User #{u_id}: TEST_USER1, TEST1@EMAIL.COM>") #better way to test id?
    
    def test_is_following(self):
        "Does is following detect when a user follows another?"

        user1 = User.query.filter(User.username == "TEST_USER1").first()
        user2 = User.query.filter(User.username == "TEST_USER2").first()

        test_follow = Follows(user_being_followed_id=user1.id,
                              user_following_id=user2.id)
        
        db.session.add(test_follow)
        db.session.commit()

        self.assertEqual(user2.is_following(user1), True)
        self.assertEqual(user1.is_following(user2), False)

    def test_is_followed_by(self):
        """Does is followed by detects when a user is followed by another user and when a user is not followed by another user"""

        user1 = User.query.filter(User.username == "TEST_USER1").first()
        user2 = User.query.filter(User.username == "TEST_USER2").first()

        test_follow = Follows(user_being_followed_id=user1.id,
                              user_following_id=user2.id)
        
        db.session.add(test_follow)
        db.session.commit()

        self.assertEqual(user1.is_followed_by(user2), True)
        self.assertEqual(user2.is_followed_by(user1), False)

    def test_user_authenticate(self):
        """Does authneticate return a user object when given a valid username and password and return Flase when giving a wrong password or username"""

        user1 = User.query.filter(User.username == "TEST_USER1").first()

        user1.password = bcrypt.generate_password_hash("test").decode('UTF-8')

        self.assertEqual(User.authenticate(user1.username, "test"), user1)
        self.assertEqual(User.authenticate(user1.username, "xxxx"), False)
        self.assertEqual(User.authenticate("userX", "test"), False)

    def test_signup_positive(self):
        """does signup() successfully create a new user with valid credentials?"""

        user_new = User.signup("BHill", "bhill@gmail.com", "password", "www.xsd.com")

        db.session.commit()

        #print("user object print:", User.query.filter(User.username == "BHill").first())

        test_user = User.query.filter(User.username == "BHill").first() 

        # Test that new user with proper username appears in DB
        self.assertEqual(test_user.username, "BHill")

        # Test that new user has properly encoded password
        self.assertEqual(bcrypt.check_password_hash(test_user.password, "password"), True)


        # def signup(cls, username, email, password, image_url)


    def test_signup_negative(self):
        """does signup() fail to create a new user with invalid credentials?"""

        user_new = User.signup("TEST_USER1", "bhill@gmail.com", "password", "www.xsd.com")

        # Test that user with non-unique username is rejected  
        self.assertRaises(exc.IntegrityError, db.session.commit)

        db.session.rollback()

        user_new = User.signup(None, "bhill@gmail.com", "password", "www.xsd.com")

        # Test that user with no username is rejected  
        self.assertRaises(exc.IntegrityError, db.session.commit)
    
        db.session.rollback()

        user_new = User.signup("BHill", "TEST1@EMAIL.COM", "password", "www.xsd.com")

        # Test that user with non-unique email is rejected
        self.assertRaises(exc.IntegrityError, db.session.commit)

        db.session.rollback()

        user_new = User.signup("BHill", None, "password", "www.xsd.com")
        
        # Test that user with no email is rejected
        self.assertRaises(exc.IntegrityError, db.session.commit)
        
        #user_new = User.signup("BHill", "bhill@gmail.com", None, "www.xsd.com")
        
        # Test that user with no password is rejected
        with self.assertRaises(ValueError):
            User.signup("BHill", "bhill@gmail.com", None, "www.xsd.com")
            





