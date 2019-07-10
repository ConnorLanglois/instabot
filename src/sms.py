import json
import re
from http.cookiejar import CookieJar
from time import sleep
from urllib import parse, request

def create(handlers=[]):
	cj = CookieJar()
	cookie_handler = request.HTTPCookieProcessor(cj)
	opener = request.build_opener(cookie_handler, *handlers)
	opener.addheaders = [
		('Connection', 'keep-alive'),
		('Host', '10minsms.com'),
		('Origin', 'https://10minsms.com'),
		('Referer', 'https://10minsms.com/'),
		('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'),
		('X-Requested-With', 'XMLHttpRequest')
	]

	url = 'https://10minsms.com/session/createFree'
	req = request.Request(url, method='POST')
	res = opener.open(req)
	text = res.read().decode()

	session = json.loads(text)
	number = session['assigned_phone_number']
	session_uuid = session['session_uuid']

	return SMS(number, session_uuid, opener)

class SMS:
	def __init__(self, number, session_uuid, opener):
		self.number = number
		self.session_uuid = session_uuid
		self.opener = opener

		print(number, session_uuid)

	def query_messages(self, interval=5, times=None):
		def get_messages():
			url = 'https://10minsms.com/messages/getMessagesByID'
			data = {
				'sessionUUID': self.session_uuid
			}
			data_enc = parse.urlencode(data).encode()
			headers = {
				'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
			}
			req = request.Request(url, data_enc)
			res = self.opener.open(req)
			text = res.read().decode()

			messages = json.loads(text)

			return messages

		while times is None or times > 0:
			messages = get_messages()

			print(messages, end='', flush=True)

			if len(messages) > 0:
				print()

				return messages
			else:
				times = times - 1 if times is not None else None

				sleep(interval)

		raise Exception('Timeout')
