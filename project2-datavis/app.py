import os
import json
from datetime import datetime
from flask import Flask, render_template, session, redirect, url_for, request
import requests
from dotenv import load_dotenv
import base64
from urllib.parse import urlencode
import secrets

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# Spotify OAuth Configuration
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')
SPOTIFY_AUTH_URL = 'https://accounts.spotify.com/authorize'
SPOTIFY_TOKEN_URL = 'https://accounts.spotify.com/api/token'
SPOTIFY_API_BASE = 'https://api.spotify.com/v1'

# Data storage file
DATA_FILE = 'data/user_data.json'

# Ensure data directory exists
os.makedirs('data', exist_ok=True)

# Initialize data file if it doesn't exist
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump({'users': {}}, f)


def load_user_data():
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            if isinstance(data.get('users'), list):
                data['users'] = {}
                save_user_data(data)
            return data
    except:
        return {'users': {}}


def save_user_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)


# Spotify OAuth Functions
def get_spotify_auth_url():
    state = secrets.token_urlsafe(16)
    session['spotify_auth_state'] = state
    
    params = {
        'client_id': SPOTIFY_CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': SPOTIFY_REDIRECT_URI,
        'state': state,
        'scope': 'user-top-read user-read-recently-played user-library-read user-read-private'
    }
    
    return f"{SPOTIFY_AUTH_URL}?{urlencode(params)}"


def exchange_spotify_code(code):
    auth_string = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
    auth_bytes = auth_string.encode('utf-8')
    auth_base64 = base64.b64encode(auth_bytes).decode('utf-8')
    
    headers = {
        'Authorization': f'Basic {auth_base64}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': SPOTIFY_REDIRECT_URI
    }
    
    response = requests.post(SPOTIFY_TOKEN_URL, headers=headers, data=data)
    return response.json()


def get_spotify_user_data(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    
    # Get user profile
    profile = requests.get(f'{SPOTIFY_API_BASE}/me', headers=headers).json()
    
    # Get top tracks
    top_tracks = requests.get(f'{SPOTIFY_API_BASE}/me/top/tracks?time_range=short_term&limit=50', headers=headers).json()
    
    # Get top artists
    top_artists = requests.get(f'{SPOTIFY_API_BASE}/me/top/artists?time_range=short_term&limit=50', headers=headers).json()
    
    # Get recently played
    recently_played = requests.get(f'{SPOTIFY_API_BASE}/me/player/recently-played?limit=50', headers=headers).json()
    
    return {
        'profile': profile,
        'top_tracks': top_tracks.get('items', []),
        'top_artists': top_artists.get('items', []),
        'recently_played': recently_played.get('items', [])
    }


# Routes
@app.route('/')
def index():
    spotify_logged_in = 'spotify_token' in session
    
    user_data = None
    if 'current_user_id' in session:
        user_data_store = load_user_data()
        user_id = session['current_user_id']
        if user_id in user_data_store['users']:
            user_data = user_data_store['users'][user_id]
    
    return render_template('index.html', 
                         spotify_logged_in=spotify_logged_in,
                         user_data=user_data)


@app.route('/login/spotify')
def login_spotify():
    return redirect(get_spotify_auth_url())


@app.route('/callback/spotify')
def callback_spotify():
    error = request.args.get('error')
    if error:
        return f"Error: {error}", 400
    
    code = request.args.get('code')
    state = request.args.get('state')
    
    if state != session.get('spotify_auth_state'):
        return "State mismatch error", 400
    
    token_data = exchange_spotify_code(code)
    
    if 'access_token' not in token_data:
        return "Failed to get access token", 400
    
    # store token in session
    session['spotify_token'] = token_data['access_token']
    session['spotify_refresh_token'] = token_data.get('refresh_token')
    
    listening_data = get_spotify_user_data(token_data['access_token'])
    profile = listening_data['profile']
    user_id = profile.get('id', 'unknown')
    
    user_data_store = load_user_data()

    if user_id not in user_data_store['users']:
        user_data_store['users'][user_id] = {
            'platform': 'spotify',
            'profile': profile,
            'history': []
        }
    
    user_data_store['users'][user_id]['history'].append({
        'timestamp': datetime.now().isoformat(),
        'data': listening_data
    })
    
    save_user_data(user_data_store)
    session['current_user_id'] = user_id
    session['current_platform'] = 'spotify'
    
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


app.run(debug=True, port=5000)

