# LICENSE HERE
"""Generates load.
"""

import os
import sys
import time
import random
from flask import Flask, request, render_template, g
from twisted.internet import task
from twisted.internet import reactor
from twisted.web.wsgi import WSGIResource
from twisted.web.server import Site

app = Flask(__name__)
app.debug = True

def load_til(runfor=5.0):
	start = time.clock()
	while (time.clock() - start) * 1000 < runfor:
		pass


@app.route('/')
def index():
	return "I can hurt you. (AKA generate load)."

@app.route('/ignore-me')
def ignore_me():
	return "Ignoring you."
	
@app.route('/tickle-me')
def tickle_me():
	"""Generate 5ms of 100% cpu load"""
	load_til(500.0)
	return "Tickling you. (half-second)"

@app.route('/hurt-me-some')
def hurt_me_some():
	"""Generate 50ms of 100% cpu load"""
	load_til(5000.0)
	return "Hurted you for 5 seconds."

@app.route('/hurt-me-lots')
def hurt_me_lots():
	"""Generate 500ms of 100% cpu load"""
	load_til(50000.0)
	return "Hurted you for 50 seconds."

@app.route('/slay-me')
def slay_me():
	"""Generate terminal load on this machine."""
	load_til(500000.0)
	return "500 seconds of pain."



resource = WSGIResource(reactor, reactor.getThreadPool(), app)
site = Site(resource)
reactor.listenTCP(7000, site)
reactor.run()