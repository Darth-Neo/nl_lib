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
