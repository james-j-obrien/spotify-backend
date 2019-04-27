import functools
from flask import current_app, g, Blueprint, request, session, jsonify
from rest_api.db import get_db
from rest_api.lib import error
from datetime import datetime, timedelta
import requests

bp = Blueprint('spotify', __name__, url_prefix='/spotify')

def get_token():
	r = requests.post(current_app.config["SPOTIFY_TOKEN"], data={
		'grant_type': 'client_credentials'
	}, headers={
		'Authorization': f'Basic {current_app.config["SPOTIFY_KEY"]}'
	})
	json = r.json() or {}
	if 'access_token' not in json:
		return False
	else: 
		g.spotify_token = json['access_token']
		g.spotify_expiry = datetime.now() + timedelta(seconds=int(json['expires_in']))
	return True

def refresh_token():
	if 'spotify' not in g or g.spotify_expiry < datetime.now():
		return get_token()
	return True	

def spotify_token(view):
	@functools.wraps(view)
	def wrapped(*args, **kwargs):
		if not refresh_token():
			return error('failed to authenticate with spotify API'), 500
		return view(*args, **kwargs)
	return wrapped

def verify_song(song):
	r = requests.get(f'{current_app.config["SPOTIFY_TRACK"]}/{song}', headers={
		'Authorization': f'Bearer {g.spotify_token}'
	})
	return r.json() and 'error' not in r.json()

@bp.route('/search', methods=['POST'])
@spotify_token
def search():
	json = request.get_json() or {}
	query = json.get('query')
	if not query:
		return error('invalid payload: missing query string'), 400
	r = requests.get(current_app.config['SPOTIFY_SEARCH'], params={
		'q': query,
		'type': 'track',
		'limit': 10,
	}, headers={
		'Authorization': f'Bearer {g.spotify_token}'
	})
	json = r.json() or {}
	if 'tracks' not in json:
		return error('bad response from spotify API'), 500
	tracks = json["tracks"]["items"]
	return jsonify({'songs': tracks}), 200