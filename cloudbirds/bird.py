# JMC License header here
"""
Yer basic cloudbird daemon, runs on every host.
TODO(JMC):
Security of this interface
"""

import os
import sys
import random
from flask import Flask, request, render_template, g
from twisted.internet import task
from twisted.internet import reactor
from twisted.web.wsgi import WSGIResource
from twisted.web.server import Site
import logging

import agent
import util

CONFIG = util.get_config()


app = Flask(__name__)
app.debug = True
app.myBird = agent.CloudBirdAgent()
app.listeningPort = None
app.boundPort = None


def restartListener(port):
	logging.info("Going to run on %s" % (port))
	app.boundPort = port
	if app.listeningPort:
		app.listeningPort.stopListening()
	app.listeningPort = reactor.listenTCP(port, site)


@app.route('/')
@app.route('/hello')
@app.route('/hello/<name>')
def index(name='World'):
	return "<b>Hello %(name)s</b>!<br/>I am an: %(state)s bird<br/> [%(health)s]<br/>Momma: %(momma)s" % {
		'name' :name, 'state' : app.myBird.fsm.current, 'health' : app.myBird.health, 'momma' : app.myBird.momma}


@app.route('/tellme/<frombird>', methods=['POST'])
def tell_me(frombird='9001'):
	"""Receives gossip messages from other birds in the flock
	MSG is in format:
	msg = 
	[{'action': 'saw_bird', 'bird_url': 'URL'},
	{'action': 'dead_bird', 'bird_url': 'URL'}]
	"""
	app.myBird.process_gossip(request.form['msg'])
	return "Okay."


@app.route('/flock')
def report_flock():
	flock_listing = ["<li><a href='%(bird)s'>%(bird)s</a></li>" % {'bird' : bird} for bird in app.myBird.flock]
	return "<b>Heres what we've got: <ul> %(flock)s </ul></b>" %  {'flock': "".join(flock_listing)}


@app.route('/gossip')
def gossip():
	"""Sends gossip messages.
	Randomly sends to other birds."""
	try:
		app.myBird.gossip()
	except: # TODO(JMC): (Custom Exception)
		app.myBird.become_omega()
		restartListener(app.myBird.port)

@app.route('/tick')
def tick():
	"""Polls SNMP data for system health.
	Stored health data will be gossip'd."""
	logging.debug("Ticking on %s ..." % (app.myBird.port))
	# If the listening port doesn't match the internal port,
	# restart the Listener
	if app.boundPort != app.myBird.port:
		logging.info("Bouncing the listener")
		restartListener(app.myBird.port)
	return app.myBird.tick()


@app.route('/spawn')
def spawn():
	return app.myBird.spawn()

@app.route('/die')
def die():
	logging.info("Bye.")
	reactor.stop()
	return "Bye"
	# return app.myBird.die()
		
logging.debug("I was called like this: %s" % (sys.argv))

if os.environ.get('MOMMA_BIRD'):
	logging.debug("I'm a BABY!")
	logging.info("ENV says momma is %s" % os.environ.get('MOMMA_BIRD'))
	util.daemonize()
	app.myBird.momma = os.environ.get('MOMMA_BIRD')


resource = WSGIResource(reactor, reactor.getThreadPool(), app)
site = Site(resource)
restartListener(app.myBird.port)
gossiploop = task.LoopingCall(gossip)
tickloop = task.LoopingCall(tick)
gossiploop.start(CONFIG['gossip_interval'])
tickloop.start(CONFIG['tick_interval'])
reactor.run()