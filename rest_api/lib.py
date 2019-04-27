from flask import jsonify, g, current_app, session, request
from hashids import Hashids
import functools
from uuid import uuid4
from hashlib import sha256

def error(mesg):
	return jsonify({'error': mesg})

def get_hash(i):
	if 'hashids' not in g:
		g.hashids = Hashids(salt=current_app.config['SECRET_KEY'])
	return g.hashids.encode(1, i)

def use_addr_hash(view):
	@functools.wraps(view)
	def wrapped(*args, **kwargs):
		kwargs['addr_hash'] = sha256(request.remote_addr.encode('utf-8')).hexdigest()
		return view(*args, **kwargs)
	return wrapped

def use_dummy_addr_hash(view):
	@functools.wraps(view)
	def wrapped(*args, **kwargs):
		kwargs['addr_hash'] = sha256(str(uuid4().encode('utf-8'))).hexdigest()
		return view(*args, **kwargs)
	return wrapped