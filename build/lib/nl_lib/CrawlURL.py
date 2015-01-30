#!/usr/bin/env python
#
# Concept Class for NLP
#
__VERSION__ = 0.1
__author__ = 'morrj140'


import re
import sys
import os
import time
import math
import urllib2
import urlparse

import Logger
logger = Logger.setupLogging(__name__)

from cgi import escape
from traceback import format_exc
from Queue import Queue, Empty as QueueEmpty
from BeautifulSoup import BeautifulSoup

from PatternSearch import PatternSearch
from Proxies import Proxies

AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:20.0) Gecko/20100101 Firefox/20.0"

homeDir = os.getcwd()

class Crawler(object):
    
    def __init__(self, rootURL, depth, locked=True):
        self.root = rootURL
        self.depth = depth
        self.locked = locked
        self.host = urlparse.urlparse(rootURL)[1]
        self.urls = []
        self.links = 0
        self.followed = 0

    def crawl(self, patternSearch):
        page = Fetcher(self.root)
        page.fetch(patternSearch)
        
        qP = Queue()
        qC = Queue()
        
        for url in page.urls:
            qP.put(url)
            logger.info("root URL : %s" % url)
            
        followed = [self.root]

        n = 0
        while n < self.depth:
            
            time.sleep(1)
            
            if qP.qsize() == 0:
                qP = qC
                qC = Queue()
                n += 1
                logger.info("Queue Empty for Depth : %s" % n)
            else:
                logger.info("Parent Queue : %d, Child Queue : %d, Depth : %d" % (qP.qsize(),qC.qsize(), n))    
                lwc, luc = patternSearch.loglengthOfConcepts()
                
                #if lwc > 500:
                #    break
            
            url = qP.get()    
            host = urlparse.urlparse(url)[1]
            
            logger.debug("%s - host: %s" % (self.host, host))
            logger.debug("re %s" % re.match(".*%s" % self.host, host))
            
            # Only go after links on this site
            if url not in followed and re.match(".*%s" % self.host, host) is not None: 
                        
                try:
                    logger.info("+++Fetching URL - %s" % url)         
                    
                    followed.append(url)
                    self.followed += 1
                    
                    page = Fetcher(url)
                    page.fetch(patternSearch)
                    
                    # enumerate links found on page
                    for i, url in enumerate(page):
                        logger.debug("------Following URL - %s" % url)
                        
                        # prevent same link on page being followed multiple times
                        if url not in self.urls:
                            self.links += 1
                            qC.put(url)
                            self.urls.append(url)
                        else:
                            logger.debug("------Skipping URL - %s" % url)

                except Exception, e:
                    logger.error( "ERROR: Can't process url '%s' (%s)" % (url, e))
                    logger.error( format_exc())
            else:
                logger.debug("Link not from - %s" % url)

class Fetcher(object):

    def __init__(self, url):
        self.url = url
        self.urls = []
        
    def __getitem__(self, x):
        return self.urls[x]

    def _addHeaders(self, request):
        request.add_header("User-Agent", AGENT)

    def open(self):
        logger.debug("Open : %s" % self.url)
        url = self.url
        try:            
            request = urllib2.Request(url)
            handle = None
        except IOError:
            return None
        return (request)

    def fetch(self, patternSearch):
        
        request = self.open()
        
        logger.info("Fetch : %s" % self.url)
        
        self._addHeaders(request)
        
        try:
            content = unicode(urllib2.urlopen(request).read(), "utf-8",
                    errors="replace")
                            
            patternSearch.htmlSearch(content, self.url)
            
            soup = BeautifulSoup(content)
            tags = soup('a')
            
        except urllib2.HTTPError, error:
            if error.code == 404:
                logger.error("ERROR: %s -> %s" % (error, error.url))
            else:
                logger.error("ERROR: %s" % error)
            tags = []
            
        except urllib2.URLError, error:
            logger.error("ERROR: %s" % error)
            tags = []
            
        except Exception, error:
            logger.error("Unknown error %s" % error)
            tags = []
        
        for tag in tags:
            href = tag.get("href")
            if href is not None:
                url = urlparse.urljoin(self.url, escape(href))
                if url not in self:
                    self.urls.append(url)


def crawlURL(listURL, single=True, web=False, depth=0):
    singleFile = "crawlURL_" + time.strftime("%Y%d%m_%H%M%S")
    
    crawler = None
    patternSearch = None
    
    for lu in listURL: 
        logger.info( "Crawling %s :" % lu)
        
        if not web:
            if single:
                homeDir = os.getcwd() + os.sep + singleFile
            else:
                host = urlparse.urlparse(lu)[1]
                homeDir = '/home/james.morris/crawler/%s' % host
        else:
            homeDir="/srv/www/htdocs"
        
        if not os.path.exists(homeDir):
            os.makedirs(homeDir)
                
        if crawler == None:    
            patternSearch = PatternSearch(lu, False, homeDir)
            crawler = Crawler(lu, depth)
        
        crawler.crawl(patternSearch)
        
        if single:
            patternSearch.exportGraph()
            patternSearch.savePatternConcepts()
            crawler = None
            patternSearch = None
       
    if not single:
        patternSearch.exportGraph()
        patternSearch.savePatternConcepts()

if __name__ == "__main__":
    
    #proxies = Proxies()
    #proxy = proxies.randomProxyHandler()
    
    listURL = list()
    
    listURL.append("http://www.foxnews.com")
    
    single=True
    web=False
    depth=0
     
    crawlURL(listURL, single, web, depth)
    
    
    
        
    
    
    
    
