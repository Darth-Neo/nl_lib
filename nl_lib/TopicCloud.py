#!/usr/bin/env python
#
# Concept Class for NLP
#
__VERSION__ = 0.2
__author__ = u'morrj140'

import os
from operator import itemgetter

from nl_lib.Logger import *
logger = setupLogging(__name__)
logger.setLevel(INFO)

from nl_lib.Concepts import Concepts
from nltk.stem import PorterStemmer, WordNetLemmatizer

import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS

#
# TopicCloud to create a Tag Cloud for Concepts
#
class TopicCloud(object):
    topicsConcepts = None
    homeDir = None
    imageFile = None
    lemmatizer = None

    def __init__(self, topicsConcepts, homeDir=None, font_path=None, imageFile=None):
        self.topicsConcepts = topicsConcepts

        if homeDir == None:
            self.homeDir = os.getcwd() + os.sep
            
        if imageFile == None:
            self.imageFile = self.homeDir + u"topicCloud.png"

        self.lemmatizer = WordNetLemmatizer()

        if font_path == None:
            self.font_path = self.homeDir + u'DroidSans.ttf'
        else:
            self.font_path = font_path

    def _getDictConcepts(self, concepts, typeName, dictConcepts=None):
        if dictConcepts == None:
            dictConcepts = dict()

        if len(concepts.getConcepts()) == 0:
            return None

        for p in concepts.getConcepts().values():
            if p.typeName == typeName:
                if dictConcepts.has_key(p.name):
                    dictConcepts[p.name] = dictConcepts[p.name] + 1
                else:
                    w = self.getLemma(p.name)
                    if p.count == 0:
                        dictConcepts[w] = 1
                    else:
                        dictConcepts[w] = p.count

            self._getDictConcepts(p, typeName, dictConcepts)

        return dictConcepts

    def getLemma(self, name):

        name.replace(".", "")

        sn = ""

        for x in name.split(" "):
            lemmaWord = self.lemmatizer.lemmatize(x.lower())
            sn = sn + " " + lemmaWord

        logger.debug(u"New Lemma : %s" % sn)

        return sn

    def createTagCloud(self, typeName=u"Topic", size_x=1800, size_y=1400, numWords=100, scale = 1.0):

        logger.info(u"Starting with %d Topics" % len(self.topicsConcepts.getConcepts()))

        dictConcepts = self._getDictConcepts(self.topicsConcepts, typeName)

        if len(dictConcepts) == 0:
            return None

        for d in dictConcepts.keys():
            dictConcepts[d] = dictConcepts[d] + dictConcepts[d] * scale

        e = sorted(dictConcepts.iteritems(), key=itemgetter(1), reverse=True)
        logger.debug(u"e = %s" % e)

        tags = " ".join([x * int(y) for x, y in e])

        wordcloud = WordCloud(
              font_path=self.font_path,
              stopwords=STOPWORDS,
              background_color=u'white',
              width=size_x,
              height=size_y
             ).generate(tags)

        plt.imshow(wordcloud)
        plt.axis(u'off')
        plt.savefig(self.imageFile, dpi=300)
        #plt.show()

        logger.info(u"Saving Tag Cloud - %s" % self.imageFile)

if __name__ == u"__main__":
    logger.debug(u"CWD : %s" % os.getcwd())

    conceptFile = u"./test/topicsDict.p"
    topic = u"Topic"

    concepts = Concepts.loadConcepts(conceptFile)

    tc = TopicCloud(concepts)

    tc.createTagCloud(topic)