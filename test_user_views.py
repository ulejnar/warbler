import os
from unittest import TestCase
from models import User, Message, Follows, db
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY
db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

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
        
        test_user2 = User(username="TEST_USER2", 
                          email="TEST2@EMAIL.COM", 
                            image_url="TEST2_IMAGE",
                            header_image_url="TEST2_HEADER_IMAGE",
                            bio="TEST2 BIO",
                            location="TEST2 LOCATION",
                            password="test")


        db.session.add_all([test_user1, test_user2])
        db.session.commit()

        self.user_id = test_user1.id
        self.other_user_id = test_user2.id
        

    def tearDown(Self):
        # super teardown?
        db.session.rollback()


    def test_signup(self):
        "Does GET /signup show the signup form?"
        with app.test_client() as client:
            response = client.get('/signup')
            self.assertEqual(response.status_code, 200)


    def test_login(self):
        "Does GET /login show the login form?"
        with app.test_client() as client:
            response = client.get('/login')
            self.assertEqual(response.status_code, 200)


    def test_logout(self):
        "Does GET /logout redirect home?"
        with app.test_client() as client:
            response = client.get('/logout')
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.location, "http://localhost/")


    def test_list_users(self):
        "Does GET /users show the list of users?"
        with app.test_client() as client:
            response = client.get('/users')
            self.assertEqual(response.status_code, 200)


    def test_user_detail(self):
        "Does GET /users/<user-id> show the details of that user?"
        with app.test_client() as client:
            response = client.get(f'/users/{self.user_id}')
            self.assertEqual(response.status_code, 200)


    def test_list_nonexisting_users(self):
        """Does GET /users/<user-id> for a user ID that doesn't exist
        give us an error page?"""
        with app.test_client() as client:
            response = client.get(f'/users/xxx')
            self.assertEqual(response.status_code, 404)


    def test_show_following(self):
        "Does GET /users/<user-id>/following show a list of following users?"
        with app.test_client()as client:
            with client.session_transaction() as session:    
                session[CURR_USER_KEY] = self.user_id
            
            response = client.get(f'/users/{self.user_id}/following')
            
            self.assertEqual(response.status_code, 200)


    def test_redirect_following(self):
        "Does GET /users/<user-id>/following with no user.id in the session redirects us to the homepage so we can't access the list of following users?"
        with app.test_client()as client:
            response = client.get(f'/users/{self.user_id}/following')
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.location, "http://localhost/")

    

    def test_show_followers(self):
        "Does GET /users/<user-id>/followers show a list of follower users?"
        with app.test_client()as client:
            with client.session_transaction() as session:    
                session[CURR_USER_KEY] = self.user_id
            
            response = client.get(f'/users/{self.user_id}/followers')
            
            self.assertEqual(response.status_code, 200)

    
    def test_user_following(self):
        """Does POST /users/follow/<follow_id> add the user to our
        followed users?"""
        with app.test_client()as client:
            with client.session_transaction() as session:    
                session[CURR_USER_KEY] = self.user_id
            
            response = client.post(f'/users/follow/{self.other_user_id}', follow_redirects=True)
            
            testuser = User.query.get(self.user_id)
            followed = User.query.get(self.other_user_id)

            self.assertEqual(response.status_code, 200)
            self.assertEqual(testuser.is_following(followed), True)
    

    def test_user_stop_following(self):
        """Does POST /users/follow/<follow_id> remove the followed user 
        from our followed users?"""
        with app.test_client()as client:
            with client.session_transaction() as session:    
                session[CURR_USER_KEY] = self.user_id
            
            client.post(f'/users/follow/{self.other_user_id}')
            response = client.post(f'/users/stop-following/{self.other_user_id}', follow_redirects=True)
            
            testuser = User.query.get(self.user_id)
            followed = User.query.get(self.other_user_id)

            self.assertEqual(response.status_code, 200)
            self.assertEqual(testuser.is_following(followed), False)
            
    
    def test_show_user_profile(self):
        """Does GET /users/profile show the edit user profile form? """
        with app.test_client()as client:
            with client.session_transaction() as session:    
                session[CURR_USER_KEY] = self.user_id
            
            response = client.get('/users/profile')
            html = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn('<form method="POST" id="user_form">', html)

    
    def test_submit_user_profile(self):
        """Does POST /users/profile submit the form data?"""
        with app.test_client()as client:
            with client.session_transaction() as session:    
                session[CURR_USER_KEY] = self.user_id
            
            test_user = User.query.get(self.user_id)
            test_user.password = bcrypt.generate_password_hash("test").decode('UTF-8')

            form_data = {
                         "username": "TESTCHANGE",
                         "email": "CHANGE@EMAIL.COM",
                         "password": "test",
                        }

            response = client.post('/users/profile', data=form_data, follow_redirects=True)
            
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(db.session.query(User.username).filter(User.username == "TESTCHANGE").first()), 1)
