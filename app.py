from flask import Flask, render_template, url_for, request, redirect
from database import registerUser, init_db, logUserIn
from dotenv import load_dotenv
import os
app = Flask(__name__)

#Stuff to load database
load_dotenv(dotenv_path='env/.env')
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{os.getenv("dbMasterUsername")}:{os.getenv("dbMasterPassword")}@localhost/dbname'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
init_db(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/Homepage')
def Homepage():
    return render_template("homepage.html")

@app.route('/Login', methods=['GET', 'POST'])
def Login():
    if request.method == "POST":
        email = request.form['username']
        password = request.form['password']
        
        success = logUserIn(email, password)
        
        if success:
            return redirect(url_for('Homepage'))
        else:
            return redirect(url_for("test.html")) #change this to an error message
    return render_template('login.html')

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


if __name__ == "__main__":
    app.run(debug=True)

