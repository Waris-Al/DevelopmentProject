from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from argon2 import PasswordHasher
from sqlalchemy.dialects.postgresql import JSONB

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

class usersreviews(db.Model):
    __tablename__ = 'usersreviews'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userid = db.Column(db.Integer, db.ForeignKey('my_discog_user.id', ondelete='CASCADE'), nullable=False)
    review_data = db.Column(JSONB, nullable=False)
    
    user = db.relationship('my_discog_user', backref='reviews')

    def __repr__(self):
        return f'<Review by {self.user.username}>'



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


def addReview(user_id, review_data):
    user = my_discog_user.query.get(user_id)
    
    if user:
        new_review = usersreviews(userid=user_id, review_data=review_data)
        db.session.add(new_review)
        db.session.commit()
        return f'Review added for user {user.username}'
    
    return 'User not found!'
    #how to select JSON info
    #SELECT * 
    #FROM reviews 
    #WHERE review_data->>'rating' = '5';

    


#need to do some actual database design but for now this works to show off the concept