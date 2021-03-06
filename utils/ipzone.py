import socket
import struct

def getInetAddr(str):
	return struct.unpack('!I', socket.inet_aton(str))[0]

def isSubnet(netaddr, netaddrlen, ipaddr):
	#print "%x, %d, %x" % (netaddr, netaddrlen, ipaddr)
	netmask = (0xffffffff << (32 - netaddrlen)) & 0xffffffff
	return (netaddr & netmask) == (ipaddr & netmask)

PRIVATE_IP_ZONE = ( (getInetAddr('10.0.0.0'), 8), (getInetAddr('192.168.0.0'), 16), 
		(getInetAddr('172.16.0.0'), 12) )

def isPrivateZone(ipaddr):
	ipaddr = getInetAddr(ipaddr)
	for subnet in PRIVATE_IP_ZONE:
		if isSubnet(subnet[0], subnet[1], ipaddr):
			return True
	return False

chinaIpZone = []
def loadChinaIpZone(path): # data/chinaip.txt
	for line in open(path).readlines():
		subnet, netaddrlen = line.split('/')
		#print subnet, netaddrlen
		chinaIpZone.append( ( getInetAddr(subnet), int(netaddrlen) ) )
	# print len(chinaIpZone)

def isChinaZone(ipaddr):
	if isPrivateZone(ipaddr): # skip top three line in chinaip.txt
		return False
	ipaddr = getInetAddr(ipaddr)
	for subnet in chinaIpZone:
		if isSubnet(subnet[0], subnet[1], ipaddr):
			return True
	return False

if __name__ == '__main__':
	loadChinaIpZone('../data/chinaip.txt')
	import sys
	print isChinaZone(socket.gethostbyname(sys.argv[1]))

	"""
	print isPrivateZone('192.168.0.1')
	print isPrivateZone('202.17.19.1')
	print isPrivateZone('10.253.89.1')

	print isChinaZone('178.63.204.101')
	print isChinaZone('42.62.43.22')
	print isChinaZone('61.164.118.174')
	print isChinaZone('115.239.211.110')
	"""
