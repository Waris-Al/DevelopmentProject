from flask import Blueprint
from database import highestRatedAlbums, allListenedAlbums
from dotenv import load_dotenv
import os
import requests


#Stuff to load database
load_dotenv(dotenv_path='env/.env')

spotifyClientID = os.getenv("spotifyClientID")
spotifyClientSecret = os.getenv("spotifyClientSecret")

recommendationAlgorithm = Blueprint('recommendationAlgorithm', __name__)


lastFMKey = os.getenv("lastFMKey")
albumToSearch = "LIFE IN HELL"
artistName = "Lancey Foux"



@recommendationAlgorithm.route('/testingRn')
def testingRn():
    reviewsToShow = highestRatedAlbums('shouldsave@bugfix.com')
    usersListenedAlbums = allListenedAlbums('mavsfan4l@test.com')  
    
    #now we need to go to the lastfm api, and get the tags.
    #then search for the top albums, ensuring that it hasn't already been heard  
    #make everything lowercase whilst comparing to avoid discrepancies between lastfm and spotify
    
    #next steps:
    #randomise an attribute and page number
    #grab album rec
    #move to next tag
    #stop at 4th
    #return all 4, embedd spotify link to the album
    
    searchAlbumTagsURL = f'https://ws.audioscrobbler.com/2.0/?method=album.getinfo&api_key={lastFMKey}&artist={artistName}&album={albumToSearch}&format=json'


    search_response1 = requests.get(searchAlbumTagsURL)
    tagName = ""
    for tag in search_response1.json()['album']['tags']['tag']:
        tagName = tag['name']
        print(tagName)

    searchTags = f'https://ws.audioscrobbler.com/2.0/?method=tag.gettopalbums&tag={tagName}&api_key={lastFMKey}&format=json&limit=50&page=1'
    
    
    

    
    search_response2 = requests.get(searchTags)
    
    for album in search_response2.json()['albums']['album']:
        if album['name'] not in usersListenedAlbums:
            print(album['name'] + " by " + album['artist']['name'])

    #print("Search Response:", search_response2.json())
    #print("Search Response:", search_response.json())
    
  
    return search_response2.json()
