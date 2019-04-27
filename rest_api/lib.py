from flask import jsonify, g, current_app, session
from hashids import Hashids
import functools
from uuid import uuid4

def error(mesg):
	return jsonify({'error': mesg})

def get_hash(i):
	if 'hashids' not in g:
		g.hashids = Hashids(salt=current_app.config['SECRET_KEY'])
	return g.hashids.encode(i)

def use_session(view):
	@functools.wraps(view)
	def wrapped(*args, **kwargs):
		if 'id' not in session:
			session['id'] = str(uuid4())
		return view(*args, **kwargs)
	return wrapped