#!/usr/bin/env python
#
# Concept Class for NLP
#
__VERSION__ = 0.1
__author__ = u'morrj140'

import sys
import os
import time
import Logger
logger = Logger.setupLogging(__name__)
    
from PatternSearch import PatternSearch


def crawlSearch(searchTerm):      

    # proxies = Proxies()
    # proxy = proxies.randomProxyHandler()

    if searchTerm is None:
        return

    logger.info(u"Searching for '%s'" % searchTerm)

    if os.name == u"nt":
        homeDir = u"crawlSearch_" + time.strftime(u"%Y%d%m_%H%M%S")
    else:
        homeDir = homeDir = u"/srv/www/htdocs"
    
    pc = PatternSearch(searchTerm, False, homeDir)  
    urlConcepts, wordConcepts = pc.patternSearch(12, 100)

    pc.exportGraph()
    
    pc.savePatternConcepts()

    #  concept.logConcepts()
    #  wordConcepts.logConcepts()
    
    
if __name__ == u'__main__':
    searchTerm = u"Walt Disney World Vacations"
    crawlSearch(searchTerm)
