from flask import Flask, render_template, request, session, jsonify, Blueprint
from database import loadMessages, addMessage
from dotenv import load_dotenv
from flask_socketio import SocketIO, send, emit
from datetime import datetime
from routes.socketSetUp import socketio 


#Stuff to load database
load_dotenv(dotenv_path='env/.env')
messagingRoutes = Blueprint('messagingRoutes', __name__)



@messagingRoutes.route('/DM')
def DM():
    return render_template("dm.html")


#change this so its using session variables, this works for testing for now
AUTHORIZED_USERS = {'user1': 'password1', 'user2': 'password2'}
connected_users = {}


@socketio.on('message')
def handle_message(msg):
    sender = session['username']
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    message_data = {
        "sender": sender,
        "message": msg,
        "timestamp": timestamp
    }

    print(f"Message from {sender}: {msg} at {timestamp}")
    send(message_data, broadcast=True)

    
@socketio.on('connect')
def handle_connect():
    username = request.args.get('username')
    password = request.args.get('password')
    
    # Check if the user is authorized
    if username in AUTHORIZED_USERS and AUTHORIZED_USERS[username] == password:
        connected_users[username] = request.sid  
        print(f'{username} connected')
    else:
        print(f'Unauthorized access attempt from {username}')
        handle_disconnect() 

@socketio.on('disconnect')
def handle_disconnect():
    for username, sid in connected_users.items():
        if sid == request.sid:
            print(f'{username} disconnected')
            del connected_users[username]  

@socketio.on('broadcast')
def handle_broadcast_event(msg):
    send(msg, broadcast=True)

@socketio.on('custom_event')
def handle_custom_event(data):
    emit('response', {'data': 'Custom event received!'}, broadcast=True)

@messagingRoutes.route("/retrieveMessages")
def loadMessage():
    conversation_id = 8 #change to session var
    messages = loadMessages(conversation_id)
    return messages



@messagingRoutes.route("/recordMessage", methods=["POST"])
def addMessages():
    data = request.json 
    message = data.get("message")

    if not message:
        return jsonify({"error": "No message provided"}),

    response = addMessage(8, session['username'], message)  
    return jsonify({"status": "success", "message": message})  



