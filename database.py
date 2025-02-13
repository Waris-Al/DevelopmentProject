from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path='env/.env')
dbMasterUsername = os.getenv('dbMasterUsername')  
dbMasterPassword = os.getenv('dbMasterPassword')
db = SQLAlchemy()  

def init_db(app):
    db.init_app(app) 

class sas21(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f'<sas21 {self.username}>'

def create_user():
    new_user = sas21(username='dsfdsfdsfdsfdsf', email='ddsfdsfdsfdsfdssadsadasd@example.com')
    db.session.add(new_user)
    db.session.commit()
    return f'User {new_user.username} created!'

#The code in here is just an example of whats needed for database connections