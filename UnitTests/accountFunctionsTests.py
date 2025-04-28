import unittest
from unittest.mock import patch, MagicMock
from flask import session
from app import app  
import json

class TestAppFunctions(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

            
    @patch('app.Login')
    def test_Login(self, mock_Login):
        with self.app as client:
            response = client.post('/Login', data={
                "email": "mavsfan4l@test.com",
                "password": "test123"
            })
            self.assertEqual(response.status_code, 302) #302 code means we were able to redirect
            self.assertEqual(response.location, '/Homepage') #checking that we get back a redirect to Homepage
        

    @patch('app.registerUser')  # Mock only registerUser
    def test_Register(self, mock_registerUser):
        with self.app as client:
            
            with client.session_transaction() as session:
                session['favourites'] = ["album", "song", "artist"]
            
            response = client.post('/Register', data={
                "email": "testuser@test.com",
                "name": "Test User",
                "username": "testuser",
                "password": "test123"
                })
            
        self.assertEqual(response.status_code, 302) #302 code means we were able to redirect
        self.assertEqual(response.location, '/Homepage') #checking that we get back a redirect to Homepage

    @patch('app.followUser')
    def test_followUser(self, mock_followUser):
        with self.app as client:
            with client.session_transaction() as session:
                session['email'] = ["covenec@mailinator.com"]  #followerEmail comes from the session
            response = client.post('/followUser', json={
                "followeeEmail": "kate@mailinator.com"
            })
        self.assertEqual(response.status_code, 200)  # 200 code means the request was successful
        self.assertEqual(response.json, {"message": "Followed successfully!"})  # checking the response message
    
if __name__ == '__main__':
    unittest.main()
 
 #python -m unittest UnitTests/accountFunctionsTests.py
 