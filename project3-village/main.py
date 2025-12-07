from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
import os
import certifi
from dotenv import load_dotenv

app = Flask(__name__)
app.secret_key = 'secretkey'

load_dotenv()  # Load variables from .env and .flaskenv
db_user = os.getenv('MONGODB_USER')
db_pass = os.getenv('DATABASE_PASSWORD')
db_name = os.getenv('DATABASE_NAME')

# MongoDB Setup
uri = f"mongodb+srv://{db_user}:{db_pass}@cart351-flask.7fkryat.mongodb.net/{db_name}?retryWrites=true"
app.config["MONGO_URI"] = uri
client = MongoClient(uri, tlsCAFile=certifi.where(), connect=False, socketTimeoutMS=5000)
db = client[db_name]
users_collection = db['villageUsers']

# Flask-Login Setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.username = user_data['username']
        self.house = user_data.get('house')

    @staticmethod
    def get(user_id):
        if not ObjectId.is_valid(user_id):
            return None
        user_data = users_collection.find_one({'_id': ObjectId(user_id)})
        if user_data:
            return User(user_data)
        return None

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        house = request.form.get('house')

        if password != confirm_password:
            flash('Passwords do not match')
            return redirect(url_for('signup'))
        
        if users_collection.find_one({'username': username}):
            flash('Username already exists')
            return redirect(url_for('signup'))
        
        hashed_password = generate_password_hash(password)
        user_id = users_collection.insert_one({
            'username': username,
            'password': hashed_password,
            'house': house
        }).inserted_id

        user = User.get(user_id)
        login_user(user)
        return redirect(url_for('map_view'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user_data = users_collection.find_one({'username': username})
        if user_data and check_password_hash(user_data['password'], password):
            user = User(user_data)
            login_user(user)
            return redirect(url_for('map_view'))
        
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/friends', methods=['GET', 'POST'])
@login_required
def friends_view():
    current_user_data = users_collection.find_one({'_id': ObjectId(current_user.id)})
    
    # get friends
    friend_ids = current_user_data.get('friends', [])
    friends = []
    if friend_ids:
        friends = list(users_collection.find({'_id': {'$in': [ObjectId(fid) for fid in friend_ids]}}))

    # get friend requests received
    request_ids = current_user_data.get('friend_requests_received', [])
    friend_requests = []
    if request_ids:
        friend_requests = list(users_collection.find({'_id': {'$in': [ObjectId(rid) for rid in request_ids]}}))

    # search
    search_results = []
    search_query = ""
    
    if request.method == 'POST':
        search_query = request.form.get('search_query')
        if search_query:
            # exclude self, friends, sent requests, received requests
            sent_requests = current_user_data.get('friend_requests_sent', [])
            exclude_ids = [ObjectId(current_user.id)] + \
                          [ObjectId(fid) for fid in friend_ids] + \
                          [ObjectId(sid) for sid in sent_requests] + \
                          [ObjectId(rid) for rid in request_ids]

            # search for users matching query (case-insensitive)
            search_results = list(users_collection.find({
                'username': {'$regex': search_query, '$options': 'i'},
                '_id': {'$nin': exclude_ids}
            }))

    return render_template('friends.html', 
                           friends=friends, 
                           friend_requests=friend_requests, 
                           search_results=search_results,
                           search_query=search_query)

@app.route('/send_request/<user_id>', methods=['POST'])
@login_required
def send_request(user_id):
    # add to target's received requests
    users_collection.update_one(
        {'_id': ObjectId(user_id)},
        {'$addToSet': {'friend_requests_received': current_user.id}}
    )
    # add to sender's sent requests to track pending
    users_collection.update_one(
        {'_id': ObjectId(current_user.id)},
        {'$addToSet': {'friend_requests_sent': user_id}}
    )
    flash('Friend request sent!')
    return redirect(url_for('friends_view'))

@app.route('/accept_request/<user_id>', methods=['POST'])
@login_required
def accept_request(user_id):
    # add to current user's friends and remove from requests
    users_collection.update_one(
        {'_id': ObjectId(current_user.id)},
        {
            '$addToSet': {'friends': user_id},
            '$pull': {'friend_requests_received': user_id}
        }
    )
    # add to sender's friends and remove from sent
    users_collection.update_one(
        {'_id': ObjectId(user_id)},
        {
            '$addToSet': {'friends': current_user.id},
            '$pull': {'friend_requests_sent': current_user.id}
        }
    )
    flash('Friend request accepted!')
    return redirect(url_for('friends_view'))

@app.route('/decline_request/<user_id>', methods=['POST'])
@login_required
def decline_request(user_id):
    # remove from current user's received
    users_collection.update_one(
        {'_id': ObjectId(current_user.id)},
        {'$pull': {'friend_requests_received': user_id}}
    )
    # remove from sender's sent
    users_collection.update_one(
        {'_id': ObjectId(user_id)},
        {'$pull': {'friend_requests_sent': current_user.id}}
    )
    flash('Friend request declined.')
    return redirect(url_for('friends_view'))

@app.route('/remove_friend/<user_id>', methods=['POST'])
@login_required
def remove_friend(user_id):
    # mutual removal
    users_collection.update_one(
        {'_id': ObjectId(current_user.id)},
        {'$pull': {'friends': user_id}}
    )
    users_collection.update_one(
        {'_id': ObjectId(user_id)},
        {'$pull': {'friends': current_user.id}}
    )
    flash('Friend removed.')
    return redirect(url_for('friends_view'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_username':
            new_username = request.form.get('username')
            if new_username and new_username != current_user.username:
                if users_collection.find_one({'username': new_username}):
                    flash('Username already exists')
                else:
                    users_collection.update_one({'_id': ObjectId(current_user.id)}, {'$set': {'username': new_username}})
                    flash('Username updated')
                    return redirect(url_for('profile'))
            
        elif action == 'change_password':
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            user_data = users_collection.find_one({'_id': ObjectId(current_user.id)})
            if not check_password_hash(user_data['password'], current_password):
                flash('Incorrect current password')
            elif new_password != confirm_password:
                flash('New passwords do not match')
            else:
                hashed_password = generate_password_hash(new_password)
                users_collection.update_one({'_id': ObjectId(current_user.id)}, {'$set': {'password': hashed_password}})
                flash('Password updated')
                return redirect(url_for('profile'))

        elif action == 'delete_account':
            # remove user from friends lists of other users
            users_collection.update_many(
                {'friends': current_user.id},
                {'$pull': {'friends': current_user.id}}
            )
            # remove user from friend requests
            users_collection.update_many(
                {'friend_requests_received': current_user.id},
                {'$pull': {'friend_requests_received': current_user.id}}
            )
            users_collection.update_many(
                {'friend_requests_sent': current_user.id},
                {'$pull': {'friend_requests_sent': current_user.id}}
            )
            
            users_collection.delete_one({'_id': ObjectId(current_user.id)})
            logout_user()
            flash('Account deleted')
            return redirect(url_for('home'))
            
    return render_template('profile.html')

@app.route('/api/users')
def get_users():
    # fetch all users, exclude passwords
    users = list(users_collection.find({}, {'password': 0}))
    
    # convert ObjectId to string for JSON 
    for user in users:
        user['_id'] = str(user['_id'])
        if 'friends' not in user:
            user['friends'] = []
            
    return jsonify(users)

@app.route('/map')
@login_required
def map_view():
    return render_template('map.html')


if __name__ == '__main__':
    app.run(debug=True)