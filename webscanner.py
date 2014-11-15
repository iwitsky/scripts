#!/usr/bin/env python
import sys, os
import urllib2
import cookielib
import re
import random
#from lxml import etree
import time
import getopt
#import errno
#import pdb
import urlparse

config = './config'
scanWait = 0
scanType = 0 # 0 list, 1 crawler
scanDepth = 3

user_agents = ['Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20130406 Firefox/23.0', \
	'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:18.0) Gecko/20100101 Firefox/18.0', \
	'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/533+ \
 	(KHTML, like Gecko) Element Browser 5.0', \
	'IBM WebExplorer /v0.94', 'Galaxy/1.0 [en] (Mac OS X 10.5.6; U; en)', \
	'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)', \
	'Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14', \
	'Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) \
	Version/6.0 Mobile/10A5355d Safari/8536.25', \
	'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) \
	Chrome/28.0.1468.0 Safari/537.36', \
	'Mozilla/5.0 (Windows NT 6.1; rv:31.0) Gecko/20100101 Firefox/31.0', 
	'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0; TheWorld)']

class Tester:
	def scan(self, url, scaner):
		pass

results = [
	"<b>Fatal error</b>:", 
	"Access Denied",
	"Microsoft OLE DB Provider", 
	"You have an error in your SQL syntax", 
	r'ERROR [0-9]+?:', 
];

class SimpleTester(Tester):
	def scan(self, url, scanner):
		# print url
		req = urllib2.Request(url)
		response = scanner.sendReq(req)
		if response == None:
			return
		respText = response.read()
		for p in results:
			if re.search(p , respText):
				scanner.report(url, respText[:1024])

class Scanner:
	_opener = None	
	_testers = ()
	
	def __init__(self):
		pass
	
	def report(self, url, msg):
		print '=' * 60
		print '[URL] ' + url
		print '[MESSAGE] ' + msg
		
	def sendReq(self, request, data = None, timeout = 15):
		index = random.randint(0, len(user_agents) - 1)
		user_agent = user_agents[index]
		request.add_header('User-agent', user_agent)
		try:
			response = self._opener.open(request, data = data, timeout = timeout)
		except Exception,e:
			#print e
			return None
		return response
	
	def getUrls(self):
		return ()

	def scanUrl(self, url):
		for tester in self._testers:
			tester.scan(url, self)
			if scanWait > 0:
				time.sleep(scanWait)
					
	def scan(self, saveCookie = False):
		#pdb.set_trace()
		# print '=' * 60
		if saveCookie:
			cookieJar = cookielib.CookieJar()
			self._opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar))
		else:
			self._opener = urllib2.build_opener()
		
		urls = self.getUrls()
		
		for url in urls:
			self.scanUrl(url)
		return True
	
class ListScanner(Scanner):
	
	def __init__(self, hostRoot, fileName, testers = (SimpleTester())):
		self._hostRoot = hostRoot
		self._fileName = fileName
		self._testers = testers
		
	def getUrls(self):
		for uri in open(self._fileName).readlines():
			if uri[0] != '/':
					uri = '/' + uri
			yield self._hostRoot + uri

class CrawlerScanner(Scanner):
	
	_linkList = set()
	
	_reexp = re.compile(r"""<a[^>]*?href\s*=\s*['"]?([^'"\s>]{1,500})['">\s]""", 
				re.I | re.M | re.S)

	def __init__(self, hostRoot, testers = [SimpleTester()]):
		self._hostRoot = hostRoot
		self._testers = testers

	def adjustUrl(self, refer, url):
		urlP = urlparse.urlparse(url)
		#print 'protocol:',urlP.scheme
		#print 'hostname:',urlP.hostname
		#print 'port:',urlP.port
		#print 'path:',urlP.path
		#print 'query:', urlP.query
		#print 'params', urlP.params
		# print "SCAN:" + url
		if urlP.hostname == None:
			url = urlparse.urljoin(refer, url)
		return url

	def scanPage(self, url, depth):
		depth += 1
		if depth < scanDepth:
			print url
			req = urllib2.Request(url)
			response = self.sendReq(req)
			if response == None:
				raise StopIteration()
			html = response.read()
			#tree = etree.HTML(html)
			#links = tree.xpath(r"/a//@href")			
			links = self._reexp.findall(html)
			#print len(links), links
			linkRec = set()
			for link in links:
				if re.search(r'^javascript:', link):
					continue
				link = self.adjustUrl(url, link)
				if not link in self._linkList:
					linkRec.add(link)
					print link
					yield link
			self._linkList.union(linkRec)
			for link in linkRec:				
				for link2 in self.scanPage(link, depth):
					yield link2

	def getUrls(self):
		for url in self.scanPage(self._hostRoot, 0):
			yield url	

#####################################################################
# vulnerability testers

# look like it's no effection now
class PhpArrayExposePathTester(Tester):
	def scan(self, url, scaner):
		urlP = urlparse.urlparse(url)
		if re.search(r'\.php$', urlP.path):
			url.replace('=', '[]=')
		req = urllib2.Request(url)
		response = scanner.sendReq(req)
		if response == None:
			return
		respText = response.read()
		for p in results:
			if re.search(p , respText):
				scanner.report(url, respText[:1024])


class SqlInjectionTester(Tester):
	def scan(self, url, scaner):
		pass

# .git | .svn | .file.swp(vim) | file.bak | dir.rar
class HiddenFileTester(Tester):
	def scan(self, url, scaner):
		pass

#####################################################################
if __name__ == "__main__":
	
	def usage():
		helpMsg = sys.argv[0] + """ [opt] host			
		
		-a show all exist page
		-e add custom error message
		-f config file. default ./config
		-h show help message
		-w wait time."""	
		print helpMsg 
		sys.exit(0)
	
	opts, args = getopt.getopt(sys.argv[1:], "ad:e:f:hpw:")
	#print opts
	#print args
	for op, value in opts:
		if op == '-a':
			checkAll = True
		elif op == '-d':
			scanDepth = int(value)
		elif op == "-e":
			results.append(value)	
		elif op == "-f":
			config = value
		elif op == "-h":
			usage()
		elif op == '-p':
			scanType = 1
		elif op == "-w":		
			scanWait = float(value)
	
	urlRoot = args[0]
	
	if config[-1] != '/':
		config += '/'
	
	if not re.search(r'^http://', urlRoot):
		urlRoot = 'http://' + urlRoot
	
	if scanType == 0:
		ls = os.listdir(config)
		for path in ls:
			if re.search('\.txt$', path):
				print 'List scanning: [', urlRoot, config + path, ']'
				scanner = ListScanner(urlRoot, config + path)
				scanner.scan()
	elif scanType == 1:
		scanner = CrawlerScanner(urlRoot, (HiddenFileTester(),))
		scanner.scan()
