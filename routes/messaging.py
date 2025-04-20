from flask import Flask, render_template, request, session, jsonify, Blueprint
from database import loadMessages, addMessage, newConversation
from dotenv import load_dotenv
from flask_socketio import SocketIO, send, emit
from datetime import datetime
from routes.socketSetUp import socketio 

load_dotenv(dotenv_path='env/.env') #Access env variables
messagingRoutes = Blueprint('messagingRoutes', __name__)

'''The functions in this file are all related to the messaging service.'''

@messagingRoutes.route('/DM')
def DM():
    return render_template("dm.html")


#change this so its using session variables, this works for testing for now
AUTHORIZED_USERS = {'user1': 'password1', 'user2': 'password2'}
connected_users = {}


#Function to receive messages
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


#Connects users to socket    
@socketio.on('connect')
def handle_connect():
    username = "user1"
    password = "password1"
    #we need to completley rewrite this logic, hard coding for now to get user testing done at least
    
    # Check if the user is authorized
    if username in AUTHORIZED_USERS and AUTHORIZED_USERS[username] == password:
        connected_users[username] = request.sid  
        print(f'{username} connected')
    else:
        print(f'Unauthorized access attempt from {username}')
        handle_disconnect() 

#Disconnect user from chat when they leave
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

#Loads previous messages in a chat
@messagingRoutes.route("/retrieveMessages")
def loadMessage():
    conversation_id = 9 #change to session var
    messages = loadMessages(conversation_id)
    return messages

#Saves message to chat history
@messagingRoutes.route("/recordMessage", methods=["POST"])
def addMessages():
    data = request.json 
    message = data.get("message")

    if not message:
        return jsonify({"error": "No message provided"}),

    response = addMessage(9, session['username'], message)  
    return jsonify({"status": "success", "message": message})  


@messagingRoutes.route("/createConversation", methods=["GET"])
def createConversation():
    #again change these all to use the session variables
    #conversersData = request.json
    sender = "thatsnotme" #conversersData.get("sender")
    receiver = "wazzamazza" #conversersData.get("receiver")
    success = newConversation(sender, receiver)
    if success:
        return jsonify({"status": "success", "message": "Conversation created"})
    else:
        return jsonify({"status": "error", "message": "Failed to create conversation"}), 500
