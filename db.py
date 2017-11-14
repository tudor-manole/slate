# from py2neo import Graph, Node, Relationship, ogm
from py2neo import *
from py2neo.ogm import *
import csv
from netaddr import *

graph = Graph(password="cashmoney")

class IPBlock(GraphObject):
	__primarykey__ = "block"
	block = Property()
	project	= RelatedFrom("Project", "RESERVES")
	def __init__(self,block, project):
		self.block = block
		p = Project.select(graph,project).first()
		self.project.add(p)

class Device(GraphObject):
	__primarykey__ = "hostname"
	hostname 	= Property()
	model 		= Property()
	serial 		= Property()
	mgmtip 		= Property()
	vendor 		= RelatedTo("Vendor", "SOLD_BY")
	rack 		= RelatedTo("Rack", "LOCATED_IN")
	labmodule 	= RelatedTo("LabModule", "USED_FOR")
	mrv 	 	= RelatedFrom("MRV", "CONTROLS")

	def __init__(self,hostname,model,serial,mgmtip,vendor,mrv,rack,labmodule):
		self.hostname 	= hostname
		self.model 		= model
		self.serial 	= serial
		self.mgmtip 	= mgmtip

		#####################################
		r = Rack.select(graph,rack).first()
		if r:
			self.rack.add(r)
		else:
			graph.push(Rack(position=rack))
			self.rack.add(Rack.select(graph,rack).first())
		#####################################
		l = LabModule.select(graph,labmodule).first()
		if l:
			self.labmodule.add(l)
		else:
			graph.push(LabModule(module=labmodule))
			self.labmodule.add(LabModule.select(graph,labmodule).first())
		#####################################
		v = Vendor.select(graph,vendor).first()
		if v:
			self.vendor.add(v)
		else:
			graph.push(Vendor(name=vendor))
			self.vendor.add(Vendor.select(graph,vendor).first())
		#####################################
		m = MRV.select(graph,mrv).first()
		if m:
			self.mrv.add(m)
		else:
			graph.push(MRV(hostname=mrv))
			self.mrv.add(MRV.select(graph,mrv).first())

	def serialize(dev):
		"""Takes in device GraphObject, returns dict"""
		return {
			"hostname": dev.hostname,
			"model": dev.model,
			"serial": dev.serial,
			"mgmtIP": dev.mgmtip,
			"vendor": list(dev.vendor).pop().name,
			"rack": list(dev.rack).pop().position,
			"labmodule": list(dev.labmodule).pop().module,
			"mrv": list(dev.mrv).pop().hostname
		}

class Vendor(GraphObject):
	__primarykey__ = "name"
	name = Property()
	def __init__(self,name):
		self.name = name

class Rack(GraphObject):
	__primarykey__ = "position"
	position = Property()
	def __init__(self, position):
		self.position = position

class LabModule(GraphObject):
	__primarykey__ = "module"
	module = Property()
	def __init__(self, module):
		self.module = module

class MRV(GraphObject):
	__primarykey__ = "hostname"
	hostname = Property()
	def __init__(self, hostname):
		self.hostname = hostname

class Project(GraphObject):
	__primarykey__ = "name"
	name = Property()
	devices = RelatedTo("Device", "USES")
	def __init__(self,name, devices=None):
		self.name = name
		if devices:
			for dname in devices:
				self.devices.add( Device.select(graph,dname).first() )

	def serialize(proj):
		"""Takes in project GraphObject, returns dict"""
		return {
			"name": proj.name,
			"devices": [Device.serialize(d) for d in proj.devices]
			# "devices": [d.hostname for d in proj.devices]#["test1", "test2"]# list(proj.devices)
		}


def seed():
	new_nodes = []
	with open('devices.csv') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			new_nodes.append(
				Device(
						hostname = row['hostname'].strip(),
						vendor=row['vendor'].strip(),
						model=row['model'].strip(),
						serial=row['serial'].strip(),
						rack=row['rack'].strip(),
						mgmtip=row['mgmtip'].strip(),
						mrv=row['mrv'].strip(),
						labmodule=row['module'].strip()
					))
	for n in new_nodes:
		# print(list(n.vendor))
		print(n.hostname)
		graph.push(n)

	# ipspace = IPNetwork('10.6.0.0/16')
	# for ip in ipspace:
	#


if __name__ == "__main__":
	IP.free_summary()

# print("running seed function")
# seed()

# g.push(Device(hostname = "Device2", vendor="Cisco",model="891",serial="abcd1234",mgmtip="1.2.3.4", mrv="MRV2"))

# v1 = Vendor()
# v1.name = "Cisco"

# g.push(v1)

# d1 = Device()
# d1.hostname = "Device1"
# d1.model="891"
# d1.serial="abcd1234"
# d1.mgmtip="1.2.3.4"
# d1.vendor.add(Vendor.select(g,"Cisco").first())

# g.push(d1)

# d1.hostname = "Hostname1"
# d1.vendor.add()

# nodes.append(Device(hostname = "Hostname1", vendor = "Cisco"))
# nodes.append(d1)

# print(list(Vendor.select(g)))

# print(nodes)
# print(type(d1.vendor))
# print(type(v1.name))

# ###############################
# # SQL/REST class definitions  #
# ###############################

# class Device(db.Entity):
# 	id 				= PrimaryKey(str, default=shortuuid.uuid)
# 	model 			= Required(str)
# 	serial 			= Required(str, unique=True)
# 	rack_position 	= Required(str)
# 	mgmt_ip 		= Required(int)
# 	hostname 		= Optional(str)
# 	mrv_info 		= Optional(str)
# 	lab_module		= Optional(int) # 0 for core, 1 for dev, 2 for testbed -- subject to change???!!!
# 	notes 			= Optional(str)
# 	###############################
# 	projects 		= Set("Project")
# 	reservations 	= Set("Reservation")

# class Project(db.Entity):
# 	id 				= PrimaryKey(str, default=shortuuid.uuid)
# 	###############################
# 	devices 		= Set("Device")
# 	reservations	= Set("Reservation")
# 	usergroups		= Set("UserGroup")

# class User(db.Entity):
# 	id 				= PrimaryKey(str, default=shortuuid.uuid)
# 	name 			= Required(str, unique=True)
# 	###############################
# 	reservations 	= Set("Reservation")
# 	usergroups 		= Set("UserGroup")

# class Reservation(db.Entity):
# 	id 			= PrimaryKey(str, default=shortuuid.uuid)
# 	notes		= Optional(str)
# 	###############################
# 	project 	= Required("Project")
# 	user 		= Required("User")
# 	devices 	= Set("Device")


# tx = g.begin()
# tx.run("CREATE (")
# tx.commit()

# result = g.data("""CREATE
# 				(device:Device { hostname:{hostname}, model:{model}, serial:{serial}, mgmtIP:{mgmtIP} })
# 				<-[:VENDOR_OF]-
# 				(:Vendor { name:{vendor} }),

# 				(device)
# 				-[:LIVES_ON]->
# 				(:Rack { position:{rack} }),

# 				(device)
# 				-[:PART_OF]->
# 				(:LabModule { module:{labModule} });
# 				""",
# 					hostname = "host1",
# 					model = "C6500",
# 					serial = "abcd1234",
# 					mgmtIP = "1.2.3.4",
# 					vendor = "Cisco",
# 					rack = "BR1-DA",
# 					labModule = "dev"
# 				)
