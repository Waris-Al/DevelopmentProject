from flask import Blueprint
from database import highestRatedAlbums, allListenedAlbums
from dotenv import load_dotenv
import os
from datetime import datetime


#Stuff to load database
load_dotenv(dotenv_path='env/.env')

spotifyClientID = os.getenv("spotifyClientID")
spotifyClientSecret = os.getenv("spotifyClientSecret")

recommendationAlgorithm = Blueprint('recommendationAlgorithm', __name__)

@recommendationAlgorithm.route('/testingRn')
def testingRn():
    reviewsToShow = highestRatedAlbums('shouldsave@bugfix.com')
    
    #now we need to go to the lastfm api, and get the tags.
    #then search for the top albums, ensuring that it hasn't already been heard  
    
    usersListenedAlbums = allListenedAlbums('mavsfan4l@test.com')   
    return usersListenedAlbums
