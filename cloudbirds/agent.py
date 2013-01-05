# JMC License header here

"""
CloudBirds agent, runs on each VM

"""

from fysom import Fysom



class Agent:
	pass

class CloudBirdAgent(Agent):
	def __init__(self):
		self.fsm = Fysom({
		  'initial': 'hungry',
		  'events': [
		    {'name': 'eat',  'src': 'hungry',    'dst': 'satisfied'},
		    {'name': 'eat',  'src': 'satisfied', 'dst': 'full'},
		    {'name': 'eat',  'src': 'full',      'dst': 'sick'},
		    {'name': 'rest', 'src': ['hungry', 'satisfied', 'full', 'sick'],
		                                         'dst': 'hungry'}
		  ]
		})
		
		self.momma = None
	
	def mainloop(self):
		# Poll my current system state via snmp
		# Gossip a bit
		# Maybe kill my children?
		# Maybe change state?
		pass
