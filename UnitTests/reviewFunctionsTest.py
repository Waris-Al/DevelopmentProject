import unittest
from unittest.mock import patch, MagicMock
from flask import session
from app import app  # Import your Flask app here
import json

class TestAppFunctions(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    @patch('app.addReview')
    def test_addReview(self, mock_addReview):
        mock_addReview.return_value = True
        
        with self.app as client:
            response = client.post('/save_review', json={
               "user_email": "covenec@mailinator.com",
               "review_data": {
                   "date_listened": "2025-12-23",
                   "review": "it was alright"
               },
               "username": "kennykungfu"
            })
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, "Review added for kennykungfu covenec@mailinator.com")
    
    @patch('app.editReview')
    def test_editReview(self, mock_editReview):
        mock_editReview.return_value = True
        
        with self.app as client:
            response = client.post('editReview', json={
               "date_listened": "2025-12-23",
               "review": "it was alright",
               "reviewID": "1" 
            })
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.json)

    @patch('app.deleteReview')
    def test_deleteReview(self, mock_deleteReview):
        # Mock the database delete operation
        mock_deleteReview.return_value = True

        # Test the function
        with self.app as client:
            response = client.post('/deleteReview', json={
                "review_id": "1"
            })
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.json)

if __name__ == '__main__':
    unittest.main()
 
 #python -m unittest UnitTests/reviewFunctionsTest.py
 