from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
import os
import certifi
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()  # Load variables from .env
app.secret_key = os.getenv('SECRET_KEY')
db_user = os.getenv('MONGODB_USER')
db_pass = os.getenv('DATABASE_PASSWORD')
db_name = os.getenv('DATABASE_NAME')

# MongoDB Setup
uri = f"mongodb+srv://{db_user}:{db_pass}@cart351-flask.7fkryat.mongodb.net/{db_name}?retryWrites=true"
app.config["MONGO_URI"] = uri
client = MongoClient(uri, tlsCAFile=certifi.where(), connect=False, socketTimeoutMS=5000)
db = client[db_name]
users_collection = db['villageUsers']

FURNITURE_CATALOG = {
    'chair': [
        {'id': 'chair1', 'price': 50, 'src': 'furniture/chairs/chair1.png'},
        {'id': 'chair2', 'price': 100, 'src': 'furniture/chairs/chair2.png'}
    ],
    'plant': [
        {'id': 'plant1', 'price': 30, 'src': 'furniture/plants/plant1.png'},
        {'id': 'plant2', 'price': 60, 'src': 'furniture/plants/plant2.png'}
    ],
    'sofa': [
        {'id': 'sofa1', 'price': 150, 'src': 'furniture/sofas/sofa1.png'},
        {'id': 'sofa2', 'price': 300, 'src': 'furniture/sofas/sofa2.png'}
    ],
    'table': [
        {'id': 'table1', 'price': 80, 'src': 'furniture/table/table1.png'},
        {'id': 'table2', 'price': 160, 'src': 'furniture/table/table2.png'}
    ],
    'wallart': [
        {'id': 'wallart1', 'price': 40, 'src': 'furniture/wallart/wallart1.png'},
        {'id': 'wallart2', 'price': 90, 'src': 'furniture/wallart/wallart2.png'}
    ],
    'exterior': [
        {'id': '1', 'price': 0, 'src': 'houses/house1.png'},
        {'id': '2', 'price': 0, 'src': 'houses/house2.png'},
        {'id': '3', 'price': 0, 'src': 'houses/house3.png'},
        {'id': '4', 'price': 500, 'src': 'houses/house4.png'},
        {'id': '5', 'price': 1000, 'src': 'houses/house5.png'},
        {'id': '6', 'price': 800, 'src': 'houses/house6.png'}
    ]
}

# Flask-Login Setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.username = user_data['username']
        self.house = user_data.get('house')
        self.furniture = user_data.get('furniture', {})
        self.inventory = user_data.get('inventory', [])
        self.coins = user_data.get('coins', 0)

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
            'house': house,
            'coins': 0,
            'inventory': [house], # Add starter house to inventory
            'furniture': {}
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
        if 'furniture' not in user:
            user['furniture'] = {}
            
    return jsonify(users)

@app.route('/map')
@login_required
def map_view():
    return render_template('map.html')

@app.route('/games')
@login_required
def games():
    return render_template('games.html')

@app.route('/games/slime')
@login_required
def game_slime():
    return render_template('game_slime.html')

@app.route('/games/matching')
@login_required
def matching_game():
    return render_template('game_matching.html')

# coins 
@app.route('/api/user/coins', methods=['GET'])
@login_required
def api_get_coins():
    user = users_collection.find_one({'_id': ObjectId(current_user.id)}, {'password': 0})
    coins = user.get('coins', 0)
    return jsonify({'coins': coins}), 200

# add coins to current user (POST) 
@app.route('/api/user/coins/add', methods=['POST'])
@login_required
def api_add_coins():
    data = request.get_json() or {}
    try:
        amount = int(data.get('amount', 0))
    except (ValueError, TypeError):
        return jsonify({'error': 'invalid amount'}), 400

    if amount <= 0:
        return jsonify({'error': 'amount must be positive'}), 400

    users_collection.update_one(
        {'_id': ObjectId(current_user.id)},
        {'$inc': {'coins': amount}}
    )

    user = users_collection.find_one({'_id': ObjectId(current_user.id)}, {'password': 0})
    coins = user.get('coins', 0)
    return jsonify({'coins': coins}), 200


@app.route('/api/furniture/catalog')
def get_catalog():
    return jsonify(FURNITURE_CATALOG)

@app.route('/api/user/furniture', methods=['GET'])
@login_required
def get_user_furniture():
    user = users_collection.find_one({'_id': ObjectId(current_user.id)})
    equipped = user.get('furniture', {})
    equipped['exterior'] = user.get('house') # Add house to equipped list
    
    inventory = user.get('inventory', [])
    # Ensure current house is in inventory for frontend logic
    if user.get('house') and user.get('house') not in inventory:
        inventory.append(user.get('house'))

    return jsonify({
        'inventory': inventory,
        'equipped': equipped,
        'coins': user.get('coins', 0)
    })

@app.route('/api/furniture/buy', methods=['POST'])
@login_required
def buy_furniture():
    data = request.get_json()
    item_id = data.get('item_id')
    
    # find item price
    price = 0
    found = False
    for category, items in FURNITURE_CATALOG.items():
        for item in items:
            if item['id'] == item_id:
                price = item['price']
                found = True
                break
        if found: break
    
    if not found:
        return jsonify({'error': 'Item not found'}), 404
        
    user = users_collection.find_one({'_id': ObjectId(current_user.id)})
    if user.get('coins', 0) < price:
        return jsonify({'error': 'Not enough coins'}), 400
        
    if item_id in user.get('inventory', []):
        return jsonify({'error': 'Already owned'}), 400

    users_collection.update_one(
        {'_id': ObjectId(current_user.id)},
        {
            '$inc': {'coins': -price},
            '$push': {'inventory': item_id}
        }
    )
    return jsonify({'success': True, 'new_balance': user.get('coins', 0) - price})

@app.route('/api/furniture/equip', methods=['POST'])
@login_required
def equip_furniture():
    data = request.get_json()
    category = data.get('category')
    item_id = data.get('item_id')
    
    if category not in FURNITURE_CATALOG:
        return jsonify({'error': 'Invalid category'}), 400
    
    user = users_collection.find_one({'_id': ObjectId(current_user.id)})
    
    if item_id:
        inventory = user.get('inventory', [])
        # Allow equipping current house even if not in inventory (legacy fix)
        if item_id not in inventory and item_id != user.get('house'):
             return jsonify({'error': 'Item not owned'}), 403

        if category == 'exterior':
            users_collection.update_one(
                {'_id': ObjectId(current_user.id)},
                {'$set': {'house': item_id}}
            )
        else:
            key = f"furniture.{category}"
            users_collection.update_one(
                {'_id': ObjectId(current_user.id)},
                {'$set': {key: item_id}}
            )
    else:
        # Unequip if item_id is None/missing
        if category == 'exterior':
             return jsonify({'error': 'Cannot unequip house'}), 400

        key = f"furniture.{category}"
        users_collection.update_one(
            {'_id': ObjectId(current_user.id)},
            {'$unset': {key: ""}}
        )

    return jsonify({'success': True})

@app.route('/home', methods=['GET', 'POST'])
@login_required
def my_home():
    return render_template('home.html', catalog=FURNITURE_CATALOG, target_user=current_user, is_owner=True)

@app.route('/visit/<user_id>')
@login_required
def visit_home(user_id):
    target_user = User.get(user_id)
    if not target_user:
        flash('User not found')
        return redirect(url_for('map_view'))
    
    is_owner = (user_id == current_user.id)
    if is_owner:
        return redirect(url_for('my_home'))
        
    return render_template('home.html', catalog=FURNITURE_CATALOG, target_user=target_user, is_owner=False)


if __name__ == '__main__':
    app.run(debug=True, port=5001)