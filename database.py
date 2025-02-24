from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from argon2 import PasswordHasher

hasher = PasswordHasher()
load_dotenv(dotenv_path='env/.env')
dbMasterUsername = os.getenv('dbMasterUsername')  
dbMasterPassword = os.getenv('dbMasterPassword')
db = SQLAlchemy()  

def init_db(app):
    db.init_app(app) 

class my_discog_user(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), unique=False, nullable=False)

    def __repr__(self):
        return f'<sas21 {self.username}>'

def registerUser(inputtedusername, theirEmail, theirpassword):
    theirpassword = hasher.hash(theirpassword)
    new_user = my_discog_user(username=inputtedusername, email=theirEmail, password=theirpassword)
    db.session.add(new_user)
    db.session.commit()
    return f'User {new_user.username} created!'


def logUserIn(theirEmail, theirPassword):
    user = my_discog_user.query.filter_by(email=theirEmail).first()

    try:
        if user and hasher.verify(user.password, theirPassword): 
            return True  
    except:
        pass  

    return False  


#need to do some actual database design but for now this works to show off the concept