#!/usr/bin/env python
#
# Concept Class for NLP
#
__VERSION__ = 0.1
__author__ = 'morrj140'

import os

# Common Filenames
homeDir = os.getcwd() + os.sep

projectsFile   = homeDir + u"projectsDict.p"
peopleFile     = homeDir + u"peopleDict.p"
peopleFile     = homeDir + u"peopleDict.p"
wordsFile      = homeDir + u"wordsDict.p"
topicsFile     = homeDir + u"topicsDict.p"
sentencesFile  = homeDir + u"sentencesDict.p"
similarityFile = homeDir + u"similarityDict.p"
imageFile      = homeDir + u"Topics_Cloud.bmp"
gmlFile        = homeDir + u"Concepts.gml"
logFile        = homeDir + u"nl_phase_log.txt"

# Used to add words to the stoplist
from nltk.corpus import stopwords
stop = stopwords.words(u'english')

# Add Stopwords
stop.append(u"of")
stop.append(u"the")
stop.append(u"not")
stop.append(u"to")
stop.append(u"or")
stop.append(u"this")
stop.append(u"all")
stop.append(u"on")
stop.append(u"with")
stop.append(u"we")
stop.append(u"in")
stop.append(u"This")
stop.append(u"The")
stop.append(u",")
stop.append(u".")
stop.append(u"..")
stop.append(u"...")
stop.append(u"...).")
stop.append(u"\")..")
stop.append(u".")
stop.append(u";")
stop.append(u"/")
stop.append(u")")
stop.append(u"(")
stop.append(u"must")
stop.append(u"system")
stop.append(u"This")
stop.append(u"The")
stop.append(u",")
stop.append(u"must")
stop.append(u"and")
stop.append(u"of")
stop.append(u"by")