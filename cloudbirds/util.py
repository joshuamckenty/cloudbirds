"""
Utils for cloudbirds
TODO: Some logging stuff
"""

import sys
from twisted.python import log

import logging
import socket

logging.basicConfig(level=logging.WARN)
observer = log.PythonLoggingObserver()
observer.start()

def test_for_socket(host='127.0.0.1', port=8000):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		s.connect((host, port))
		s.shutdown(2)
		return True
	except:
		return False
