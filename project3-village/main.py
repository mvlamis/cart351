from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
import os
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
client = MongoClient(uri)
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

@app.route('/api/users')
def get_users():
    # Fetch all users, exclude passwords
    users = list(users_collection.find({}, {'password': 0}))
    
    # Convert ObjectId to string for JSON serialization
    for user in users:
        user['_id'] = str(user['_id'])
        # Ensure friends list exists
        if 'friends' not in user:
            user['friends'] = []
            
    return jsonify(users)

@app.route('/map')
@login_required
def map_view():
    return render_template('map.html')


if __name__ == '__main__':
    app.run(debug=True)