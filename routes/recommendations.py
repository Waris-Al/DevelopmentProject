from flask import Blueprint, jsonify, session
from database import highestRatedAlbums, allListenedAlbums
from dotenv import load_dotenv
import os
import requests
import random


load_dotenv(dotenv_path='env/.env') #Access env variables

# Spotify API credentials
spotifyClientID = os.getenv("spotifyClientID")
spotifyClientSecret = os.getenv("spotifyClientSecret")

recommendationAlgorithm = Blueprint('recommendationAlgorithm', __name__)


lastFMKey = os.getenv("lastFMKey")



'''
Function that contains the bulk of the recommendation algorithm
This algorithm works by taking any album the user has rated 4 or more stars, and finding the genres of each of these albums.
It will then search for similar albums in those genres, ideally ones with cross over and return the recommendations.
To avoid the same recommendations constantly, the algorithm uses randomness with what albums come back.
'''
@recommendationAlgorithm.route('/recommendAlbums')
def recommendAlbums():
    
    #WARIS: WE'RE MAKING MULTIPLE API CALLS, DO NOT KEEP IT LIKE THIS, EITHER RUN THEM CONCURRENTLY OR FIND ANOTHER WAY
    
    usersListeningHistory = allListenedAlbums(session['email']) #this is a list of all the albums the user has listened to, we need this to avoid duplicates in recommendations
    listOfGenres = {}
    #Getting the users highly rated albums, and a list of all the albums they've listened to to avoid duplicates in recommendation
    usersTopRatedAlbums = highestRatedAlbums(session['email']) #we may need to add randomness to this too
    
    for album in usersTopRatedAlbums:
        albumToSearch = album[0] 
        artistName = album[1]

        #make everything lowercase whilst comparing to avoid discrepancies between lastfm and spotify
        #next steps:
        #randomise an attribute and page number
        #grab album rec
        #move to next tag
        #stop at 4th
        #return all 4, embedd spotify link to the album
        
        #Using the lastFM API to get an the genres (called tags on the API) of the albums the user has rated highly, and then getting albums in these genres
        getAlbumGenres = f'https://ws.audioscrobbler.com/2.0/?method=album.getinfo&api_key={lastFMKey}&artist={artistName}&album={albumToSearch}&format=json' #change how this is done, too many API calls rn

        relevantGenres = requests.get(getAlbumGenres)
        
        tagName = "" #tags are genres
        
        if relevantGenres.json()["album"]["tags"] == "":
            print("No tags found for this album, moving on")
        else:
            for tag in relevantGenres.json()["album"]["tags"]["tag"]:
                tagName = tag['name']

                if tagName in listOfGenres:
                    listOfGenres[tagName] += 1
                else:  
                    listOfGenres[tagName] = 1
                
        
    sortedGenreList = sorted(listOfGenres.items(), key=lambda item: item[1], reverse=True)
    print("List of Genres: ", sortedGenreList)
    

    valid_recommendations = []
    for i in range(4):
        tagToSearchWith = sortedGenreList[i][0]
        #print("Tag to search with: ", tagToSearchWith)
        similarAlbums = f'https://ws.audioscrobbler.com/2.0/?method=tag.gettopalbums&tag={tagToSearchWith}&api_key={lastFMKey}&format=json&limit=50&page=1'
        
        
        #album['@attr']['rank'] == '2'
        #Here we check to make sure the albums we're recommending haven't been heard before
        foundRecs = requests.get(similarAlbums)
        albumToRandomlyRecommend = random.randrange(1,50)
        
            
        album = foundRecs.json()['albums']['album'][albumToRandomlyRecommend]

        # Check if it hasn't been listened to and the rank matches
        if album['name'] not in usersListeningHistory and album['@attr']['rank'] == str(albumToRandomlyRecommend + 1):
            valid_recommendations.append({
                'name': album['name'],
                'artist': album['artist']['name']
            })


    return jsonify({
        'albums': {
            'album': valid_recommendations
        }
    })
