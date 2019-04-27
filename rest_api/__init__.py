import os

from flask import Flask
from flask_cors import CORS

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    CORS(app)

    app.config.from_mapping(
        SECRET_KEY=os.environ['SECRET_KEY'],

        DATABASE_HOST='localhost',
        DATABASE_PORT=6379,
        DATABASE=0,

        SPOTIFY_SEARCH='https://api.spotify.com/v1/search',
        SPOTIFY_TOKEN='https://accounts.spotify.com/api/token',
        SPOTIFY_TRACK='https://api.spotify.com/v1/tracks',
        SPOTIFY_KEY=os.environ['SPOTIFY_KEY']
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

    from . import playlist
    app.register_blueprint(playlist.bp)

    from . import spotify
    app.register_blueprint(spotify.bp)

    from . import stream
    app.register_blueprint(stream.bp)

    return app