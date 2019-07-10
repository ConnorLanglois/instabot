import json
import random
import re
import sms
from bs4 import BeautifulSoup
from http.cookiejar import CookieJar
from time import sleep
from urllib import error, parse, request

class InstapyException(error.URLError):
	def __init__(self, reason, status):
		super().__init__(reason)

		self.status = status

def signup(email, name, username, password, handlers=[]):
	cj, opener = auth(handlers)
	url = 'https://www.instagram.com/accounts/web_create_ajax/' 
	data = {
		'email': email,
		'first_name': name,
		'username': username,
		'password': password
	}
	data_enc = parse.urlencode(data).encode('ASCII')
	req = request.Request(url, data=data_enc)
	res = opener.open(req)
	text = res.read().decode()
	status = json.loads(text)

	if status['account_created'] == True:
		print('Signup success: ' + username + ' ' + password)

		token = [cookie for cookie in cj][0].value
		opener.addheaders[-1] = ('x-csrftoken', token)

		acc = Account(username, token, handlers, opener)

		return acc
	else:
		raise InstapyException('Signup fail: ' + username + ' ' + password, status)

def login(username, password, handlers=[]):
	cj, opener = auth(handlers)
	url = 'https://www.instagram.com/accounts/login/ajax/'
	data = {
		'username': username,
		'password': password
	}
	data_enc = parse.urlencode(data).encode('ASCII')
	req = request.Request(url, data=data_enc)

	try:
		res = opener.open(req)
	except error.HTTPError as e:
		res = e

	text = res.read().decode()
	status = json.loads(text)

	if 'authenticated' in status and status['authenticated'] == True or status['message'] == 'checkpoint_required':
		print('Login success: ' + username + ' ' + password)

		token = [cookie for cookie in cj][0].value
		opener.addheaders[-1] = ('x-csrftoken', token)

		verify(status, token, handlers, opener)

		acc = Account(username, token, handlers, opener)

		return acc
	else:
		raise Exception('Login fail: ' + username + ' ' + password)

def id(username):
	url = f'https://www.instagram.com/{username}'
	req = request.Request(url)
	res = request.urlopen(req)
	text = res.read().decode()

	obj = json.loads(re.findall('window._sharedData = (.+);', BeautifulSoup(text, 'html.parser').find_all('script')[2].text)[0])
	id_ = obj['entry_data']['ProfilePage'][0]['graphql']['user']['id']

	return id_

def auth(handlers=[]):
	cj = CookieJar()
	cookie_handler = request.HTTPCookieProcessor(cj)
	opener = request.build_opener(cookie_handler, *handlers)
	opener.addheaders = [
		('accept', '*/*'),
		('accept-encoding', 'deflate, br'),
		('accept-language', 'en-US,en;q=0.8'),
		('cache-control', 'max-age=0'),
		('content-type', 'application/x-www-form-urlencoded'),
		('origin', 'https://www.instagram.com'),
		('referer', 'https://www.instagram.com/'),
		('user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'),
		('x-instagram-ajax', '1'),
		('x-requested-with', 'XMLHttpRequest')
	]

	url = 'https://www.instagram.com/'
	req = request.Request(url)
	res = opener.open(req)

	ig_vw = random.randint(200, 2000)

	res.headers.add_header('Set-Cookie', 'ig_pr=1')
	res.headers.add_header('Set-Cookie', 'ig_vw=' + str(ig_vw))
	cj.extract_cookies(res, req)
	opener.addheaders.append(('x-csrftoken', [cookie for cookie in cj][0].value))

	return (cj, opener)

def verify(status, token, handlers, opener):
	if 'message' in status and status['message'] == 'checkpoint_required':
		raise Exception('Challenge Denied')

		print('Challenge Accepted')

		ssms = sms.create(handlers)

		sleep(3)

		checkpoint_url = status['checkpoint_url']
		url = 'https://www.instagram.com' + checkpoint_url[checkpoint_url.index('/challenge'):]
		data = {
			'csrfmiddlewaretoken': token,
			'phone_number': ssms.number[2:]
		}
		data_enc = parse.urlencode(data).encode('ASCII')
		req = request.Request(url, data=data_enc)
		res = opener.open(req)
		text = res.read().decode()

		messages = ssms.query_messages()
		body = messages[0]['Body']
		rex = 'Use (.*?) to'
		pattern = re.compile(rex)
		security_code = re.findall(rex, body)[0].replace(' ', '')

		data = {
			'csrfmiddlewaretoken': token,
			'security_code': security_code
		}
		data_enc = parse.urlencode(data).encode('ASCII')
		req = request.Request(url, data=data_enc)
		res = opener.open(req)

class Account:
	def __init__(self, username, token, handlers, opener):
		self.username = username
		self.token = token
		self.handlers = handlers
		self.opener = opener

	def set_profile_picture(self, url):
		req = request.Request(url)
		res = request.urlopen(req)
		bytes_ = res.read()

		data1 = '------WebKitFormBoundary6Xoi262s5uqs6AjI\r\nContent-Disposition: form-data; name="profile_pic"; filename="profilepic.jpg"\r\nContent-Type: image/jpeg\r\n\r\n'
		data2 = '\r\n------WebKitFormBoundary6Xoi262s5uqs6AjI--'
		data1_enc = data1.encode()
		data2_enc = data2.encode()
		data_enc = data1_enc + bytes_ + data2_enc
		headers = {
			'Content-Type': 'multipart/form-data; boundary=----WebKitFormBoundary6Xoi262s5uqs6AjI',
			'Referer': f'https://www.instagram.com/{self.username}/'
		}

		self.post('https://www.instagram.com/accounts/web_change_profile_picture/', data_enc, headers)
		print(f'Set profile picture {url}')

	def remove_profile_picture(self):
		self.post('https://www.instagram.com/accounts/web_change_profile_picture/')
		print(f'Removed profile picture {url}')

	def follow(self, user_id):
		self.post(f'https://www.instagram.com/web/friendships/{user_id}/follow/')
		print(f'Followed {user_id}')

	def unfollow(self, user_id):
		self.post(f'https://www.instagram.com/web/friendships/{user_id}/unfollow/')
		print(f'Unfollowed {user_id}')

	def like(self, post_id):
		self.post(f'https://www.instagram.com/web/likes/{post_id}/like/')
		print(f'Liked {post_id}')

	def unlike(self, post_id):
		self.post(f'https://www.instagram.com/web/likes/{post_id}/unlike/')
		print(f'Unliked {post_id}')

	def verify(self):
		url = 'https://www.instagram.com/'
		req = request.Request(url)

		try:
			res = self.opener.open(req)
		except error.HTTPError as e:
			text = e.read().decode()
			status = json.loads(text)

			verify(status, self.token, self.handlers, self.opener)

	def post(self, url, data_enc=[], headers={}):
		req = request.Request(url, data=data_enc, headers=headers, method='POST')
		res = self.opener.open(req)

		return res
