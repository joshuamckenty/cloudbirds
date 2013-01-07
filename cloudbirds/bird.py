# LICENSE HERE
"""
Yer basic cloudbird daemon, runs on every host.
TODO:
Security of this interface
"""

import random
from flask import Flask, request, render_template, g
from twisted.internet import task
from twisted.internet import reactor
from twisted.web.wsgi import WSGIResource
from twisted.web.server import Site

import agent
import util

LOW_PORT = 8001
HIGH_PORT = 9000
OMEGA_PORT = 8000

OMEGA = False

def pick_port():
	if OMEGA: return OMEGA_PORT
	while True: # TODO - probably shouldn't run this forever
		port=random.randrange(LOW_PORT, HIGH_PORT)
		if not util.test_for_socket(port=port):
			return port


# If there's no omega, I need to be omega
if not (util.test_for_socket(port=OMEGA_PORT)):
	OMEGA = True			
birdport = pick_port()	
app = Flask(__name__)
app.debug = True
app.myBird = agent.CloudBirdAgent(birdport)


@app.route('/')
@app.route('/hello')
@app.route('/hello/<name>')
def index(name='World'):
	print "got request"
	return "<b>Hello %(name)s</b>!<br/>I am an: %(state)s bird" % {'name' :name, 'state' : app.myBird.fsm.current}


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
	return "<b>Heres what we've got: %(flock)s</b>" % {'flock': app.myBird.flock}


@app.route('/gossip')
def gossip():
	"""Sends gossip messages.
	Randomly sends to other birds."""
	return app.myBird.gossip()


l = task.LoopingCall(gossip)
# l.stop() will stop the looping calls

resource = WSGIResource(reactor, reactor.getThreadPool(), app)
site = Site(resource)
print "Going to run on ", birdport
reactor.listenTCP(birdport, site)
l.start(3.0) # call every second
reactor.run()

# http://highscalability.com/blog/2011/11/14/using-gossip-protocols-for-failure-detection-monitoring-mess.html
# http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.160.2604
# http://pysnmp.sourceforge.net/examples/current/index.html