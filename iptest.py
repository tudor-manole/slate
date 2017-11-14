from py2neo import *
from py2neo.ogm import *
import csv
from netaddr import *
import random

graph = Graph(password="cashmoney")

class IP(GraphObject):
	number = Property()
	used = Property() # 0 for "free", 1 for "used"
	def __init__(self,num, used):
		self.number = num
		self.used = used

def populate():
	# ipspace = IPNetwork('10.6.0.0/16')
	ipspace = IPNetwork('192.168.1.0/24')
	counter = len(list(ipspace))
	for ip in ipspace:
		graph.push( IP( int(ip), random.randint(0,1) ) )
		# graph.push( IP( int(ip),0 ) )
		print(counter)
		counter -= 1

def occupy():
	ipspace = IPNetwork('192.168.1.0/24')
	subnets = list(ipspace.subnet(25))
	# print(type(subnets[0]))
	for i in subnets[0]:
		_ = graph.find_one(label="IP", property_key="number", property_value=int(i))
		_["used"] = 1
		graph.push(_)

	# print(list(subnets))

def cleanup():
	graph.delete_all()

def get_all_free():
	# ips_in_db = list( IPAddress(i["number"]) for i in graph.find(label="IP", property_key="used", property_value=0) )
	ips_in_db = cidr_merge( list( IPAddress(i["number"]) for i in graph.data("MATCH (i:IP {used:0}) RETURN i.number AS number") ) )
	ips_in_db.sort()
	print( [ str(n) for n in ips_in_db ] )

if __name__ == "__main__":
	# cleanup()
	# populate()
	# occupy()
	get_all_free()


# print(total_ipspace.prefixlen)

# sub1 = total_ipspace.subnet(32)
#
# print([s for s in sub1])

# for ip in total_ipspace.iter_hosts():
# 	# print(ip)
# 	str_ip = str(ip)
# 	if "255" in str_ip:
# 		print(str_ip)
# 	ipspace_container.append( IP(int(ip)) )
#
# for ip in ipspace_container:
# 	print( IPAddress( ip.number ))

# ip_list = []
# ip_list.append( int( IPAddress('192.168.1.0') ) )
# ip_list.append( int( IPAddress('192.168.1.1') ) )
# ip_list.append( int( IPAddress('192.168.1.2') ) )
# ip_list.append( int( IPAddress('192.168.1.3') ) )
# ip_list.append( int( IPAddress('192.168.1.200') ) )
#
# print(ip_list)
#
# # print(cidr_merge( [IPAddress(i) for i in ip_list] ))
# print( [IPAddress(i).bits() for i in ip_list] )


# ipspace_container = []
#
