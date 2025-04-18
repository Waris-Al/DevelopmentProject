from flask import Flask, render_template, url_for, request, redirect, session, jsonify
from database import registerUser, init_db, logUserIn, addReview, loadFavourites, searchFor, findUser, editReview, deleteReview, getUserReviews, mutualFollow, findFollowers, followUser
from dotenv import load_dotenv
import os
from routes.spotifyAuth import spotifyAuthBP
from routes.messaging import messagingRoutes
from routes.socketSetUp import socketio
from routes.recommendations import recommendationAlgorithm
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
app.register_blueprint(recommendationAlgorithm)



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/deleteReview', methods=['POST'])
def deleteUserReview():
        
    if request.method == 'POST':
        data = request.json
        reviewID = data.get("review_id")
        
        deletedReview = deleteReview(reviewID)
        
        if deletedReview:
            print("Review deleted successfully")
            
    else:
        return render_template("deleteReview.html")
    return "hi"

@app.route('/editReview', methods=['GET', 'POST'])
def editUserReview():
        
    if request.method == 'POST':
        data = request.json
        review = data.get("review")
        dateListened = data.get("date_listened")
        reviewID = data.get("review_id")
        

        
        editedReview = editReview(dateListened, review, reviewID)
        
        if editedReview:
            print("Review edited successfully")

    else:
        return render_template("editReview.html")
    return "hi"

@app.route('/Homepage')
def Homepage():
    if session.get('email'):
        formatted_reviews = getUserReviews(session['email'])
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

    if request.method == 'POST' and session.get('favourites') is not None:
        email = request.form['email'].lower()
        name = request.form['name']
        username = request.form['username'].lower()
        password = request.form['password']
        favourites = session['favourites']
        
        success = registerUser(username, email, password, favourites, name)
        
        if success:
            session.pop('error', None)
            session['email'] = email
            return redirect(url_for('Homepage'))
        else:
            return render_template('register.html', error=session.get('error')) 
    
    elif request.method == 'POST' and session.get('favourites') is None:
        session['error'] = "Registration failed, please select favourites"

    return render_template('register.html', error=session.get('error'))


@app.route('/save_review', methods=['GET', 'POST'])
def save_review():
    try:
        userID = session['email']
        username = session['username']

        
        if request.method == "POST":
            data = request.json
            review = data.get("reviewData")
            addReview(userID, review, username)
        else:
            review = session['review_json']
            
            for autoReview in review:
                addReview(userID, autoReview, username)
            
        
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
        return jsonify({"redirect_url": url_for('userProfile', username=users['username'])})
    else:
        return jsonify({"error": "No users found"}) # make sure to pass this back so it displays on html


@app.route('/userProfile/<username>', methods=['GET', 'POST'])
def userProfile(username):
    user = findUser(username)
    
    #we also need to put this in the db file, perhaps we could merge this function with homepage?
    if user:
        showFollowButton = False
        showChatButton = False
        
        followerEmail = session['email']
        followeeEmail = user['email']
        checkFollowers = findFollowers(followeeEmail)
        
        if followerEmail in checkFollowers:
            areMutuals = mutualFollow(followerEmail, followeeEmail)
            if areMutuals != "Not moots":
                showChatButton = True
        else:
            showFollowButton = True
        
        formatted_reviews = getUserReviews(user['email'])
        return render_template("userProfile.html", username=username, profilesEmail=user['email'], reviews=formatted_reviews, favourites=user['favourites'], showFollowButton=showFollowButton, showChatButton=showChatButton)
    else:
        return "User not found", 404


@app.route('/followUser', methods=['POST'])
def follow():
    data = request.json
    followerEmail = session['email']
    followeeEmail = data.get("followeeEmail")
    
    userFollowed = followUser(followerEmail, followeeEmail)
    
    if userFollowed:
        return jsonify({"message": "Followed successfully!"}), 200
    else:
        return jsonify({"error": "Failed to follow user."}), 400
    
#we will also need an unfollow function
    
    
#arguably we dont even need these endpoints and can just use the functions, but keep for now just in case
@app.route('/getMutuals')
def getMutuals():
    areMutuals = mutualFollow('shouldsave@bugfix.com', 'wanilaj@mailinator.com') #these need to come from the post request
    
    return areMutuals

@app.route('/getAllFollowers')
def getAllFollowers():
    allFollowers = findFollowers('wanilaj@mailinator.com') #should be passed in
    
    return allFollowers

if __name__ == "__main__":
    socketio.run(app, debug=True)


