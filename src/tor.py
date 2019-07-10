from stem import Signal
from stem.control import Controller

def clean():
	print('Changing IP address...')

	with Controller.from_port(port = 9051) as controller:
		controller.authenticate()
		controller.signal(Signal.NEWNYM)

		wait = controller.get_newnym_wait()

	return wait
