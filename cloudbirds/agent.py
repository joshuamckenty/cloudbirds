# JMC License header here

"""
CloudBirds agent, runs on each VM

"""

import json
import random
import requests
from fysom import Fysom



class Agent:
	pass

class CloudBirdAgent(Agent):
	def __init__(self, port):
		self.fsm = Fysom({
		  'initial': 'egg',
		  'events': [
		    {'name': 'hatch',  'src': 'egg',    'dst': 'teenager'},
		    {'name': 'grow_up',  'src': 'teenager', 'dst': 'content'},
		    {'name': 'get_stressed',  'src': 'content', 'dst': 'overwhelmed'},
		    {'name': 'get_bored', 'src': 'overwhelmed', 'dst': 'content'},
		    {'name': 'get_bored', 'src': 'content', 'dst': 'bored'}
		  ]
		})
		
		self.momma = None
		self.host = "localhost"
		self.port = str(port)
		self.flock = ['http://localhost:8000']
		self.antiFlock = []
		self.add_flock_member(self.url)
	
	@property
	def url(self):
		return "http://%s:%s" % (self.host, self.port)
	
	def add_flock_member(self, bird_url):
		if not bird_url in self.flock:
			self.flock.append(bird_url)
		if bird_url in self.antiFlock:
			self.antiFlock.remove(bird_url)
	
	def remove_flock_member(self, bird_url):
		if bird_url in self.flock:
			self.flock.remove(bird_url)
		if not bird_url in self.antiFlock:
			self.antiFlock.append(bird_url)
	
	def gossip(self):
		bird_url = random.choice(self.flock)
		if bird_url == self.url:
			return "Don't like to talk to myself."
		url = "%s/tellme/%s" % (bird_url, self.port)
		actions = [{'action': 'saw_bird', 'bird_url': saw_bird} for saw_bird in self.flock]
		actions.extend([{'action': 'dead_bird', 'bird_url': dead_bird} for dead_bird in self.antiFlock])
		msg = json.dumps(actions)
		try:
			requests.post(url, data={'msg': msg})
		except requests.exceptions.ConnectionError, e:
			# I don't believe in this bird anymore
			self.remove_flock_member(bird_url)
		return "Did it."
	
	def process_gossip(self, msg):
		print "Got some gossip with msg %s" % msg
		messages = json.loads(msg)
		for msg in messages:
			if msg['action'] == "saw_bird":
				self.add_flock_member(msg['bird_url'])
				print "Adding a flock member of %s" % msg['bird_url']
			if msg['action'] == "dead_bird":
				self.remove_flock_member(msg['bird_url'])
				print "Removing a flock member of %s" % msg['bird_url']

	def imprint(self):
		pass
	
	def spawn(self):
		pass
	
	def adopt(self, child):
		pass