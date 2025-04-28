import unittest
from unittest.mock import patch, MagicMock
from app import app 

class TestAppFunctions(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    #faking the model and tokenizer to avoid loading them for real when testing
    @patch('routes.model.load_model') 
    @patch('routes.model.pickle.load')  
    def test_modelTesting(self, mock_pickle_load, mock_load_model):
        mock_model = MagicMock()
        mock_model.predict.return_value = [[0.1, 0.2, 0.3, 0.2, 0.2]] #possible return values
        mock_load_model.return_value = mock_model
        
        mock_tokenizer = MagicMock()
        mock_tokenizer.texts_to_sequences.return_value = [[1, 2, 3]]  #example of what the tokenizer would look like
        mock_pickle_load.return_value = mock_tokenizer

        response = self.app.post('/modelTesting', json={
            "reviewContent": "it was okay"
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), '3')  #change value depending on review type being tested

if __name__ == '__main__':
    unittest.main()
