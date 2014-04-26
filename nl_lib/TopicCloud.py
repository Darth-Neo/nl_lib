from nl_lib import Concepts
from nl_lib import Logger
logger = Logger.setupLogging(__name__)

from pytagcloud import create_tag_image, make_tags
#from pytagcloud.lang.counter import get_tag_counts
from operator import itemgetter

#
# TopicCloud to create a Tag Cloud for Concepts
#
class TopicCloud(object):
    topicsConcepts = None
    homeDir = None
    imageFile = None

    def __init__(self, topicsConcepts, homeDir=None):
        self.topicsConcepts = topicsConcepts

        for topic in self.topicsConcepts.getConcepts().values():
            if topic.count == 0:
                logger.info("deleted %s from topics" % topic.name)
                del self.topicsConcepts.getConcepts()[topic.name]
    
        if homeDir == None:
            homeDir = os.getcwd() + os.sep
            
        self.homeDir = homeDir
        self.imageFile = self.homeDir + "topicCloud.png"

    def _getDictConcepts(self, concepts, typeName, dictConcepts):
        if len(concepts.getConcepts()) == 0:
            return None

        for p in concepts.getConcepts().values():
            if p.typeName == typeName:
                if dictConcepts.has_key(p.name):
                    dictConcepts[p.name] = dictConcepts[p.name] + p.count
                else:
                    dictConcepts[p.name] = p.count

            self._getDictConcepts(p, typeName, dictConcepts)  
    
    def createCloudImage(self, typeName="Topic", size_x=1200, size_y=900, numWords=100, scale = 1.0):
        logger.info("Saving Tag Cloud - %s" % self.imageFile)
        logger.info("Starting with %d Topics" % len(self.topicsConcepts.getConcepts()))

        dictConcepts = dict()
        self._getDictConcepts(self.topicsConcepts, typeName, dictConcepts)

        for d in dictConcepts.keys():
            dictConcepts[d] = dictConcepts[d] + dictConcepts[d] * scale
        
        e = sorted(dictConcepts.iteritems(), key=itemgetter(1), reverse=True)
        logger.debug("e = %s" % e)

        e = e[1:numWords]

        tags = make_tags(e, maxsize=numWords)

        create_tag_image(tags, self.imageFile, size=(size_x, size_y), fontname='Droid Sans')

