import unittest
from unittest.mock import patch, MagicMock
from routes.spotifyAuth import spotifyAuthBP
from bson import ObjectId
from flask import Flask, jsonify
from database import #include relevant ones in here
app = Flask(__name__)

class TestMessagingServices(unittest.TestCase):
    def setUp(self):
         self.app_context = app.app_context()
         self.app_context.push()
 
    def tearDown(self):
        self.app_context.pop()
    
    
    #example of a unit test    
    @patch('routes.messaging.loadMessages')
    def test1(self, mock_function):
        #actual unit test code in here

        
        
if __name__ == '__main__':
     unittest.main()
     
 
 #python -m unittest UnitTests/test_file.py