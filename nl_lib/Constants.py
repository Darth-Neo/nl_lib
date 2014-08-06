import os

# Common Filenames
homeDir = os.getcwd() + os.sep

projectsFile   = homeDir + "projectsDict.p"
peopleFile     = homeDir + "peopleDict.p"
peopleFile     = homeDir + "peopleDict.p"
wordsFile      = homeDir + "wordsDict.p"
topicsFile     = homeDir + "topicsDict.p"
sentencesFile  = homeDir + "sentencesDict.p"
similarityFile = homeDir + "similarityDict.p" 
imageFile      = homeDir + "Topics_Cloud.bmp"
gmlFile        = homeDir + "Concepts.gml"
logFile        = homeDir + "nl_phase_log.txt"

# Used to add words to the stoplist
from nltk.corpus import stopwords
stop = stopwords.words('english')

# Add Stopwords
stop.append("of")
stop.append("the")
stop.append("not")
stop.append("to")
stop.append("or")
stop.append("this")
stop.append("all")
stop.append("with")
stop.append("we")
stop.append("in")
stop.append("This")
stop.append("The")
stop.append(",")
stop.append(".")
stop.append("..")
stop.append("...")
stop.append("...).")
stop.append("\")..")
stop.append(".")
stop.append(";")
stop.append("/")
stop.append(")")
stop.append("(")
stop.append("must")
stop.append("system")
