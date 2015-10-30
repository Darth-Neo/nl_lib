#! env python
# -*- coding: utf-8 -*-

import sys

from Logger import *
logger = setupLogging(__name__)
logger.setLevel(INFO)
from Concepts import Concepts
from test_Constants import *
import pytest

_author__ = u'james.morris'

@pytest.fixture(scope=u"module")
def cleandir():
    cwd = os.getcwd()

    listFiles = list()
    listFiles.append(exportFileTest)

    for lf in listFiles:
        ftr = cwd + os.sep + u"test" + os.sep + lf

        if os.path.exists(ftr):
            logger.info(u"remove : %s" % ftr)
            os.remove(ftr)


@pytest.mark.Encoding
def test_encoding(cleandir):
    n = 0
    s = 'Ivan Krsti\xc4\x87'

    logger.info(u"_________________________________________________________________________________")

    n += 1
    u = u"café"
    uld = Concepts._convertConcepts(u)
    logger.info(u"%d-%s.%s." % (n,  type(uld), uld))
    logger.info(u"_________________________________________________________________________________")

    n += 1
    s = u"Flügel"
    sl = Concepts._convertConcepts(s)
    logger.info(u"%d-%s.%s" % (n, type(sl), sl))

    logger.info(u"_________________________________________________________________________________")

    n += 1
    p = u"Hi!"
    pl = Concepts._convertConcepts(p)
    logger.info(u"%d-%s.%s\t%s.%s" % (n, type(p), p, type(pl), pl))

    logger.info(u"________________________________________________________________________________")

    n += 1
    q = u'Fl\xfcgel' # Flügel
    logger.info(u"%d-%s:%s" % (n, type(q), q))

    # go from q = u'Fl\xfcgel' to Flügel, then Fl��gel

if __name__ == u"__main__":
    test_encoding(cleandir)
