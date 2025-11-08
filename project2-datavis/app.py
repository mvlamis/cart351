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

# Last.fm API Configuration
LASTFM_API_KEY = os.getenv('LASTFM_API_KEY')
LASTFM_API_BASE = 'http://ws.audioscrobbler.com/2.0/'

# ReccoBeats API Configuration
RECCOBEATS_API_TRACK = "https://api.reccobeats.com/v1/track?ids={track_id}"
RECCOBEATS_API_AUDIO_FEATURES = "https://api.reccobeats.com/v1/track/{track_id}/audio-features"

# Data storage file
DATA_FILE = 'data/user_data.json'

DEMO_USERNAME = 'WonkaWizard34'

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
    profile = requests.get(f'{SPOTIFY_API_BASE}/me', headers=headers).json()
    recently_played = requests.get(f'{SPOTIFY_API_BASE}/me/player/recently-played?limit=40', headers=headers).json()
    
    tracks = []
    for item in recently_played.get('items', []):
        track = item.get('track', {})
        tracks.append({
            'track_id': track.get('id'),
            'track_name': track.get('name'),
            'artists': [artist.get('name') for artist in track.get('artists', [])],
            'album': track.get('album', {}).get('name'),
            'album_image': track.get('album', {}).get('images', [{}])[0].get('url')
        })
    return {
        'profile': profile,
        'recent_tracks': tracks
    }


def get_lastfm_user_data(username):
    # Get user profile
    profile_params = {
        'method': 'user.getinfo',
        'user': username,
        'api_key': LASTFM_API_KEY,
        'format': 'json'
    }
    profile_resp = requests.get(LASTFM_API_BASE, params=profile_params).json()
    profile = profile_resp.get('user', {})

    # Get recent tracks
    tracks_params = {
        'method': 'user.getrecenttracks',
        'user': username,
        'api_key': LASTFM_API_KEY,
        'limit': 40,
        'format': 'json'
    }
    tracks_resp = requests.get(LASTFM_API_BASE, params=tracks_params).json()
    tracks = []
    for item in tracks_resp.get('recenttracks', {}).get('track', []):
        tracks.append({
            'track_id': item.get('mbid'),
            'track_name': item.get('name'),
            'artists': [item.get('artist', {}).get('#text')],
            'album': item.get('album', {}).get('#text'),
            'album_image': item.get('image', [{}])[-1].get('#text') if item.get('image') else None
        })
    return {
        'profile': profile,
        'recent_tracks': tracks
    }


def get_reccobeats_tracks(id_list):
    track_string = ','.join(id_list)
    url = RECCOBEATS_API_TRACK.format(track_id=track_string)
    
    payload = {}
    headers = {
        'Accept': 'application/json'
    }

    response = requests.get(url, headers=headers)

    return response.json()

def get_reccobeats_audio_features(id):
    url = RECCOBEATS_API_AUDIO_FEATURES.format(track_id=id)
    
    payload = {}
    headers = {
        'Accept': 'application/json'
    }

    response = requests.get(url, headers=headers)

    return response.json()

def search_spotify_track(track_name, artist_name, access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    query = f'track:{track_name} artist:{artist_name}'
    params = {
        'q': query,
        'type': 'track',
        'limit': 1
    }
    resp = requests.get(f'{SPOTIFY_API_BASE}/search', headers=headers, params=params)
    results = resp.json()
    items = results.get('tracks', {}).get('items', [])
    if items:
        return items[0]['id']
    return None

def get_spotify_app_token():
    auth_string = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
    auth_bytes = auth_string.encode('utf-8')
    auth_base64 = base64.b64encode(auth_bytes).decode('utf-8')
    headers = {
        'Authorization': f'Basic {auth_base64}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'client_credentials'
    }
    response = requests.post(SPOTIFY_TOKEN_URL, headers=headers, data=data)
    token_data = response.json()
    return token_data.get('access_token')


# Routes
@app.route('/')
def index():
    spotify_logged_in = 'spotify_token' in session
    lastfm_logged_in = 'lastfm_username' in session

    user_data = None
    recent_tracks = []
    # load user data from reccobeats
    user_id = session.get('current_user_id')
    platform = session.get('current_platform')
    if user_id and platform:
        all_user_data = load_user_data()
        user_data = all_user_data['users'].get(user_id)
        if user_data:
            recent_tracks = user_data.get('reccobeats_data', {}).get('content', [])
            for track in recent_tracks:
                track['audio_features'] = track.get('audio_features', {})

    # hide demo username in user info
    if user_data and user_data.get('profile', {}).get('name') == DEMO_USERNAME:
        user_data['profile']['name'] = 'Demo User'

    return render_template(
        'index.html',
        spotify_logged_in=spotify_logged_in,
        lastfm_logged_in=lastfm_logged_in,
        user_data=user_data,
        recent_tracks=recent_tracks
    )


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
    
    track_ids = [track['track_id'] for track in listening_data['recent_tracks'] if track.get('track_id')]
    reccobeats_data = get_reccobeats_tracks(track_ids)

    for track in reccobeats_data.get('content', []):
        audio_features = get_reccobeats_audio_features(track['id'])
        track['audio_features'] = audio_features
    

    user_data_store['users'][user_id] = {
        'platform': 'spotify',
        'profile': profile,
        'reccobeats_data': reccobeats_data,
        'last_updated': datetime.now().isoformat()
    }

    save_user_data(user_data_store)
    session['current_user_id'] = user_id
    session['current_platform'] = 'spotify'


    return redirect(url_for('index'))


@app.route('/login/lastfm', methods=['GET', 'POST'])
def login_lastfm():
    if request.method == 'POST':
        username = request.form.get('username')
        if not username:
            return "Username required", 400
        session['lastfm_username'] = username
        return redirect(url_for('callback_lastfm'))
    return render_template('lastfm_login.html')


@app.route('/callback/lastfm')
def callback_lastfm():
    username = session.get('lastfm_username')
    if not username:
        return "No Last.fm username in session", 400

    user_data_store = load_user_data()
    listening_data = get_lastfm_user_data(username)
    profile = listening_data['profile']
    user_id = profile.get('name', username)


    spotify_app_token = get_spotify_app_token()
    
    # get reccobeats ids for tracks
    track_ids = []
    for track in listening_data['recent_tracks'][:40]:
        spotify_track_id = search_spotify_track(track['track_name'], track['artists'][0], spotify_app_token)
        if spotify_track_id:
            track_ids.append(spotify_track_id)

    reccobeats_data = get_reccobeats_tracks(track_ids)

    for track in reccobeats_data.get('content', []):
        audio_features = get_reccobeats_audio_features(track['id'])
        track['audio_features'] = audio_features

    user_data_store['users'][user_id] = {
        'platform': 'lastfm',
        'profile': profile,
        'reccobeats_data': reccobeats_data,
        'last_updated': datetime.now().isoformat()
    }

    save_user_data(user_data_store)
    session['current_user_id'] = user_id
    session['current_platform'] = 'lastfm'
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/visual')
def visual():
    if not session.get('current_user_id'):
        return redirect(url_for('index'))
    all_user_data = load_user_data()
    user_id = session['current_user_id']
    user_data = all_user_data['users'].get(user_id)
    listening_data = user_data.get('reccobeats_data', {}) if user_data else {}
    return render_template(
        'visual.html',
        user_id=user_id,
        platform=session['current_platform'],
        listening_data=listening_data
    )


@app.route('/demo')
def demo():
    session['lastfm_username'] = DEMO_USERNAME
    return redirect(url_for('callback_lastfm'))


app.run(debug=True, port=5001)

