#!/usr/bin/env python
#
# Concept Class for NLP
#
import csv
import urllib2
from random import randint
from Logger import *
logger = setupLogging(__name__)
logger.setLevel(DEBUG)

__VERSION__ = 0.1
__author__ = u'morrj140'


class Proxies(object):  
    proxyFile = None
    proxyList = None
    
    def __init__(self, proxyFile=u'./proxies.csv'):
        self.proxyFile = proxyFile
        self.proxyList = list()
        
        with open(self.proxyFile, u'rb') as csvfile:
            # Skip first line
            csvfile.readline()
            siteRow = csv.reader(csvfile, delimiter=u',', quotechar=u'"')
            n = 0
            for row in siteRow:
                n += 1
                logger.debug(u"%d - %s" % (n, row))
                m = 0
                plist = list()
                for col in row:
                    m += 1
                    if m in (2, 3):
                        logger.debug(u"   %d - %s" % (m, col))
                        plist.append(col)
                self.proxyList.append(plist)
        
        logger.debug(u"%s" % self.proxyList)
        
    def randomProxyHandler(self):
        logger.debugu(u"%s" % self.proxyList)
        
        proxyIndex = randint(0, len(self.proxyList)-1)
        
        proxy = self.proxyList[proxyIndex]
        
        p = u'http://' + proxy[0] + ':' + proxy[1]
        logger.info(u"Use Random Proxy %s" % (p))
        
        proxy_support = urllib2.ProxyHandler({u"http": p})
        opener = urllib2.build_opener(proxy_support)
        urllib2.install_opener(opener)

        return urllib2.ProxyHandler({u"http": p})
        
if __name__ == u'__main__':
    proxy = Proxies().randomProxyHandler()

