from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

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
    new_user = my_discog_user(username=inputtedusername, email=theirEmail, password=theirpassword)
    db.session.add(new_user)
    db.session.commit()
    return f'User {new_user.username} created!'

#need to do some actual database design but for now this works to show off the concept