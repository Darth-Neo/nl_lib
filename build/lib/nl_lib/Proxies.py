#!/usr/bin/env python
#
# Concept Class for NLP
#
__VERSION__ = 0.1
__author__ = 'morrj140'

import sys
import os
import csv
import urllib2
from random import randint

import Logger
logger = Logger.setupLogging(__name__)

class Proxies(object):  
    proxyFile = None
    proxyList = None
    
    def __init__(self, proxyFile='./proxies.csv'):
        self.proxyFile = proxyFile
        self.proxyList = list()
        
        with open(self.proxyFile, 'rb') as csvfile:
            # Skip first line
            csvfile.readline()
            siteRow = csv.reader(csvfile, delimiter=',', quotechar='"')
            n = 0
            for row in siteRow:
                n += 1
                logger.debug("%d - %s" % (n, row))
                m = 0
                plist = list()
                for col in row:
                    m += 1
                    if m in (2, 3):
                        logger.debug("   %d - %s" % (m, col))
                        plist.append(col)
                self.proxyList.append(plist)
        
        logger.debug("%s" % self.proxyList)
        
    def randomProxyHandler(self):
        logger.debug("%s" % self.proxyList)
        
        proxyIndex = randint(0,len(self.proxyList)-1) 
        
        proxy = self.proxyList[proxyIndex]
        
        p = 'http://' + proxy[0] + ':' + proxy[1]
        logger.info("Use Random Proxy %s" % (p))
        
        proxy_support = urllib2.ProxyHandler({"http" : p})
        opener = urllib2.build_opener(proxy_support)
        urllib2.install_opener(opener)

        return urllib2.ProxyHandler({"http" : p})
        
if __name__ == '__main__':   
    proxy = Proxies().randomProxyHandler()
    