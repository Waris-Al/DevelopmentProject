from flask import Flask, render_template, url_for, request, redirect
from database import registerUser, init_db
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

@app.route('/Login')
def Login():
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

