from nl_lib import Concepts
from nl_lib import Logger
logger = Logger.setupLogging(__name__)

from pytagcloud import create_tag_image, make_tags
from pytagcloud.lang.counter import get_tag_counts

#
# TopicCloud to create a Tag Cloud for Concepts
#
class TopicCloud(object):
    topicsConcepts = None
    homeDir = None
    imageFile = None

    def __init__(self, topicsConcepts, homeDir=None):
        self.topicsConcepts = topicsConcepts
        if homeDir == None:
            homeDir = os.getcwd() + os.sep
        self.homeDir = homeDir
        self.imageFile = self.homeDir + "topicCloud.png"
        
    def createCloudImage(self, size_x=1200, size_y=900, numWords=100):
        logger.info("Saving Tag Cloud - %s" % self.imageFile)
        logger.info("Starting with %d Topics" % len(self.topicsConcepts.getConcepts()))

        textConcepts = " "

        e = self.topicsConcepts.sortConcepts("Topic")
        
        if len(e) < numWords:
            limit = len(e)
        else:
            limit = numWords
            
        i = 0
        for i in range(limit):
            try:
                logger.info("%s" % e[i])
                textConcepts = textConcepts + (e[i][0] + " ") * (e[i][2] / 2)
            except:
                logger.error(str(sys.exc_info()[0]))
            i += 1

        # discard the first one
        tagCounts = get_tag_counts(textConcepts)[1:]
        tags = make_tags(tagCounts, maxsize=limit)

        create_tag_image(tags, self.imageFile, size=(size_x, size_y), fontname='Droid Sans')

