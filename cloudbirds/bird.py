# LICENSE HERE
"""
Yer basic cloudbird daemon, runs on every host.
TODO:
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

import agent

app = Flask(__name__)
app.debug = True
app.myBird = agent.CloudBirdAgent()
app.listeningPort = None
app.boundPort = None


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



def restartListener(port):
	print "Going to run on %s" % (port)
	app.boundPort = port
	if app.listeningPort:
		app.listeningPort.stopListening()
	app.listeningPort = reactor.listenTCP(port, site)


@app.route('/')
@app.route('/hello')
@app.route('/hello/<name>')
def index(name='World'):
	return "<b>Hello %(name)s</b>!<br/>I am an: %(state)s bird [%(health)s]" % {
		'name' :name, 'state' : app.myBird.fsm.current, 'health' : app.myBird.health}


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
	except: # TODO (Custom Exception)
		app.myBird.become_omega()
		restartListener(app.myBird.port)

@app.route('/tick')
def tick():
	"""Polls SNMP data for system health.
	Stored health data will be gossip'd."""
	print "Ticking on %s ..." % (app.myBird.port)
	# If the listening port doesn't match the internal port,
	# restart the Listener
	if app.boundPort != app.myBird.port:
		print "Bouncing the listener"
		restartListener(app.myBird.port)
	return app.myBird.tick()


@app.route('/spawn')
def spawn():
	return app.myBird.spawn()

@app.route('/die')
def die():
	print "Bye."
	reactor.stop()
	return "Bye"
	# return app.myBird.die()
		
print "I was called like this: %s" % (sys.argv)

if 'momma' in sys.argv:
	print "I'm a BABY!"
	print os.environ.get('MOMMA_BIRD')
	port = sys.argv[sys.argv.index('momma')+1]
	print "Baby of %s" % port
	_fork() and _decouple()
	_fork() and _rebind()
	app.myBird.momma = port
	


resource = WSGIResource(reactor, reactor.getThreadPool(), app)
site = Site(resource)
restartListener(app.myBird.port)
gossiploop = task.LoopingCall(gossip)
tickloop = task.LoopingCall(tick)
gossiploop.start(3.0) # call every three seconds
tickloop.start(5.0) # call every 30 seconds
reactor.run()