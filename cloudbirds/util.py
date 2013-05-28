"""
Utils for cloudbirds
TODO: Some logging stuff
"""

import sys
from twisted.python import log

import os
import json
import logging
import socket

def test_for_socket(host='127.0.0.1', port=8000):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		s.connect((host, port))
		s.shutdown(2)
		return True
	except:
		return False

def get_config(path='config.json'):
	# TODO: Memoize
	with open(path, "r") as config_file:
		return json.loads(config_file.read())

def daemonize():
	_fork()
	_decouple()
	_fork()
	_rebind()

def _fork():
	""" Fork ourselves."""
	try:
		if os.fork():
			sys.exit(0)
	except OSError, e:
		sys.exit("Couldn't fork: %s" % (e))

def _decouple():
	""" Decouple the child from the parent """
	# os.chdir('/')
	os.umask(0)
	os.setsid()

def _rebind():
	""" Rebind stdin/stderr/stdout """
	return # TEMP
	[f.close() for f in [sys.stdin, sys.stderr, sys.stdout]]

	sys.stdin = os.open('/dev/null', os.O_RDONLY)
	sys.stderr = os.open('/dev/null', os.O_WRONLY)
	sys.stdout = os.open('/dev/null', os.O_WRONLY)


logging.basicConfig(level=getattr(logging, get_config().get('log_level', 'WARN').upper()))
observer = log.PythonLoggingObserver()
observer.start()