from flask import Flask, render_template, url_for
from database import create_user, init_db
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

@app.route('/Register')
def Register():
    return render_template('register.html')

@app.route('/createUser')
def createUser():
    create_user()
    return "successfully Created User"
    #we should add some error handling here. and in all the functions tbf

if __name__ == "__main__":
    app.run(debug=True)

