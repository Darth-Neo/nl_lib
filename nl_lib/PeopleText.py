#!/usr/bin/env python
#
# Concept Class for NLP
#
__VERSION__ = 0.1
__author__ = u'morrj140'

from Logger import *
logger = setupLogging(__name__)
logger.setLevel(INFO)


def cleanPeople(name):
    r = u" "
    for c in name:
        if c.isalpha() or c == u',':
            r += c
            logger.debug(u"r = %s" % r)
        else:
            r += u" "
    return r


def splitPeople(people):
    logger.debug(u"SplitPeople: " + people)

    pl = people.split(u",")
    logger.debug(pl)

    peopleList = list()

    count = len(pl)
    logger.debug(u"Count = %s" % count)
     
    if count > 1:
        
        while count > 0:
            logger.debug(u"count: " + str(count))
            lfName = pl[count-2] + u"," + pl[count-1]
            lfName = cleanPeople(lfName)
            logger.debug(u"lfName=" + lfName)

            peopleList.append(lfName)
            count -= 2
    
    else:
        result = ''.join([i for i in people if i.isalpha()])
        if len(result) > 0:
            peopleList.append(result)
         
    return peopleList
