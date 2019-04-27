from redis import Redis

from flask import current_app, g
from flask.cli import with_appcontext, click

def get_db():
    if 'db' not in g:
        g.db = Redis(
            host=current_app.config['DATABASE_HOST'],
			port=current_app.config['DATABASE_PORT'],
            db=current_app.config['DATABASE'],
            decode_responses=True
        )

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

@click.command('init-db')
@with_appcontext
def init_db_command():
    db = get_db()
    db.flushdb()


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
