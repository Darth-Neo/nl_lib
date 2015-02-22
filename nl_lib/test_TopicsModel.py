# -*- coding: utf-8 -*-

# #!/usr/bin/python
#
# nl_lib Testing
#
__author__ = 'morrj140'
__VERSION__ = '0.2'

from nl_lib.Logger import *
logger = setupLogging(__name__)
logger.setLevel(INFO)

from Constants import *
from Concepts import Concepts
from TopicsModel import TopicsModel

import pytest
from test_Constants import *

@pytest.fixture(scope="module")
def cleandir():
    cwd = os.getcwd()

    for lf in listFiles:
        ftr = testDir + lf

        if os.path.exists(ftr):
            logger.info("remove : %s" % ftr)
            os.remove(ftr)

@pytest.mark.TopicsMode
def test_CreateTopics(cleandir):

    num_topics = 100
    num_words  = 100

    if __name__ == "__main__":
        cleandir()

    assert (os.path.isdir(testDir) == True)
    tm = TopicsModel(directory=testDir)

    assert (os.path.isfile(conceptsTest)  == True)
    concepts = Concepts.loadConcepts(conceptsTest)
    logger.info("Load Concepts from " + conceptsTest)

    logger.info("Load Documents from Concepts")
    documentsList, wordcount = tm.loadConceptsWords(concepts)

    logger.info("Read " + str(len(documentsList)) + " Documents, with " + str(wordcount) + " words.")

    if wordcount == 0:
        logger.error("No topics to use!")
        return None

    logger.info("Compute Topics")
    topics = tm.computeTopics(documentsList, nt=num_topics, nw=num_words)

    logger.info("Log Topics")
    tm.logTopics(topics)

    listTopics = [x[0].encode('ascii', errors="ignore").strip().replace("\"", "") for x in topics]

    logger.info("Saving Topics")
    topicConcepts = tm.saveTopics(topics)

    for fl in listFiles:
        ftr = testDir + fl
        assert (os.path.isfile(ftr) == True)

    tm.logTopics(topics)

if __name__ == "__main__":
    test_CreateTopics(cleandir)



