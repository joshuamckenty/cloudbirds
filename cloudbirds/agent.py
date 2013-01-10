# JMC License header here

"""
CloudBirds agent, runs on each VM

"""


import os
import signal
import sys
import snmp
import subprocess
import json
import random

import requests
from fysom import Fysom
from twisted.internet import reactor
from twisted.internet.protocol import ServerFactory, ProcessProtocol

import util

LOW_PORT = 8001
HIGH_PORT = 9000
OMEGA_PORT = 8000
limits = {'cpu' : 0.5, 'ram' : 0.8}
# TODO - Adapt health check interval based on current state


class EggProcessProtocol(ProcessProtocol):
	def processEnded(self, reason):
		pass

class Agent:
	pass

class CloudBirdAgent(Agent):
	def __init__(self):
		self.become_egg()
		self.momma = None
		self.host = "localhost"
		self.flock = []
		self.antiFlock = []
		self.is_omega = False
		self.port = self.select_port()
		self.add_flock_member(self.omega_url)
		self.add_flock_member(self.url)
	
	def become_egg(self):
		self.fsm = Fysom({
		  'initial': 'egg',
		  'events': [
			{'name': 'hatch',  'src': 'egg',	'dst': 'teenager'},
			{'name': 'grow_up',	 'src': 'teenager', 'dst': 'content'},
			{'name': 'get_stressed',  'src': 'teenager', 'dst': 'content'}, # WRONG AND TEMPORARY
			{'name': 'get_stressed',  'src': 'content', 'dst': 'overwhelmed'},
			{'name': 'get_stressed',  'src': 'overwhelmed', 'dst': 'dying'},
			{'name': 'get_bored', 'src': 'overwhelmed', 'dst': 'content'},
			{'name': 'get_bored', 'src': 'content', 'dst': 'bored'}
		  ]
		})
		self.health = {}

	def select_port(self):
		if not (util.test_for_socket(port=OMEGA_PORT)):
			self.is_omega = True
			print "OMEGA PORT SELECTION"
			return OMEGA_PORT
		while True: # TODO - probably shouldn't run this forever
			port=random.randrange(LOW_PORT, HIGH_PORT)
			if not util.test_for_socket(port=port):
				print "PORT SELECTION : %s" % (port)
				return port
	
	@property
	def omega_url(self):
		return "http://localhost:%s" % (OMEGA_PORT)
	
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
			if self.omega_url == bird_url:
				print "ERROR!! No Omega is bad, need promotion"
				raise
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

	def healthcheck(self):
		if self.fsm.current == "egg":
			return "Eggs don't have health."
		self.health = snmp.get_stats()
		for stat_key in self.health.iterkeys():
			stat_val = self.health[stat_key]
			print "Looking at stat_key of %s with value of %s" % (stat_key, stat_val)
			if stat_key in limits.keys() and stat_val > limits[stat_key]:
				print "Freaking out!"
				if self.fsm.current == 'dying':
					return "Too overwhelmed, dying."
				self.fsm.get_stressed()
				return self.fsm.current

	def tick(self):
		if self.is_omega and self.fsm.current == 'egg':
			self.fsm.hatch()
		self.healthcheck()

	def become_omega(self):
		old_port = self.port
		self.is_omega = True
		self.remove_flock_member(self.url)
		self.port = OMEGA_PORT
		self.add_flock_member(self.url)
		if self.fsm.current == 'egg':
			self.fsm.hatch()
		self.spawn()

	def imprint(self):
		pass
	
	def spawn(self):
		old_port = self.port
		pp = EggProcessProtocol()
		command = [sys.executable]
		command.extend(sys.argv)
		command.extend(['momma', '%s' % old_port])
		print "Command for spawn is %s" % command
		subprocess = reactor.spawnProcess(pp, command[0], command, {'MOMMA_BIRD' : self.url}, childFDs = { 0: 0, 1: 1, 2: 2})
				# 
				# if _fork(remain=True): # Runs in spawned child only
				#	_decouple()
				#	_fork(remain=False)
				#	_rebind()
				#	self.port = self.select_port()
				#	self.momma = old_port
				#	self.become_egg()
		# subprocess.call("python %s" % (" ".join(sys.argv)), shell=True)
		return "Okay."
	
	def die(self):
		sys.exit(0)
	
	def adopt(self, child):
		pass