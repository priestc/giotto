import redis
import bcrypt

def get_user(id):
	"""
	Given a user id, return the associated user
	"""
	user = redis.get(key=id)
	return user

def new_user(password):
	"""
	Create a new user instance. Passed in is the password of this user
	"""
	encrypted_password = bcrypt # FIXME
	user = GiottoUser(user_id)
	return user

class GiottoUser(object):
	"""
	Barebones class for representing a user
	"""
	user_id = 0
	engine = ''
