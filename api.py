#!/usr/bin/python3
import hug # REST API framework
from falcon import HTTP_400, HTTP_409, HTTP_404, HTTP_200, HTTP_201, HTTP_405
import json
# from hug_middleware_cors import CORSMiddleware
from datamodel import *

#####################
# Hug Handler class #
#####################

@hug.object.urls('/devices', requires=())
class DeviceHandler(object):

	# CREATE
	@hug.object.post('{hostname}')
	def create(self, body):
		pass
	# def __init__(self,hostname,model,serial,mgmtip,vendor,mrv,rack,labmodule):


	# READ

	@hug.object.get()
	def get_all(self):
		"""Return all devices"""
		return [Device.serialize(d) for d in Device.select(graph)]

	@hug.object.get('{hostname}')
	def get_one(self, hostname, response):
		"""Return one device by hostname"""
		dev = graph.data("MATCH (d:Device) WHERE d.hostname = {hostname} RETURN d", hostname=hostname)
		if dev:
			return Device.serialize(Device.select(graph, hostname).first())
		else:
			response.status = HTTP_404

	# UPDATE

	@hug.object.put('{hostname}')
	def update_one(self,hostname,body, response):
		if body:
			dev = graph.data("MATCH (d:Device) WHERE d.hostname = {hostname} RETURN d", hostname=hostname)
			if dev:
				print(body)
				graph.push( Device(hostname=body['hostname'],model=body['model'],serial=body['serial'],mgmtip=body['mgmtIP'],
				vendor=body['vendor'],mrv=body['mrv'],rack=body['rack'],labmodule=body['labmodule']) ) # will update or create the project node
			else:
				response.status = HTTP_400 # bad request
		else:
			response.status = HTTP_400 # bad request

	# DELETE

	@hug.object.delete('{hostname}')
	def delete(self, hostname, response):
		# graph.delete(Device.select(graph, hostname).first())
		if graph.data("MATCH (d:Device) WHERE d.hostname = {hostname} RETURN d", hostname=hostname):
			graph.data("MATCH (d:Device) WHERE d.hostname = {hostname} DETACH DELETE d", hostname=hostname)
			response.status = HTTP_200
		else:
			response.status = HTTP_404

@hug.object.urls('/projects', requires=())
class ProjectHandler(object):

	# CREATE

	@hug.object.post('{name}')
	def create_one(self, name, body, response):
		if body:
			devices = body.strip().split(",")
			for d in devices:
				d = d.strip()
			graph.push( Project(name,devices) )
		else:
			graph.push( Project(name) )

	@hug.object.post('{name}/{devname}')
	def add_project_device(self, name, devname, response):
		proj = Project.select(graph, name).first()
		dev = Device.select(graph, devname).first()
		if proj:
			if dev:
				if dev in proj.devices:
					response.status = HTTP_409
				else:
					print("add dev {} to project {}'s devices: {}".format(dev.hostname, proj.name, list(proj.devices)))
					proj.devices.add(dev)
					graph.push( proj )
			else:
				response.status = HTTP_404
		else:
			response.status = HTTP_404

	# READ

	@hug.object.get()
	def get_all(self):
		"""Return all projects"""
		return [Project.serialize(p) for p in Project.select(graph)]

	@hug.object.get('{name}')
	def get_one(self, name, response):
		"""Return one project by name"""
		proj = Project.select(graph, name).first()
		if proj:
			return Project.serialize(proj)
		else:
			response.status = HTTP_404

	# UPDATE

	@hug.object.put('{name}')
	def update_one(self, name, body, response):
		if body:
			proj = Project(body["name"], body["devices"])
			print(proj.devices)
			# graph.push( proj ) # will update or create the project node
		else:
			response.status = HTTP_400 # bad request

	# DELETE

	@hug.object.delete('{name}')
	def delete_one(self, name, response):
		"""Delete one project by name"""
		proj = Project.select(graph, name).first()
		if proj:
			graph.delete(proj)
			response.status = HTTP_200
		else:
			response.status = HTTP_404

	@hug.object.delete('{name}/{devname}')
	def delete_project_device(self, name, devname, response):
		proj = Project.select(graph, name).first()
		dev = Device.select(graph, devname).first()
		if proj:
			if dev:
				if dev in proj.devices:
					print("remove dev {} from project {}'s devices: {}".format(dev.hostname, proj.name, list(proj.devices)))
					proj.devices.remove(dev)
					# print("proj.devices after remove: ",list(proj.devices))
					graph.push( proj )
			else:
				response.status = HTTP_404
		else:
			response.status = HTTP_404


# class IPBlock(GraphObject):
# 	__primarykey__ = "block"
# 	block = Property()
# 	project	= RelatedFrom("Project", "RESERVES")
# 	def __init__(self,block, project):
# 		self.block = block
# 		p = Project.select(graph,project).first()
# 		self.project.add(p)

@hug.object.urls('/ipblocks', requires=())
class IPHandler(object):
	ipspace = IPSet(IPNetwork("10.6.0.0/16"))
	# CREATE (reserve a block)
	@hug.object.post('reserve')
	def reserve_block(self, body, response):
		used_blocks = cidr_merge( list( IPNetwork(i["block"]) for i in graph.data("MATCH (b:IPBlock) RETURN b.block as block") ) )
		free_blocks_in_db = IPHandler.ipspace - IPSet(used_blocks)
		requested_block = IPSet(IPNetwork(body["block"]))
		if requested_block - free_blocks_in_db:
			response.status = HTTP_400
		else:
			graph.push( IPBlock( block=str(IPNetwork(body["block"])), project=body["project"] ) )

	# READ

	@hug.object.get('used')
	def get_all_used(self):
		used_blocks = cidr_merge( list( IPNetwork(i["block"]) for i in graph.data("MATCH (b:IPBlock) RETURN b.block as block") ) )
		return [ str(n) for n in used_blocks ]


	@hug.object.get('free')
	def get_all_free(self):
		used_blocks = cidr_merge( list( IPNetwork(i["block"]) for i in graph.data("MATCH (b:IPBlock) RETURN b.block as block") ) )
		free_blocks_in_db = cidr_merge(IPHandler.ipspace - IPSet(used_blocks))
		# free_blocks_in_db = cidr_merge( list( IPAddress(i["number"]) for i in graph.data("MATCH (b:IPBlock) WHERE NOT (:Project) -[:RESERVES]-> (b) RETURN b.block") ) )
		return [ str(n) for n in free_blocks_in_db ]


	# UPDATE

	# @hug.object.put('{number}')
	# def update_one(self, number, body, response):
	# 	if body:
	# 		ip = IP(body["number"], body["devices"])
	# 		graph.push( proj ) # will update or create the project node
	# 	else:
	# 		response.status = HTTP_400 # bad request

# GOOD UPDATE CODE:
		# _ = graph.find_one(label="IP", property_key="number", property_value=int(i))
		# _["used"] = 1
		# graph.push(_)



#############################################################

# graph.data("MATCH (a:Person) RETURN a.name, a.born LIMIT 4")
# [{'a.born': 1964, 'a.name': 'Keanu Reeves'},
#  {'a.born': 1967, 'a.name': 'Carrie-Anne Moss'},
#  {'a.born': 1961, 'a.name': 'Laurence Fishburne'},
#  {'a.born': 1960, 'a.name': 'Hugo Weaving'}]

# @hug.object.urls('/projects', requires=())
# class ProjectHandler(object):
#
# 	@hug.object.post('list')
# 	def list(self, body):
# 		pass
#
# 	@hug.object.post('create')
# 	def create(self, body):
# 		pass
#
# 	@hug.object.post('update')
# 	def update_one(self,body):
# 		pass
#
# 	@hug.object.post('delete')
# 	def delete(self,body):
# 		pass

api = hug.API(__name__)
# api.http.add_middleware(CORSMiddleware(api))
api.http.add_middleware(hug.middleware.CORSMiddleware(api))
