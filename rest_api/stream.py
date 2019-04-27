from flask import Blueprint, Response
from rest_api.db import get_db
from rest_api.playlist import playlist_exists

bp = Blueprint('stream', __name__, url_prefix='/stream')

def vote_stream(db, playlist):
    pubsub = db.pubsub(ignore_subscribe_messages=True)
    pubsub.psubscribe(f'__keyspace@0__:playlist:{playlist}:song:*')

    for message in pubsub.listen():
        yield f'data: {message["channel"].split(":")[-1]}\n\n'

@bp.route('/', methods=['GET'])
@playlist_exists
def r_stream(playlist):
    db = get_db()
    if not db.sismember('playlists', playlist):
        return 'playlist does not exist', 404
    return Response(vote_stream(db, playlist), mimetype="text/event-stream")