import eemail
import json
import random as rand
from urllib import request

def create(handlers=[]):
	opener = request.build_opener(*handlers)

	url = 'https://randomuser.me/api'
	req = request.Request(url)
	res = opener.open(req)
	text = res.read().decode()
	info = json.loads(text)

	first = info['results'][0]['name']['first']
	last = info['results'][0]['name']['last']
	name = first.capitalize() + ' ' + last.capitalize()
	username = (first + last + str(rand.randint(100, 999))).replace(' ', '')
	password = info['results'][0]['login']['password'] + str(rand.randint(100, 999))

	if not all([len(s.encode()) == len(s) for s in (first, last, username, password)]):
		return create()

	email = eemail.generate()
	picture = info['results'][0]['picture']['large']

	return User(email, name, username, password, picture)

class User:
	def __init__(self, email, name, username, password, picture):
		self.email = email
		self.name = name
		self.username = username
		self.password = password
		self.picture = picture
