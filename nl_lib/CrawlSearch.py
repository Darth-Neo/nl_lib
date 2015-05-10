#!/usr/bin/env python
#
# Concept Class for NLP
#
import os
import time
from Logger import *
logger = setupLogging(__name__)
logger.setLevel(INFO)

from PatternSearch import PatternSearch

__VERSION__ = 0.1
__author__ = u'morrj140'


def crawlSearch(searchTerm):

    # proxies = Proxies()
    # proxy = proxies.randomProxyHandler()

    if searchTerm is None:
        return

    logger.info(u"Searching for '%s'" % searchTerm)

    if os.name == u"nt":
        homeDir = u"crawlSearch_" + time.strftime(u"%Y%d%m_%H%M%S")
    else:
        homeDir = u"/srv/www/htdocs"
    
    pc = PatternSearch(searchTerm, homeDir)
    # urlConcepts, wordConcepts =
    pc.patternSearch(12, 100)

    pc.exportGraph()
    
    pc.savePatternConcepts()

    #  concept.logConcepts()
    #  wordConcepts.logConcepts()

if __name__ == u'__main__':
    term = u"Walt Disney World Vacations"
    crawlSearch(term)
