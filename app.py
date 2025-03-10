from flask import Flask, render_template, url_for, request, redirect, session, jsonify
from database import registerUser, init_db, logUserIn, addReview, usersreviews
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
app = Flask(__name__)

#Stuff to load database
load_dotenv(dotenv_path='env/.env')
app.secret_key = os.getenv("app.secret_key")

spotifyClientID = os.getenv("spotifyClientID")
spotifyClientSecret = os.getenv("spotifyClientSecret")

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{os.getenv("dbMasterUsername")}:{os.getenv("dbMasterPassword")}@localhost/dbname'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
init_db(app)

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
    reviews = usersreviews.query.filter_by(userid=4).all()

    formatted_reviews = []
    for review in reviews:
        review_data = review.review_data
        formatted_reviews.append({
            'album_name': review_data.get('albumName', 'Unknown Album'),
            'artist_name': review_data.get('artistName', 'Unknown Artist'),
            'date_listened': review_data.get('dateListened', 'Unknown Date'),
            'review': review_data.get('notes', 'No review available')
        })
        
    return render_template("homepage.html", reviews=formatted_reviews)

@app.route('/Login', methods=['GET', 'POST'])
def Login():
    if request.method == "POST":
        email = request.form['username']
        password = request.form['password']
        
        success = logUserIn(email, password)
        
        if success:
            session.pop('error', None)
            return redirect(url_for('Homepage'))
        else:
            session['error'] = "Invalid username or password"
            return redirect(url_for('Login')) 
    
    error = session.pop('error', None)
    return render_template('login.html', error=error)

@app.route('/Register', methods=['GET', 'POST'])
def Register():
    if request.method == 'POST':
        email = request.form['email']
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        
        success = registerUser(email, username, password)
        
        if success:
            return redirect(url_for('Login'))
        else:
            return render_template('register.html', error="Registration failed, please try again.")
    
    return render_template('register.html')


@app.route('/save_review', methods=['POST'])
def save_review():
    try:
        userID = 4 #placeholder, change so that it uses the real one 
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

if __name__ == "__main__":
    app.run(debug=True)

