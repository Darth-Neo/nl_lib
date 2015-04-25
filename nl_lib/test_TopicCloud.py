# -*- coding: utf-8 -*-
# #!/usr/bin/python
#
# nl_lib Testing
# __author__ = 'morrj140'
import os
from nl_lib.Logger import *
logger = setupLogging(__name__)
logger.setLevel(INFO)

from nl_lib.TopicCloud import TopicCloud
from nl_lib.Concepts import Concepts

import pytest
from test_Constants import *

@pytest.fixture(scope=u"module")
def cleandir():
    cwd = os.getcwd()

    for lf in listFiles:
        ftr = testDir + lf

        if os.path.exists(ftr):
            logger.info(u"remove : %s" % ftr)
            os.remove(ftr)

@pytest.mark.TopicsMode
def test_CreateTopicCloud(cleandir):

    logger.debug(u"CWD : %s" % os.getcwd())

    conceptFile = u"./testdata/topicsDict.p"
    topic = u"Topic"

    imageFile = u"test.png"
    if os.path.exists(imageFile):
        logger.info(u"remove : %s" % imageFile)
        os.remove(imageFile)

    assert (os.path.isfile(imageFile) == False)

    concepts = Concepts.loadConcepts(conceptFile)

    tc = TopicCloud(concepts, imageFile=imageFile)

    tc.createTagCloud(topic)

    assert (os.path.isfile(imageFile)  == True)

if __name__ == u"__main__":
    test_CreateTopicCloud(cleandir)