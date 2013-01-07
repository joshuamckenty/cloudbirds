# LICENSE HERE
"""
Yer basic cloudbird daemon, runs on every host.
TODO:
Security of this interface
"""
import random
from bottle import route, run, template
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
myBird = agent.CloudBirdAgent(birdport)

@route('/tellme/:bird')
def tell_me(bird='9001'):
	"""Receives gossip messages from other birds in the flock
	"""
	myBird.add_flock_member(bird)
	return "Okay."

@route('/gossip')
def gossip():
	"""Sends gossip messages.
	Always sends news to the OMEGA (for now), # TODO THIS!
	Randomly sends to other birds."""
	target_bird = random.choice(myBird.flock)
	if target_bird == myBird.port:
		return "Don't like to talk to myself."
	for bird in myBird.flock: # Should be random later
		# TODO: Batch up these calls
		url = "http://localhost:%s/tellme/%s" % (target_bird, bird)
		print "Going to fetch against %s", url
		requests.get(url)


@route('/')
@route('/hello')
@route('/hello/:name')
def index(name='World'):
	print "got request"
	return template('<b>Hello {{name}}</b>!<br/>I am an: {{state}} bird', name=name, state=myBird.fsm.current)


@route('/flock')
def report_flock():
	return template('<b>Heres what weve got: {{flock}}</b>', flock=myBird.flock)


run(host='localhost', port=birdport)