import unittest
import datetime
import json
from flask_bcrypt import Bcrypt
from flask_testing import TestCase
from app import app, db
from app.models import *

bcrypt = Bcrypt(app)

# use
# SQLALCHEMY_WARN_20=1 SQLALCHEMY_SILENCE_UBER_WARNING=1 python test_app.py
# in terminal, if too messy


class CustomTestResult(unittest.TextTestResult):
    def startTest(self, test):
        super().startTest(test)
        print(f"Running test: {test.id()} - {test.shortDescription()}")

    def addSuccess(self, test):
        super().addSuccess(test)
        print(f"  -> Passed")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        print(f"  -> Failed: {err[1]}")

    def addError(self, test, err):
        super().addError(test, err)
        print(f"  -> Error: {err[1]}")


class TestRegistration(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
        return app

    def setUp(self):
        db.create_all()
        self.client = app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_registration(self):
        """Test user registration."""
        response = self.client.post('/register', data=dict(
            username='testuser',
            password='testpassword',
            confirm_password='testpassword'
        ), follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b'Your account has been created! You can now log in.', response.data)

        # Check if the user is now in the database
        user = User.query.filter_by(username='testuser').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'testuser')


class TestLogin(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
        return app

    def setUp(self):
        db.create_all()
        self.client = app.test_client()

        # Create a test user for login
        hashed_password = bcrypt.generate_password_hash("testpassword")
        test_user = User(username='testuser', password=hashed_password)
        db.session.add(test_user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_login(self):
        """Test user login."""
        response = self.client.post('/login', data=dict(
            username='testuser',
            password='testpassword'
        ), follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        decoded_response = response.data.decode('utf-8')
        self.assertIn('Hello there', decoded_response)


class TestIncorrectLogin(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
        return app

    def setUp(self):
        db.create_all()
        self.client = app.test_client()

        # Create a test user for login
        hashed_password = bcrypt.generate_password_hash("testpassword")
        test_user = User(username='testuser', password=hashed_password)
        db.session.add(test_user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_login(self):
        """Test incorrect user login."""
        response = self.client.post('/login', data=dict(
            username='testuser',
            password='testpassword1'
        ), follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        decoded_response = response.data.decode('utf-8')
        self.assertIn(
            'Incorrect username or password. Please try again.', decoded_response)


class TestCreatePost(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
        return app

    def setUp(self):
        db.create_all()
        self.client = app.test_client()

        # Create a test user for posting
        hashed_password = bcrypt.generate_password_hash("testpassword")
        test_user = User(username='testuser', password=hashed_password)
        db.session.add(test_user)
        db.session.commit()

        # Log in the test user
        response = self.client.post('/login', data=dict(
            username='testuser',
            password='testpassword'
        ), follow_redirects=True)

        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_create_post(self):
        """Test creating a post."""
        response = self.client.post('/', data=dict(
            post='Test post'
        ), follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        # Check if the post is now in the database
        post = Post.query.filter_by(text='Test post').first()
        self.assertIsNotNone(post)
        self.assertEqual(post.text, 'Test post')

    def test_create_large_post(self):
        """Test creating a post with more than 15 characters."""
        response = self.client.post('/', data=dict(
            post='This is a test post with more than 15 characters.'
        ), follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        # Check if the error message is present in the response
        self.assertIn(
            b'Error: Post should be 15 characters or less.', response.data)

        # Check if the post is not in the database
        post = Post.query.filter_by(
            text='This is a test post with more than 15 characters.').first()
        self.assertIsNone(post)


class TestLikePost(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
        return app

    def setUp(self):
        db.create_all()
        self.client = app.test_client()

        # Create a test user for liking
        hashed_password = bcrypt.generate_password_hash("testpassword")
        test_user = User(username='testuser', password=hashed_password)
        db.session.add(test_user)
        db.session.commit()

        # Log in the test user
        response = self.client.post('/login', data=dict(
            username='testuser',
            password='testpassword'
        ), follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        # Create a test post for liking
        test_post = Post(text='Test post', owner_id=test_user.id,
                         timestamp=datetime.datetime.utcnow())
        db.session.add(test_post)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_like_post(self):
        """Test liking a post."""
        post = Post.query.filter_by(text='Test post').first()
        response = self.client.post(
            '/like', data=json.dumps({'post_id': post.id}), content_type='application/json')

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['status'], 'OK')
        self.assertEqual(data['likes'], 1)
        self.assertTrue(data['user_has_liked'])


class TestReplyPost(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
        return app

    def setUp(self):
        db.create_all()
        self.client = app.test_client()

        # Create a test user for replying
        hashed_password = bcrypt.generate_password_hash("testpassword")
        test_user = User(username='testuser', password=hashed_password)
        db.session.add(test_user)
        db.session.commit()

        # Log in the test user
        response = self.client.post('/login', data=dict(
            username='testuser',
            password='testpassword'
        ), follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        # Create a test post for replying
        test_post = Post(text='Test post', owner_id=test_user.id,
                         timestamp=datetime.datetime.utcnow())
        db.session.add(test_post)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_reply_post(self):
        """Test replying to a post."""
        post = Post.query.filter_by(text='Test post').first()
        response = self.client.post(f'/reply_post/{post.id}', data=dict(
            post='Test reply'
        ), follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        # Check if the reply is now in the database
        reply = Reply.query.filter_by(text='Test reply').first()
        self.assertIsNotNone(reply)
        self.assertEqual(reply.text, 'Test reply')

    def test_reply_large_post(self):
        """Test replying with more than 15 characters."""
        post = Post.query.filter_by(text='Test post').first()
        # Attempt to reply with more than 15 characters
        response = self.client.post(f'/reply_post/{post.id}', data=dict(
            post='This is a test reply with more than 15 characters.'
        ), follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        # Check if the error message is present in the response
        self.assertIn(
            b'Error: Reply should be 15 characters or less.', response.data)

        # Check if the reply is not in the database
        reply = Reply.query.filter_by(
            text='This is a test reply with more than 15 characters.').first()
        self.assertIsNone(reply)


class TestDeleteReply(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
        return app

    def setUp(self):
        db.create_all()
        self.client = app.test_client()

        # Create a test user for replying and deleting replies
        hashed_password = bcrypt.generate_password_hash("testpassword")
        test_user = User(username='testuser', password=hashed_password)
        db.session.add(test_user)
        db.session.commit()

        # Log in the test user
        response = self.client.post('/login', data=dict(
            username='testuser',
            password='testpassword'
        ), follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        # Create a test post for replying
        test_post = Post(text='Test post', owner_id=test_user.id,
                         timestamp=datetime.datetime.utcnow())
        db.session.add(test_post)
        db.session.commit()

        # Create a test reply
        test_reply = Reply(text='Test reply', owner_id=test_user.id,
                           parent_id=test_post.id, 
                           timestamp=datetime.datetime.utcnow())
        db.session.add(test_reply)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_delete_reply(self):
        """Test deleting a reply."""
        reply = Reply.query.filter_by(text='Test reply').first()
        response = self.client.post(
            f'/delete_reply/{reply.id}', follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        # Check if the reply is now deleted from the database
        deleted_reply = Reply.query.filter_by(text='Test reply').first()
        self.assertIsNone(deleted_reply)


class TestDeletePost(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
        return app

    def setUp(self):
        db.create_all()
        self.client = app.test_client()

        # Create a test user for deleting posts
        hashed_password = bcrypt.generate_password_hash("testpassword")
        test_user = User(username='testuser', password=hashed_password)
        db.session.add(test_user)
        db.session.commit()

        # Log in the test user
        response = self.client.post('/login', data=dict(
            username='testuser',
            password='testpassword'
        ), follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        # Create a test post
        test_post = Post(text='Test post', owner_id=test_user.id,
                         timestamp=datetime.datetime.utcnow())
        db.session.add(test_post)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_delete_post(self):
        """Test deleting a post."""
        post = Post.query.filter_by(text='Test post').first()
        response = self.client.post(
            f'/delete_post/{post.id}', follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        # Check if the post is now deleted from the database
        deleted_post = Post.query.filter_by(text='Test post').first()
        self.assertIsNone(deleted_post)


class TestChangeEmoji(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
        return app

    def setUp(self):
        db.create_all()
        self.client = app.test_client()

        # Create a test user for changing the emoji
        hashed_password = bcrypt.generate_password_hash("testpassword")
        test_user = User(username='testuser', password=hashed_password)
        db.session.add(test_user)
        db.session.commit()

        # Log in the test user
        response = self.client.post('/login', data=dict(
            username='testuser',
            password='testpassword'
        ), follow_redirects=True)

        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_change_emoji(self):
        """Test changing the emoji for a user."""
        response = self.client.post('/change_emoji', data=dict(
            emoji='😊'
        ), follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        # Check if the emoji for the user is now changed in the database
        user = User.query.filter_by(username='testuser').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.emoji, '😊')


class TestSearch(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
        return app

    def setUp(self):
        db.create_all()
        self.client = app.test_client()

        # Create a test user
        hashed_password = bcrypt.generate_password_hash("testpassword")
        test_user = User(username='testuser', password=hashed_password)
        db.session.add(test_user)
        db.session.commit()

        # Log in the test user
        response = self.client.post('/login', data=dict(
            username='testuser',
            password='testpassword'
        ), follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        # Create test posts
        test_post1 = Post(text='keyword', owner_id=test_user.id,
                          timestamp=datetime.datetime.utcnow())
        test_post2 = Post(text='guac', owner_id=test_user.id,
                          timestamp=datetime.datetime.utcnow())
        db.session.add(test_post1)
        db.session.add(test_post2)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_search(self):
        """Test the search functionality."""
        response = self.client.get(
            '/search?query=keyword', follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        # Check if the search results contain the expected post
        self.assertIn(b'keyword', response.data)
        self.assertNotIn(b'guac', response.data)


class TestLogout(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
        return app

    def setUp(self):
        db.create_all()
        self.client = app.test_client()

        # Create a test user
        hashed_password = bcrypt.generate_password_hash("testpassword")
        test_user = User(username='testuser', password=hashed_password)
        db.session.add(test_user)
        db.session.commit()

        # Log in the test user
        response = self.client.post('/login', data=dict(
            username='testuser',
            password='testpassword'
        ), follow_redirects=True)

        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_logout(self):
        """Test user logout."""
        # Log out the user
        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Check if the user is no longer authenticated
        with self.client as c:
            response = c.get('/profile', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Login Page', response.data)

class TestFollowUser(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
        return app

    def setUp(self):
        db.create_all()
        self.client = app.test_client()

        # Create a test user for following
        hashed_password = bcrypt.generate_password_hash("testpassword")
        test_user = User(username='testuser', password=hashed_password)
        db.session.add(test_user)
        db.session.commit()

        # Log in the test user
        response = self.client.post('/login', data=dict(
            username='testuser',
            password='testpassword'
        ), follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        # Create another test user to be followed
        hashed_password = bcrypt.generate_password_hash("testpassword2")
        user_to_follow = User(username='user_to_follow', password=hashed_password)
        db.session.add(user_to_follow)
        db.session.commit()

        # new user makes post
        test_post = Post(text='Test post', owner_id=user_to_follow.id,
                            timestamp=datetime.datetime.utcnow())
        db.session.add(test_post)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_follow_user(self):
        """Test following a user."""
        user_to_follow = User.query.filter_by(username='user_to_follow').first()
        test_user = User.query.filter_by(username='testuser').first()
        
        # Ensure that the user is not initially followed
        self.assertFalse(Follow.query.filter_by(
            follower_id=test_user.id, followed_id=user_to_follow.id).first())

        # find the test post
        test_post = Post.query.filter_by(text='Test post').first()

        # Follow the user
        response = self.client.post('/follow', data=json.dumps({'post_id': test_post.id}), content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['status'], 'OK')
        self.assertTrue(data['user_has_followed'])

        # Check if the follow relationship is now in the database
        follow_relationship = Follow.query.filter_by(
            follower_id=test_user.id, followed_id=user_to_follow.id).first()
        self.assertIsNotNone(follow_relationship)



if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestRegistration)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLogin))
    suite.addTests(unittest.TestLoader(
    ).loadTestsFromTestCase(TestIncorrectLogin))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCreatePost))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLikePost))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestReplyPost))
    suite.addTests(unittest.TestLoader(
    ).loadTestsFromTestCase(TestDeleteReply))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDeletePost))
    suite.addTests(unittest.TestLoader(
    ).loadTestsFromTestCase(TestChangeEmoji))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSearch))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLogout))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFollowUser))
    unittest.TextTestRunner(resultclass=CustomTestResult).run(suite)
