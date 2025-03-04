from flask import Flask, render_template, url_for, request, redirect, session, jsonify
from database import registerUser, init_db, logUserIn, addReview, usersreviews
from dotenv import load_dotenv
import os
app = Flask(__name__)

#Stuff to load database
load_dotenv(dotenv_path='env/.env')
app.secret_key = os.getenv("app.secret_key")
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{os.getenv("dbMasterUsername")}:{os.getenv("dbMasterPassword")}@localhost/dbname'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
init_db(app)

@app.route('/')
def index():
    return render_template('index.html')

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


if __name__ == "__main__":
    app.run(debug=True)

