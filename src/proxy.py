import json
import random as rand
import re
from urllib import request

def create():
	offset = rand.randint(0, 15)
	url = 'http://proxydb.net/?protocol=https&anonlvl=4&offset=' + str(offset)
	req = request.Request(url)
	res = request.urlopen(req, timeout=10)
	text = res.read().decode()

	rex = '<tr>\n                <td>\n                    <a href="(?:.*?)">(.*?)</a>'
	pattern = re.compile(rex)
	ip_ports = re.findall(pattern, text)

	rand_i = rand.randrange(0, len(ip_ports))
	ip_port = ip_ports[rand_i]

	# proxies = {
	# 	'http': ip_port,
	# 	'https': ip_port
	# }
	# proxy_handler = request.ProxyHandler(proxies)
	# opener = request.build_opener(proxy_handler)

	# url = 'https://gimmeproxy.com/api/getProxy?get=true&post=true&supportsHttps=true&protocol=http'
	# req = request.Request(url)
	# res = opener.open(req, timeout=20)
	# text = res.read().decode()

	# obj = json.loads(text)
	# ip = obj['ip']
	# port = obj['port']
	# ip_port = obj['ipPort']
	
	return proxy

class Proxy:
	def __init__(self, ip_port):
		self.ip_port = ip_port
