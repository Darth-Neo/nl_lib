#!/usr/bin/env python
#
# Concept Class for NLP
#
__VERSION__ = 0.1
__author__ = 'morrj140'

import sys
import os
import time
import Logger
logger = Logger.setupLogging(__name__)
    
from PatternSearch import PatternSearch
from Proxies import Proxies

#
# main
#
def crawlSearch(searchTerm):      

    #proxies = Proxies()
    #proxy = proxies.randomProxyHandler()

    if searchTerm == None:
        return

    logger.info("Searching for '%s'" % searchTerm)

    if os.name == "nt":
        homeDir = "crawlSearch_" + time.strftime("%Y%d%m_%H%M%S")
    else:
        homeDir = homeDir="/srv/www/htdocs"
    
    pc = PatternSearch(searchTerm, False, homeDir)  
    urlConcepts, wordConcepts = pc.patternSearch(12, 100)

    pc.exportGraph()
    
    pc.savePatternConcepts()

    #concept.logConcepts()
    #wordConcepts.logConcepts()
    
    
if __name__ == '__main__':
    searchTerm = "Walt Disney World Vacations"
    crawlSearch(searchTerm)
