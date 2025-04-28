import unittest
from unittest.mock import patch, MagicMock
from flask import session
from app import app
import json

class TestAutoLogListenedAlbums(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    
    '''This is testing the auto log functionality'''
    #mocking some functions that are used inside autoLogListenedAlbums
    @patch('routes.spotifyAuth.requests.get') 
    @patch('routes.spotifyAuth.mostRecentReview')  
    def test_autoLogListenedAlbums(self, mock_mostRecentReview, mock_requests_get):
        with self.app as client:
            with client.session_transaction() as sess:
                #setting the relevant session vars
                sess['email'] = "test1324@test.com"
                sess['token_info'] = {"access_token": "fake_token"}

            mock_mostRecentReview.return_value = {
                "album_name": "Speak Now" #example album
            }

            #fake example of what the spotify API would come back with. the real function has to sift through a lot
            #more than this, but given that this is the only data the function uses, we only need to fake this
            fake_spotify_data = {
                "items": [
                    {
                        "track": {
                            "album": {
                                "name": "albumName",
                                "artists": [{"name": "artistName"}]
                            }
                        },
                        "played_at": "2024-04-27T12:34:56.789Z",
                        "context": {"type": "album"}
                    }
                ]
            }

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = fake_spotify_data
            mock_requests_get.return_value = mock_response

            response = client.get('/autoLogListenedAlbums')

            #checking that the redirect worked
            self.assertEqual(response.status_code, 302)
            self.assertIn('/save_review', response.location)

            #Checking that session vars were set
            with client.session_transaction() as sess:
                self.assertTrue(sess.get('autologgedReviews'))
                self.assertIsNotNone(sess.get('review_json'))
                self.assertEqual(sess['review_json'][0]['albumName'], 'albumName')



    '''This is testing the recommendation algorithm'''
    #this test currently exposes a flaw in the algorithm, that if the attribute selected is out of index the system crashes
    @patch('routes.recommendations.requests.get') 
    @patch('routes.recommendations.highestRatedAlbums')
    @patch('routes.recommendations.allListenedAlbums') 
    @patch('routes.recommendations.random.randrange', return_value=0)  #need to not randomly select a returned album for testing sake
    def test_recommend_albums_success(self, mock_allListenedAlbums, mock_highestRatedAlbums, mock_requests_get, mock_randrange):
        with self.app as client:
            with client.session_transaction() as sess:
                sess['email'] = "test1324@test.com"


            mock_allListenedAlbums.return_value = ["album1", "album2"]


            mock_highestRatedAlbums.return_value = [
                ("topAlbum1", "topArtist1"),
                ("topAlbum2", "topArtist2")
            ]

            #example of the API response from lastFM (well simulating the details we need, not the rest of the fluff)
            genre_response = MagicMock()
            genre_response.json.return_value = {
                "album": {
                    "tags": {
                        "tag": [
                            {"name": "rap"},
                            {"name": "hip-hop"}
                        ]
                    }
                }
            }

            #Trying to mock 4 returned albums that we'll then recommend
            similar_album_response = MagicMock()
            similar_album_response.json.return_value = {
                "albums": {
                    "album": [
                        {
                            "name": "recommendAlbum1",
                            "artist": {"name": "artist1"},
                            "image": [
                                {}, {}, {"#text": "imageurl1.jpg"}
                            ],
                            "@attr": {"rank": "1"}
                        },
                        {
                            "name": "recommendAlbum2",
                            "artist": {"name": "artist2"},
                            "image": [
                                {}, {}, {"#text": "imageurl2.jpg"}
                            ],
                            "@attr": {"rank": "2"}
                        },
                        {
                            "name": "recommendAlbum3",
                            "artist": {"name": "artist3"},
                            "image": [
                                {}, {}, {"#text": "imageurl3.jpg"}
                            ],
                            "@attr": {"rank": "3"}
                        },
                        {
                            "name": "recommendAlbum4",
                            "artist": {"name": "artist4"},
                            "image": [
                                {}, {}, {"#text": "imageurl4.jpg"}
                            ],
                            "@attr": {"rank": "4"}
                        }
                    ] 
                }
            }

            mock_requests_get.side_effect = [genre_response, genre_response, 
                                            similar_album_response, similar_album_response,
                                            similar_album_response, similar_album_response]  


            response = client.get('/recommendAlbums')

            self.assertEqual(response.status_code, 200)

            response_data = json.loads(response.data)
            #checking that the recommendation is formated properly
            first_album = response_data['albums']['album'][0]
            self.assertIn('name', first_album)
            self.assertIn('artist', first_album)
            self.assertIn('thumbnail', first_album)




if __name__ == '__main__':
    unittest.main()
 #python -m unittest UnitTests/externalAPIFunctionsTests.py