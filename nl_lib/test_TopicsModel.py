# -*- coding: utf-8 -*-

# #!/usr/bin/python
#
# nl_lib Testing
#
__author__ = u'morrj140'
__VERSION__ = u'0.2'

from Logger import *
logger = setupLogging(__name__)
logger.setLevel(INFO)

from test_Constants import *
from Constants import *
from Concepts import Concepts
from TopicsModel import TopicsModel

import pytest


@pytest.fixture(scope=u"module")
def cleandir():
    cwd = os.getcwd()

    for lf in listFiles:
        ftr = testDir + lf

        if os.path.exists(ftr):
            logger.info(u"remove : %s" % ftr)
            os.remove(ftr)

@pytest.mark.TopicsModel
def test_CreateTopics(cleandir):

    num_topics = 100
    num_words  = 100

    if __name__ == u"__main__":
        cleandir()

    assert (os.path.isdir(testDir) is True)
    tm = TopicsModel(directory=testDir)

    assert (os.path.isfile(conceptsTest) is True)
    concepts = Concepts.loadConcepts(conceptsTest)
    logger.info(u"Load Concepts from " + conceptsTest)

    logger.info(u"Load Documents from Concepts")
    documentsList, wordcount = tm.loadConceptsWords(concepts)

    logger.info(u"Read " + str(len(documentsList)) + u" Documents, with " + str(wordcount) + u" words.")

    if wordcount == 0:
        logger.error(u"No topics to use!")
        return None

    logger.info(u"Compute Topics")
    topics = tm.computeTopics(documentsList, nt=num_topics, nw=num_words)

    logger.info(u"Log Topics")
    tm.logTopics(topics)

    listTopics = [x[0].encode(u'ascii', errors=u"ignore").strip().replace(u"\"", u"") for x in topics]

    logger.info(u"Saving Topics")
    topicConcepts = tm.saveTopics(topics)

    for fl in listFiles:
        ftr = testDir + fl
        assert (os.path.isfile(ftr) is True)

    tm.logTopics(topics)

if __name__ == u"__main__":
    test_CreateTopics(cleandir)



