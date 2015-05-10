#! env python
# -*- coding: ISO-8859-1 -*-

import sys

from nl_lib.Logger import *
logger = setupLogging(__name__)
logger.setLevel(INFO)

from test_Constants import *
import pytest

_author__ = 'james.morris'

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

    decode_type = "utf-8"
    encode_type = "ascii"
    # ea = 'replace'
    ea = 'ignore'

    logger.error("_________________________________________________________________________________")

    n += 1
    u = "café"
    uld = u.decode(decode_type, errors=ea)
    # print n, type(uld), uld
    logger.info("%d decode-%s %s.%s." % (n, decode_type, type(uld), uld))

    n += 1
    logger.info("%d Expect Failure", n)
    try:
        ule = u.encode(encode_type, errors=ea)
        # print n, type(ule), ule
        logger.info("%d encode-%s %s.%s." % (n, encode_type, type(ule), ule))
    except:
        logger.error("%d encode-%s %s" % (n, encode_type, sys.exc_info()[0]))

    logger.error("_________________________________________________________________________________")

    n += 1
    s = "Flügel"
    sl = s.decode(decode_type, errors=ea)
    # print n, type(sl), sl
    logger.info("%d decode-%s %s.%s" % (n, decode_type, type(sl), sl))

    n += 1
    logger.info("%d Expect Failure", n)
    try:
        s = "Flügel"
        sl = s.encode(encode_type, errors=ea)
        # print n, type(sl), sl
        logger.info("%d encode-%s %s.%s" % (n, encode_type, type(s), sl))
    except:
        logger.error("%d encode-%s %s" % (n, encode_type, sys.exc_info()[0]))

    logger.error("_________________________________________________________________________________")

    n += 1
    sl = s.decode(decode_type, errors=ea)
    # print n, type(sl), sl
    logger.info("%d decode-%s %s.%s." % (n, decode_type, type(sl), sl))

    n += 1
    logger.info("%d Expect Failure", n)
    try:
        sl = s.encode(encode_type, errors=ea)
        # print n, type(sl), sl
        logger.info("%d Encode-%s %s.%s." % (n, encode_type, type(sl), sl))
    except:
        logger.error("%d Encode-%s %s" % (n, encode_type, sys.exc_info()[0]))

    logger.error("_________________________________________________________________________________")

    n += 1
    p = "Hi!"
    pl = p.decode(decode_type, errors=ea)
    # print n, type(pl), pl
    logger.info("%d Decode-%s %s.%s\t%s.%s" % (n, decode_type, type(p), p, type(pl), pl))

    n += 1
    logger.info("%d Expect Failure", n)
    try:
        p = "Hi!"
        pl = p.encode(encode_type, errors=ea)
        # print n, type(pl), pl
        logger.info("%d Encode-%s %s.%s\t%s.%s" % (n, encode_type, type(p), p, type(pl), pl))
    except:
        logger.error("%d Encode-%s %s" % (n, encode_type, sys.exc_info()[0]))

    logger.error("_________________________________________________________________________________")

    n += 1
    us = u"Hi!"
    sl = us.decode(decode_type, errors=ea)
    # print n, sl
    logger.info("%d Decode-%s %s.%s" % (n, decode_type, type(sl), sl))

    n += 1
    logger.info("%d Expect Failure", n)
    try:
        us = u"Hi!"
        sl = us.encode(encode_type, errors=ea)
        #print n, sl
        logger.info("%d Encode-%s %s.%s" % (n, encode_type, type(sl), sl))

    except:
        logger.error("%d Encode-%s %s" % (n, encode_type, sys.exc_info()[0]))

    logger.error("_________________________________________________________________________________")

    n += 1
    q = u'Fl\xfcgel'
    # print n, q
    logger.info("%d Plain %s:%s" % (n, type(q), q))

    n += 1
    ql = q.encode(encode_type, errors=ea)
    # print n, ql
    logger.info("%d Encode-%s %s.%s" % (n, encode_type, type(q), ql))

if __name__ == u"__main__":
    test_encoding(cleandir)