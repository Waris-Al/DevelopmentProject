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

    @patch('routes.spotifyAuth.changeFavourites')
    def test_changeFavourites(self, mock_changeFavourites):
        with self.app as client:
            with client.session_transaction() as session:
                session['email'] = "test1324@test.com"
            response = client.post('/changeFavourites', json={
                "type" : "artist",
                "name": "Taylor Swift",
                "imageURL": "url.jpg"
            })
        self.assertEqual(response.status_code, 200)  #200 code means the request worked
        self.assertEqual(response.json, {
            "status": "success",
            "favourite": {
                "name": "Taylor Swift",
                "imageUrl": "url.jpg"
            }
        })

if __name__ == '__main__':
    unittest.main()
 
 #python -m unittest UnitTests/favouritesTests.py
 