# JMC License header here

"""
CloudBirds agent, runs on each VM

"""

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
		self.port = str(port)
		self.flock = ['8000']
		self.add_flock_member(self.port)
	
	def add_flock_member(self, bird):
		if not bird in self.flock:
			self.flock.append(bird)
	
	def mainloop(self):
		# Poll my current system state via snmp
		# Gossip a bit
		# Maybe kill my children?
		# Maybe change state?
		pass

	def imprint(self):
		pass
	
	def spawn(self):
		pass
	
	def adopt(self, child):
		pass