import json
import instapy
import proxy
import random
import tor
import user
from enum import Enum
from threading import Thread
from time import sleep
from urllib import error, request

class Mode(Enum):
	SIGNUP = 0
	LOGIN = 1

def bot(func, *args, n_threads=1):
	threads = [Thread(target=func, args=args, daemon=True) for i in range(0, n_threads - 1)]

	for thread in threads:
		thread.start()

	func(*args)

def follow_bot(usernames, follows=1, mode=Mode.SIGNUP):
	user_ids = [instapy.id(username) for username in usernames]

	for i in range(0, follows):
		print(i + 1)

		acc = account_bot(i, mode)

		for user_id in user_ids:
			try:
				acc.follow(user_id)
			except Exception as e:
				pass

def like_bot(post_ids, likes=1, mode=Mode.SIGNUP):
	for i in range(0, likes):
		print(i + 1)

		acc = account_bot(i, mode)

		for post_id in post_ids:
			try:
				acc.like(post_id)
			except Exception as e:
				print(e.reason)

def account_bot(index=0, mode=Mode.SIGNUP):
	handlers = get_handlers()

	if mode == Mode.SIGNUP:
		acc = signup_bot(handlers)
	elif mode == Mode.LOGIN:
		account = read_account(index)
		username = account['username']
		password = account['password']

		acc = login_bot(username, password, handlers)

	return acc

def signup_bot(handlers=[]):
	try:
		userr = user.create(handlers)
		acc = instapy.signup(userr.email.address, userr.name, userr.username, userr.password, handlers)

		# write_account(userr.username, userr.password)
		# acc.verify()
		acc.set_profile_picture(userr.picture)

		return acc
	except instapy.InstapyException as e:
		# print(e, e.status)

		errors = e.status['errors']

		if 'ip' in errors and errors['ip'][0].find('The IP address you are using has been flagged as an open proxy.') >= 0:
			sleep(tor.clean())

		return signup_bot(handlers)
	except error.HTTPError as e:
		# print(e)

		if e.code == 403:
			sleep(tor.clean())

		return signup_bot(handlers)
	except Exception as e:
		# print(e)

		return signup_bot(handlers)

def login_bot(username, password, handlers=[]):
	try:
		acc = instapy.login(username, password, handlers)
	except error.HTTPError as e:
		print(e)

	return acc

def get_handlers():
	proxy_handler = get_proxy_handler()
	handlers = [proxy_handler]

	return handlers

def get_proxy_handler():
	pproxy = proxy.Proxy('127.0.0.1:8118')
	proxies = {
		'http': pproxy.ip_port,
		'https': pproxy.ip_port
	}
	proxy_handler = request.ProxyHandler(proxies)

	return proxy_handler

def write_account(username, password):
	with threading.Lock, open('accounts.txt', 'a+') as file:
		file.seek(0)

		text = file.read()
		accounts = json.loads(text) if text != '' else []
		info = {
			'username': username,
			'password': password
		}

		accounts.append(info)
		file.seek(0)
		file.truncate()
		json.dump(accounts, file)

def read_account(index):
	accounts = read_accounts()
	account = accounts[index]

	return account

def read_accounts():
	with open('accounts.txt') as file:
		text = file.read()
		accounts = json.loads(text)

	return accounts

bot(follow_bot, [''], 100)
