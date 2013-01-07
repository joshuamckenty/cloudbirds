# LICENSE HERE
"""
Yer basic cloudbird daemon, runs on every host.
TODO:
Security of this interface
"""
import random
from flask import Flask, render_template, g
from twisted.internet import task
from twisted.internet import reactor
from twisted.web.wsgi import WSGIResource
from twisted.web.server import Site

import agent
import util
import requests

LOW_PORT = 8001
HIGH_PORT = 9000
OMEGA_PORT = 8000

OMEGA = False

# If there's no omega, I need to be omega
if not (util.test_for_socket(port=OMEGA_PORT)):
	OMEGA = True

def pick_port():
	if OMEGA: return OMEGA_PORT
	while True: # TODO - probably shouldn't run this forever
		port=random.randrange(LOW_PORT, HIGH_PORT)
		if not util.test_for_socket(port=port):
			return port
			
birdport = pick_port()	
app = Flask(__name__)
app.debug = True
app.myBird = agent.CloudBirdAgent(birdport)

@app.route('/tellme/<bird>')
def tell_me(bird='9001'):
	"""Receives gossip messages from other birds in the flock
	"""
	app.myBird.add_flock_member(bird)
	print "Adding a flock member of %s" % bird
	return "Okay."

@app.route('/gossip')
def gossip():
	"""Sends gossip messages.
	Always sends news to the OMEGA (for now), # TODO THIS!
	Randomly sends to other birds."""
	target_bird = random.choice(app.myBird.flock)
	if target_bird == app.myBird.port:
		return "Don't like to talk to myself."
	for bird in app.myBird.flock: # Should be random later
		# TODO: Batch up these calls
		url = "http://localhost:%s/tellme/%s" % (target_bird, bird)
		print "Going to fetch against %s", url
		requests.get(url)
	return "Did it."


@app.route('/')
@app.route('/hello')
@app.route('/hello/<name>')
def index(name='World'):
	print "got request"
	return "<b>Hello %(name)s</b>!<br/>I am an: %(state)s bird" % {'name' :name, 'state' : app.myBird.fsm.current}

@app.route('/flock')
def report_flock():
	return "<b>Heres what weve got: %(flock)s</b>" % {'flock': app.myBird.flock}

l = task.LoopingCall(gossip)
l.start(3.0) # call every second
# l.stop() will stop the looping calls

resource = WSGIResource(reactor, reactor.getThreadPool(), app)
site = Site(resource)
print "Going to run on ", birdport
reactor.listenTCP(birdport, site)
reactor.run()

# run(host='localhost', port=birdport)


# http://highscalability.com/blog/2011/11/14/using-gossip-protocols-for-failure-detection-monitoring-mess.html
# http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.160.2604
# http://pysnmp.sourceforge.net/examples/current/index.html