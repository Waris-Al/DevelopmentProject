from flask import render_template, url_for, request, redirect, session, jsonify, json, Blueprint
from database import editFavourite, mostRecentReview
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
import os
import requests
import base64
from datetime import datetime
import time

#Stuff to load database
load_dotenv(dotenv_path='env/.env')

spotifyClientID = os.getenv("spotifyClientID")
spotifyClientSecret = os.getenv("spotifyClientSecret")




spotifyAuthBP = Blueprint('spotifyAuth', __name__)


REDIRECT_URI = "http://127.0.0.1:5000/callback" 


SCOPE = "user-top-read user-read-playback-state user-read-currently-playing user-read-recently-played"



sp_oauth = SpotifyOAuth(client_id=spotifyClientID,
                        client_secret=spotifyClientSecret,
                        redirect_uri=REDIRECT_URI,
                        scope=SCOPE)


@spotifyAuthBP.route("/spotify_login")
def spotify_login():
    """Redirect user to Spotify OAuth login"""
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@spotifyAuthBP.route("/callback")
def callback():
    """Handle Spotify OAuth callback and retrieve access token"""
    code = request.args.get("code")

    if not code:
        return "Error: No authorization code provided by Spotify."

    try:

        token_info = sp_oauth.get_access_token(code, as_dict=True)

        print("Token Info:", token_info)  

        if not token_info or "access_token" not in token_info:
            return "Error: Failed to retrieve access token from Spotify. Try logging in again."

        session["token_info"] = token_info
        return redirect(url_for("test"))

    except Exception as e:
        print("Spotify Token Error:", str(e))
        return f"Error: {str(e)}"



@spotifyAuthBP.route('/test2')
def test2():
    latestReview = mostRecentReview(session['email'])
    mostRecentListen = latestReview['album_name']
    
    token_info = session.get("token_info")
    if not token_info or "access_token" not in token_info:
        return redirect(url_for("spotifyAuthBP.callback"))

    access_token = token_info["access_token"]

    search_headers = {
        "Authorization": f"Bearer {access_token}"
    }

    current_timestamp_ms = int(time.time() * 1000)
    params = {
        "before": current_timestamp_ms,
        "limit": 50
    }

    search_response = requests.get("https://api.spotify.com/v1/me/player/recently-played", headers=search_headers, params=params)

    if search_response.status_code == 204:  
        return jsonify({"message": "No recently played tracks found."})

    if search_response.status_code != 200:
        return jsonify({"error": "Error fetching data from Spotify", "status_code": search_response.status_code}), 500

    try:
        data = search_response.json()
    except requests.exceptions.JSONDecodeError:
        return jsonify({"error": "Invalid JSON response from Spotify"}), 500

    recent_tracks = []
    for item in data.get("items", []):
        track = item["track"]
        artist_name = ", ".join([artist["name"] for artist in track["artists"]]) 
        album_name = track["album"]["name"]
        context_type = item["context"]["type"] if item.get("context") else "Unknown"
        played_at = item["played_at"]

        played_at_dt = datetime.strptime(played_at, "%Y-%m-%dT%H:%M:%S.%fZ")
        played_at_str = played_at_dt.strftime("%Y-%m-%d %H:%M:%S")

        if context_type != "playlist" and not any(track['albumName'] == album_name for track in recent_tracks):
            if album_name == mostRecentListen:
                break
            recent_tracks.append({
                "notes": "",
                "albumName": album_name,
                "artistName": artist_name,
                "firstListen": "",  
                "dateListened": played_at_str,
                "averageRating": "" 
            })

    autoLogged = recent_tracks[0]
    session['review_json'] = autoLogged
    return redirect(url_for('save_review'))





@spotifyAuthBP.route('/searchSpotify', methods=['POST'])
def searchSpotify():
    data = request.get_json()
    query = data.get('query')
    search_type = data.get('type')

    client_credentials = f"{spotifyClientID}:{spotifyClientSecret}"
    encoded_credentials = base64.b64encode(client_credentials.encode('utf-8')).decode('utf-8')

    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    token_data = {
        "grant_type": "client_credentials"
    }

    token_response = requests.post("https://accounts.spotify.com/api/token", data=token_data, headers=headers)

    if token_response.status_code != 200:
        return jsonify({"error": "Error fetching access token from Spotify"}), 500

    token_info = token_response.json()
    access_token = token_info.get('access_token')

    if not access_token:
        return jsonify({"error": "Access token not found"}), 500

    search_headers = {
        "Authorization": f"Bearer {access_token}"
    }

    params = {
        "q": query,
        "type": search_type,
        "limit": 1 
    }

    search_response = requests.get("https://api.spotify.com/v1/search", headers=search_headers, params=params)

    if search_response.status_code != 200:
        return jsonify({"error": "Error fetching data from Spotify", "message": search_response.json()}), 500

    search_info = search_response.json()
    if search_type == 'album' and search_info.get('albums', {}).get('items'):
        album = search_info['albums']['items'][0]
        return jsonify({
            'type': 'favouriteAlbum',
            'name': album['name'],
            'imageURL': album['images'][0]['url']
        })
    elif search_type == 'track' and search_info.get('tracks', {}).get('items'):
        song = search_info['tracks']['items'][0]
        return jsonify({
            'type': 'favouriteSong',
            'name': song['name'],
            'imageURL': song['album']['images'][0]['url']
        })
    elif search_type == 'artist' and search_info.get('artists', {}).get('items'):
        artist = search_info['artists']['items'][0]
        return jsonify({
            'type': 'favouriteArtist',
            'name': artist['name'],
            'imageURL': artist['images'][0]['url']
        })
    else:
        return jsonify({"error": f"No {search_type} found for the query"}), 404


@spotifyAuthBP.route('/changeFavourites', methods=['POST'])
def changeFavourites():
    data = request.get_json()

    category = data.get('type')  
    newName = data.get('name')  
    newURL = data.get('imageURL') 

    favourites_json = {
        "name": newName,
        "imageUrl": newURL
    }
    favouritesJSONString = json.dumps(favourites_json)
    worked = editFavourite(favouritesJSONString, session['email'], category)

    if worked:
        return jsonify({"status": "success", "favourite": favourites_json})
    else:
        return jsonify({"status": "failure"})
    
    
@spotifyAuthBP.route('/setFavourites', methods=['GET', 'POST'])
def setFavourites():
    if request.method == 'POST':
        session['favourites'] = request.json
        print(session['favourites'])
    
    return render_template("setFavourites.html", spotifyClientID=spotifyClientID, spotifyClientSecret=spotifyClientSecret)



