from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from dotenv import load_dotenv
import os
from argon2 import PasswordHasher
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
import json


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
    favourites = db.Column(JSONB)

    def __repr__(self):
        return f'<sas21 {self.username}>'

class usersreviews(db.Model):
    __tablename__ = 'usersreviews'
    
    reviewid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_email = db.Column(db.String, db.ForeignKey('my_discog_user.email', ondelete='CASCADE'), nullable=False)
    review = db.Column(JSONB, nullable=False) 
    
    user = db.relationship('my_discog_user', backref='reviews')

    def __repr__(self):
        return f'<Review by {self.user.email}>'

class conversations(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    senderid = db.Column(db.String(80), db.ForeignKey('my_discog_user.username'), nullable=False)
    receiverid = db.Column(db.String(80), db.ForeignKey('my_discog_user.username'), nullable=False)
    messages = db.Column(JSONB, nullable=False)
    
    sender = db.relationship('my_discog_user', foreign_keys=[senderid])  
    receiver = db.relationship('my_discog_user', foreign_keys=[receiverid]) 
    
    def __repr__(self):
        return f'<Conversations(senderID={self.senderID}, receiverID={self.receiverID})>'

    

def loadMessages(conversationID):
    try:
        conversation = conversations.query.get(conversationID)
        
        if conversation:
            return conversation.messages
        else:
            return {"error": "Conversation not found"}
    
    except Exception as e:
        return {"error": str(e)}
    
    
def addMessage(conversationID, sender, message):
    conversation = conversations.query.get(conversationID)
    
    if conversation:
        previousMessages = conversation.messages or [] 
        new_message = {
            "sender": sender,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()  
        }
        
        previousMessages.append(new_message)
        db.session.expire(conversation, ["messages"]) 
        conversation.messages = previousMessages
        db.session.commit()
        
        return "Message added"





def registerUser(inputtedusername, theirEmail, theirpassword, favourites):
    theirpassword = hasher.hash(theirpassword)
    new_user = my_discog_user(username=inputtedusername, email=theirEmail, password=theirpassword, favourites=favourites)
    db.session.add(new_user)
    db.session.commit()
    return f'User {new_user.username} created!'


def logUserIn(theirEmail, theirPassword):
    user = my_discog_user.query.filter_by(email=theirEmail).first()

    try:
        if user and hasher.verify(user.password, theirPassword): 
            return user.username  
    except:
        pass  

    return False  


def addReview(user_email, review_data):
    user = my_discog_user.query.filter_by(email=user_email).first()
    
    if user:
        new_review = usersreviews(user_email=user_email, review=review_data)  # Removed reviewid, as it's auto-incrementing
        db.session.add(new_review)
        db.session.commit()
        return f'Review added for user {user.email}'
    
    return 'User not found!'


    #how to select JSON info
    #SELECT * 
    #FROM reviews 
    #WHERE review_data->>'rating' = '5';

    
def editFavourite(newFavourite, email, category):
    user = my_discog_user.query.filter_by(email=email).with_entities(my_discog_user.favourites[category]).first()

    if user:
        my_discog_user.query.filter_by(email=email).update({
            'favourites': func.jsonb_set(
                my_discog_user.favourites,  
                [category],                 
                newFavourite,            
                True                       
            )
        })
        db.session.commit()

        return True
    else:
        return False


def loadFavourites(email):
    user = my_discog_user.query.filter_by(email=email).with_entities(my_discog_user.favourites).first()
    
    if user:
        return user[0]
    else:
        return None
    

def searchReviews(searchTerm):
    try:
        results = usersreviews.query.filter(
            usersreviews.review['albumName'].astext == searchTerm
        ).all()

        if results:
            return [{"review_id": review.reviewid, "user_email": review.user_email, "review": review.review} for review in results]
        else:
            return {"message": "No reviews found for the album name."}
    except Exception as e:
        return {"error": str(e)}



#need to do some actual database design but for now this works to show off the concept