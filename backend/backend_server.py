import os
import json
import time
import uuid
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import requests
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate('.\\personal-finance-snapshot-firebase-adminsdk-ub403-53c2c8a22d.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

load_dotenv()

app = Flask(__name__)

PLAID_CLIENT_ID = os.getenv('PLAID_CLIENT_ID')
PLAID_SECRET = os.getenv('PLAID_SECRET')
PLAID_PORT = os.getenv('PLAID_PORT')
PLAID_URL = os.getenv('NGROK_URL', f'http://localhost:{PLAID_PORT}')

@app.route('/', methods=['GET'])
def index():
    return jsonify({'name': 'backend server', 'status': 'ok'})

# plaid client flow
# route to register user based on given user_id, put {user_id: user_token} in db
@app.route('/register_user', methods=['POST'])
def register_user():
    try:
        user_id = request.json['user_id']
        response = requests.post(PLAID_URL + '/api/create_user_token', json={'user_id': user_id})
        if response.status_code == 200:
            posts = response.json()
            user_token = posts['user_token']
            put_user_token(user_id, user_token)
        else:
            print('create user token Plaid server POST request error:', response.status_code)
            return None
    except requests.exceptions.RequestException as e:
        print('Error: ', e)
        return None
    return jsonify(text = 'success', status=200) 



# route to use user_token, request link token, return link token to client
@app.route('/get_link_token', methods=['POST'])
def get_link_token():
    try:
        user_id = request.json['user_id']
        user_token = get_user_token(user_id)
        if not user_token:
            return jsonify({'error': 'User token not found'}), 404
        response = requests.post(PLAID_URL + '/api/create_link_token', json={'user_token': user_token})
        if response.status_code == 200:
            posts = response.json()
        else:
            print('get link token Plaid server POST request error:', response.status_code)
            return None
    except requests.exceptions.RequestException as e:
        print('Error: ', e)
        return None
    return jsonify({'link_token': posts['link_token']})

# (not implemented here) use link token, call frontend, from onSuccess callback, extract (temp) public token
# route to use public token, call plaid exchange method to exchange public_token for (permanent) access_token and item_id and put in db for this user
@app.route('/exchange_public_token', methods=['POST'])
def exchange_public_token():
    try:
        user_id = request.json['user_id']
        public_token = request.json['public_token']
        response = requests.post(PLAID_URL + 'api/set_access_token', json={'public_token': public_token})
        if response.status_code == 200:
            posts = response.json()
            put_access_token_and_item_id(user_id, posts['access_token'], posts['item_id'])
        else:
            print('exchange public token Plaid server POST request error: ', response.status_code)
            return None
    except requests.exceptions.RequestException as e:
        print('Error: ', e)
        return None
    return jsonify(text = 'success', status=200)

def put_access_token_and_item_id(user_id, access_token, item_id):
    global db
    try:
        doc_ref = db.collection('users').document(user_id)
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            items = data.get('items',[])
            
            for item in items:
                if item['item_id'] == item_id:
                    item['access_token'] = access_token
                    break
            
            else:
                items.append({'item_id':item_id, 'access_token':access_token})
            doc_ref.update({'items':items})
        else:
            print('Document does not exist')
        
    except Exception as e:
        print(f"Error storing access_token and item_id for user {user_id}: {e}")
    

def put_user_token(user_id, user_token):
    global db
    doc_ref = db.collection('users').document(user_id)
    doc_ref.set({
        'user_token': user_token
    })
    
def get_user_token(user_id):
    global db
    doc_ref = db.collection('users').document(user_id)
    doc = doc_ref.get()
    try:
        if doc.exists:
            data = doc.to_dict()
            return data.get('user_token')
        else:
            print(f"No document found for user_id: {user_id}")
            return None
    except Exception as e:
        print(f"Error retrieving user_token for user_id {user_id}: {e}")
        return None

def get_access_token(user_id):
    # TODO: get access_token from db
    global db
    try:
        doc_ref = db.collection('users').document(user_id)
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            return data.get('access_token')
        else:
            print(f"No document found for user_id: {user_id}")
            return None
    except Exception as e:
        print(f"Error retrieving access_token for user_id {user_id}: {e}")
        return None


if __name__ == '__main__':
    app.run(port=int(os.getenv('BACKEND_PORT', 7000)))