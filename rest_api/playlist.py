import functools
from flask import current_app, Blueprint, request, session, jsonify, redirect, url_for, session
from rest_api.db import get_db
from rest_api.spotify import spotify_token, verify_song
from rest_api.lib import get_hash, error, use_addr_hash, use_dummy_addr_hash
import random

bp = Blueprint('playlist', __name__, url_prefix='')

def playlist_exists(view):
	@functools.wraps(view)
	def wrapped(*args, **kwargs):
		db = get_db()
		if request.method == 'GET':
			playlist = request.args.get('playlist')
		if request.method == 'POST':
			json = request.get_json() or {}
			playlist = json.get('playlist')
		if not playlist: 
			return error('invalid payload: missing playlist id'), 400
		if not db.sismember('playlists', playlist):
			return error('playlist does not exist'), 404
		kwargs["playlist"] = playlist
		return view(*args, **kwargs)
	return wrapped


@bp.route('/create', methods=['POST'])
def r_create():
	db = get_db()
	json = request.get_json() or {}
	name = json.get('name')
	if not name:
		return error('invalid payload: missing playlist name'), 400
	next_id = db.incr('next_id')
	hash_id = get_hash(next_id)
	db.sadd('playlists', hash_id)
	db.set(f'playlist:{hash_id}', name)
	return jsonify({'id': hash_id}), 201

@spotify_token
def add_song(addr_hash, playlist, song):
	db = get_db()
	if not verify_song(song):
		return error('invalid song: bad song uri')
	db.sadd(f'playlist:{playlist}:songs', song)
	db.sadd(f'playlist:{playlist}:song:{song}', addr_hash)
	return ':)', 201

@bp.route('/vote', methods=['POST'])
@playlist_exists
@use_addr_hash
def r_vote(addr_hash, playlist):
	db = get_db()
	json = request.get_json() or {}
	song = json.get('song')
	if not song:
		return error('invalid payload: missing song id'), 400
	if not db.sismember(f'playlist:{playlist}:songs', song):
		return add_song(addr_hash, playlist, song)
	db.sadd(f'playlist:{playlist}:song:{song}', addr_hash)
	return ':)', 200

@bp.route('/dummy_vote', methods=['POST'])
@playlist_exists
@use_dummy_addr_hash
def r_dummy_vote(addr_hash, playlist):
	return r_vote(addr_ash, playlist)

@bp.route('/songs', methods=['GET'])
@playlist_exists
def r_songs(playlist):
	db = get_db()
	song_ids = list(db.smembers(f'playlist:{playlist}:songs'))
	songs = [{'id': s, 'votes': db.scard(f'playlist:{playlist}:song:{s}')} for s in song_ids]
	name = db.get(f'playlist:{playlist}')
	return jsonify({ 'name': name, 'songs': songs })


@bp.route('/shuffle', methods=['GET'])
@playlist_exists
def r_shuffle(playlist):
	db = get_db()
	song_ids = list(db.smembers(f'playlist:{playlist}:songs'))
	random.shuffle(song_ids)
	songs = [{'id': s} for s in song_ids]
	return jsonify({'songs': songs})