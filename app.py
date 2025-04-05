from flask import Flask, render_template, url_for, request, redirect, session, jsonify, json
from database import registerUser, init_db, logUserIn, addReview, usersreviews, loadFavourites, searchFor, findUser, editReview
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from flask_socketio import SocketIO, send, emit
from datetime import datetime
import requests
import base64
from routes.spotifyAuth import spotifyAuthBP
from routes.messaging import messagingRoutes
from routes.socketSetUp import socketio
app = Flask(__name__)

#Stuff to load database
load_dotenv(dotenv_path='env/.env')
app.secret_key = os.getenv("app.secret_key")

spotifyClientID = os.getenv("spotifyClientID")
spotifyClientSecret = os.getenv("spotifyClientSecret")



db_username = os.getenv("DB_USERNAME")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_username}:{db_password}@{db_host}/{db_name}'
#app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{os.getenv("dbMasterUsername")}:{os.getenv("dbMasterPassword")}@localhost/dbname'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



init_db(app)
socketio.init_app(app)
app.register_blueprint(spotifyAuthBP)
app.register_blueprint(messagingRoutes)



@app.route('/')
def index():
    return render_template('index.html')



@app.route('/editReview', methods=['GET', 'POST'])
def editUserReview():
        
    if request.method == 'POST':
        data = request.json
        review = data.get("review")
        dateListened = data.get("dateListened")
        

        
        editedReview = editReview(dateListened, review, 28) #use teh actual id
        
        if editedReview:
            print("Review edited successfully")

    else:
        return render_template("editReview.html")
    return "hi"

@app.route('/Homepage')
def Homepage():
    if session.get('email'):
        #move this into the DB file
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
        email = request.form['email'].lower()
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
    if session.get('favourites') is None:
        session['error'] = "Registration failed, please select favourites"
        
    elif request.method == 'POST' and session.get('favourites') is not None:
        email = request.form['email'].lower()
        name = request.form['name']
        username = request.form['username'].lower()
        password = request.form['password']
        favourites = session['favourites']
        
        success = registerUser(username, email, password, favourites)
        
        if success:
            session.pop('error', None)
            return redirect(url_for('Login'))
        else:
            return render_template('register.html', error=session.get('error')) 

    return render_template('register.html', error=session.get('error'))


@app.route('/save_review', methods=['GET', 'POST'])
def save_review():
    try:
        userID = session['email']
        
        if request.method == "POST":
            data = request.json
            review = data.get("reviewData")
        else:
            review = session['review_json']
            
        addReview(userID, review) 
        
        if session['autologgedReviews']:
            session.pop('autologgedReviews', None)
            return redirect(url_for('Homepage'))
        
        return jsonify({"message": "Review saved successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/newReview')
def newReview():
    return render_template("newReview.html", spotifyClientID=spotifyClientID, spotifyClientSecret=spotifyClientSecret)

@app.route('/test')
def test():
    return render_template("test.html", spotifyClientID=spotifyClientID, spotifyClientSecret=spotifyClientSecret)




@app.route('/searchReviews', methods=['POST'])
def searchReviews():
    data = request.json
    searchTerm = data.get("query") 
    reviews = searchFor(searchTerm)
    
    return jsonify(reviews) #get this displayed in a dropdown on the page



@app.route('/searchUser', methods=['POST'])
def searchUserOrMedia():
    data = request.json
    query = data.get("query")
    users = findUser(query)
    
    if users:
        return users
    else:
        return "No users found" # make sure to pass this back so it displays on html


if __name__ == "__main__":
    socketio.run(app, debug=True)


