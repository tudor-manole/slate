# from py2neo import Graph, Node, Relationship, ogm
from py2neo import *
from py2neo.ogm import *
import csv

g = Graph(password="cashmoney")

class Person(GraphObject):
	__primarykey__ = "name"
	def __init__(self,name,house):
		self.name 	= name
		#####################################
		h = House.select(g,house).first()
		if h:
			print("House",house,"found!")
			self.house.add(h)
		else:
			print("House",house,"NOT found, has been created.")
			g.push(House(name=house))
			self.house.add(House.select(g,house).first())
	name 	= Property()
	house = RelatedTo("House", "LIVES_IN")

class House(GraphObject):
	__primarykey__ = "name"
	def __init__(self,name):
		self.name = name
	name = Property()

g.push(Person("Bob","WindsorHouse"))
