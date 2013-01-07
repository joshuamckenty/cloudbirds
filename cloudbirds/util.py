"""
Utils for cloudbirds
TODO: Some logging stuff
"""
import socket

def test_for_socket(host='127.0.0.1', port=8000):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		s.connect((host, port))
		s.shutdown(2)
		return True
	except:
		return False