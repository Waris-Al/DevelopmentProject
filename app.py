from flask import Flask, render_template, url_for, request, redirect, session, jsonify, json
from database import registerUser, init_db, logUserIn, addReview, usersreviews, loadMessages, addMessage, editFavourite, loadFavourites
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from flask_socketio import SocketIO, send, emit
from datetime import datetime
import requests
import base64
app = Flask(__name__)

#Stuff to load database
load_dotenv(dotenv_path='env/.env')
app.secret_key = os.getenv("app.secret_key")

spotifyClientID = os.getenv("spotifyClientID")
spotifyClientSecret = os.getenv("spotifyClientSecret")

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{os.getenv("dbMasterUsername")}:{os.getenv("dbMasterPassword")}@localhost/dbname'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
init_db(app)
socketio = SocketIO(app)


@app.route('/')
def index():
    return render_template('index.html')


REDIRECT_URI = "http://127.0.0.1:5000/callback" 


SCOPE = "user-top-read user-read-playback-state user-read-currently-playing"



sp_oauth = SpotifyOAuth(client_id=spotifyClientID,
                        client_secret=spotifyClientSecret,
                        redirect_uri=REDIRECT_URI,
                        scope=SCOPE)


@app.route("/spotify_login")
def spotify_login():
    """Redirect user to Spotify OAuth login"""
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route("/callback")
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
        return redirect(url_for("top_artist"))

    except Exception as e:
        print("Spotify Token Error:", str(e))
        return f"Error: {str(e)}"



@app.route('/Homepage')
def Homepage():
    if session.get('email'):
        reviews = usersreviews.query.filter_by(user_email=session['email']).all()

        formatted_reviews = []
        for userReview in reviews:
            review_data = userReview.review
            formatted_reviews.append({
                'album_name': review_data.get('albumName', 'Unknown Album'),
                'artist_name': review_data.get('artistName', 'Unknown Artist'),
                'date_listened': review_data.get('dateListened', 'Unknown Date'),
                'review': review_data.get('notes', 'No review available')
            })
            
        favourites = loadFavourites(session['email'])
            
        return render_template("homepage.html", reviews=formatted_reviews, spotifyClientID=spotifyClientID, spotifyClientSecret=spotifyClientSecret, favourites=favourites)
    else:
        return render_template("index.html")

@app.route('/Login', methods=['GET', 'POST'])
def Login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        
        success = logUserIn(email, password)
        
        if success:
            session['username'] = success
            session['email'] = email
            session.pop('error', None)
            print(session['username'])
            return redirect(url_for('Homepage'))
        else:
            session['error'] = "Invalid username or password"
            return redirect(url_for('Login')) 
    
    
    error = session.pop('error', None)
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index')) 


@app.route('/Register', methods=['GET', 'POST'])
def Register():
    if request.method == 'POST' and session['favourites'] != None:
        email = request.form['email']
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        favourites = session['favourites']
        
        success = registerUser(username, email, password, favourites)
        
        if success:
            return redirect(url_for('Login'))
        else:
            return render_template('register.html', error="Registration failed, please try again.")
    
    return render_template('register.html')


@app.route('/save_review', methods=['POST'])
def save_review():
    try:
        userID = session['email']
        data = request.json  
        review = data.get("reviewData") 
        
        addReview(userID, review) 
        
        return jsonify({"message": "Review saved successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/newReview')
def newReview():
    return render_template("newReview.html", spotifyClientID=spotifyClientID, spotifyClientSecret=spotifyClientSecret)

@app.route('/test')
def test():
    return render_template("test.html", spotifyClientID=spotifyClientID, spotifyClientSecret=spotifyClientSecret)


@app.route('/DM')
def DM():
    return render_template("DM.html")




@app.route('/searchSpotify', methods=['POST'])
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


@app.route('/changeFavourites', methods=['POST'])
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
    
    
@app.route('/setFavourites', methods=['GET', 'POST'])
def setFavourites():
    if request.method == 'POST':
        session['favourites'] = request.json
        print(session['favourites'])
    
    return render_template("setFavourites.html", spotifyClientID=spotifyClientID, spotifyClientSecret=spotifyClientSecret)



#change this so its using session variables, this works for testing for now
AUTHORIZED_USERS = {'user1': 'password1', 'user2': 'password2'}
connected_users = {}


@socketio.on('message')
def handle_message(msg):
    sender = session['username']
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    message_data = {
        "sender": sender,
        "message": msg,
        "timestamp": timestamp
    }

    print(f"Message from {sender}: {msg} at {timestamp}")
    send(message_data, broadcast=True)

    
@socketio.on('connect')
def handle_connect():
    username = request.args.get('username')
    password = request.args.get('password')
    
    # Check if the user is authorized
    if username in AUTHORIZED_USERS and AUTHORIZED_USERS[username] == password:
        connected_users[username] = request.sid  
        print(f'{username} connected')
    else:
        print(f'Unauthorized access attempt from {username}')
        handle_disconnect() 

@socketio.on('disconnect')
def handle_disconnect():
    for username, sid in connected_users.items():
        if sid == request.sid:
            print(f'{username} disconnected')
            del connected_users[username]  

@socketio.on('broadcast')
def handle_broadcast_event(msg):
    send(msg, broadcast=True)

@socketio.on('custom_event')
def handle_custom_event(data):
    emit('response', {'data': 'Custom event received!'}, broadcast=True)

@app.route("/retrieveMessages")
def loadMessage():
    conversation_id = 8 #change to session var
    messages = loadMessages(conversation_id)
    return messages



@app.route("/recordMessage", methods=["POST"])
def addMessages():
    data = request.json 
    message = data.get("message")

    if not message:
        return jsonify({"error": "No message provided"}),

    response = addMessage(8, session['username'], message)  
    return jsonify({"status": "success", "message": message})  



if __name__ == "__main__":
    socketio.run(app, debug=True)


