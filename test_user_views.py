import os
from unittest import TestCase
from models import User, Message, Follows, db
from flask import g

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY
db.create_all()

class UserViewsTestCase(TestCase):

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        test_user1 = User(username="TEST_USER1", 
                          email="TEST1@EMAIL.COM", 
                            image_url="TEST1_IMAGE",
                            header_image_url="TEST1_HEADER_IMAGE",
                            bio="TEST1 BIO",
                            location="TEST1 LOCATION",
                            password="test")
        
        db.session.add(test_user1)
        db.session.commit()

        self.user_id = test_user1.id
        

    def tearDown(Self):
        # super teardown?
        db.session.rollback()

    def test_list_users(self):
        with app.test_client() as client:
            response = client.get('/users')
            self.assertEqual(response.status_code, 200)

    def test_list_users(self):
        with app.test_client() as client:
            response = client.get(f'/users/{self.user_id}')
            self.assertEqual(response.status_code, 200)

    def test_list_nonexisting_users(self):
        with app.test_client() as client:
            response = client.get(f'/users/xxx')
            self.assertEqual(response.status_code, 404)

    def test_show_following(self):
        with app.test_client()as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.user_id
                response = client.get(f'/users/{self.user_id}/following')
                self.assertEqual(response.status_code, 200)
            