from flask import Blueprint
from database import highestRatedAlbums, allListenedAlbums
from dotenv import load_dotenv
import os
import requests


load_dotenv(dotenv_path='env/.env') #Access env variables

# Spotify API credentials
spotifyClientID = os.getenv("spotifyClientID")
spotifyClientSecret = os.getenv("spotifyClientSecret")

recommendationAlgorithm = Blueprint('recommendationAlgorithm', __name__)


lastFMKey = os.getenv("lastFMKey")
albumToSearch = "LIFE IN HELL"
artistName = "Lancey Foux"


'''
Function that contains the bulk of the recommendation algorithm
This algorithm works by taking any album the user has rated 4 or more stars, and finding the genres of each of these albums.
It will then search for similar albums in those genres, ideally ones with cross over and return the recommendations.
To avoid the same recommendations constantly, the algorithm uses randomness with what albums come back.
'''
@recommendationAlgorithm.route('/testingRn')
def testingRn():
    
    #Getting the users highly rated albums, and a list of all the albums they've listened to to avoid duplicates in recommendation
    usersTopRatedAlbums = highestRatedAlbums('shouldsave@bugfix.com') #we may need to add randomness to this too
    usersListeningHistory = allListenedAlbums('mavsfan4l@test.com')  
    
    #make everything lowercase whilst comparing to avoid discrepancies between lastfm and spotify
    #next steps:
    #randomise an attribute and page number
    #grab album rec
    #move to next tag
    #stop at 4th
    #return all 4, embedd spotify link to the album
    
    #Using the lastFM API to get an the genres (called tags on the API) of the albums the user has rated highly, and then getting albums in these genres
    getAlbumGenres = f'https://ws.audioscrobbler.com/2.0/?method=album.getinfo&api_key={lastFMKey}&artist={artistName}&album={albumToSearch}&format=json'

    relevantGenres = requests.get(getAlbumGenres)
    tagName = "" #tags are genres
    for tag in relevantGenres.json()['album']['tags']['tag']:
        tagName = tag['name']
        print(tagName)

    similarAlbums = f'https://ws.audioscrobbler.com/2.0/?method=tag.gettopalbums&tag={tagName}&api_key={lastFMKey}&format=json&limit=50&page=1'
    
    
    

    #Here we check to make sure the albums we're recommending haven't been heard before
    foundRecs = requests.get(similarAlbums)
    for album in foundRecs.json()['albums']['album']:
        if album['name'] not in usersListeningHistory:
            print(album['name'] + " by " + album['artist']['name'])
    
  
    return foundRecs.json()
