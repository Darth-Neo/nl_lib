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

import pytest
from test_Constants import *

@pytest.fixture(scope="module")
def cleandir():
    cwd = os.getcwd()

    listFiles = list()
    listFiles.append(exportFileTest)

    for lf in listFiles:
        ftr = cwd + os.sep + "test" + os.sep + lf

        if os.path.exists(ftr):
            logger.info("remove : %s" % ftr)
            os.remove(ftr)

def setup():
    key = "key"
    value = "value"

    c = Concepts(key, value)
    assert (c.name  == key)
    assert (c.typeName  == value)

    d = c.addConceptKeyType(key, value)
    assert (c.count  == 1)
    assert (d.name  == key)
    assert (d.typeName  == value)

    e = d.addConceptKeyType(key, value)
    assert (d.count  == 1)
    assert (e.name  == key)
    assert (e.typeName  == value)

    e = d.addConceptKeyType(key, value)
    assert (e.count == 0)

    return key, value, c

@pytest.mark.Concepts
def test_Concepts(cleandir):

    key, value, c = setup()

    logger.info("Using : %s" % exportFileTest)

    Concepts.saveConcepts(c, exportFileTest)

    assert (os.path.isfile(exportFileTest)  == True)

@pytest.mark.Concepts
def test_Concepts_Props(cleandir):
    key, value, c = setup()

    d = dict()
    d[key] = value

    c.setProperties(d)

    nd = c.getProperties()

    assert(nd[key] == value)

@pytest.mark.Concepts
def test_concepts_dict(cleandir):
    key, value, c = setup()

    d = c.dictChildrenType(value)

    assert(d != None)
    assert(len(d) > 0)
    assert(len(d) == 1)

@pytest.mark.Concepts
def test_sorted_concepts(cleandir):
    key, value, c = setup()

    sc = c.sortConcepts(value)

    assert(sc != None)
    assert(isinstance(sc, list))
    assert(len(sc) > 0)
    assert(len(sc) == 1)

@pytest.mark.Concepts
def test_listCSVConcepts(cleandir):
    key, value, c = setup()

    sc = c.listCSVConcepts()

    assert(sc != None)
    assert(isinstance(sc, list))
    assert(len(sc) > 0)
    assert(len(sc) == 3)

@pytest.mark.Concepts
def test_addConcept(cleandir):
    key, value, c = setup()

    dkey = "nd"
    dvalue = "ndt"

    d = Concepts(dkey, dvalue)

    c.addConcept(d)
    cd = c.getConcepts()
    ck = c.getConcepts().keys()
    cv = c.getConcepts().values()

    assert(cv != None)
    assert(isinstance(cv, list))
    assert(d.name == cd[dkey].name)
    assert(d.count == cd[dkey].count)

@pytest.mark.Concepts
def test_addListConcepts(cleandir):

    key, value, c = setup()

    listConcepts = list()
    listConcepts.append(Concepts("a", "b"))
    listConcepts.append(Concepts("c", "d"))
    listConcepts.append(Concepts("e", "f"))

    c.addListConcepts(listConcepts)

    cd = c.getConcepts()

    assert(cd != None)
    assert(len(cd) > 0)
    assert(len(cd) == 4)

@pytest.mark.Concepts
def test_encoding(cleandir):

    # Note: Encode a string to UTF-8
    # Note: Decode a string to Unicode

    u = u"café"
    ul = u.encode('utf-8', errors='strict')
    logger.info("ul %s.%s." % (type(ul), ul))

    s = "Flügel"
    logger.info("%s:%s" % (type(s), s))

    sl = s.decode('utf-8')
    logger.info("sl %s.%s." % (type(sl), sl))

    p = "Hi!"
    pl = unicode(p, "utf-8")
    logger.info("p %s:%s\tpl %s:%s" % (type(p), p, type(pl), pl))

    us = u"Hi!"
    sl = us.decode('utf-8')
    logger.info("sl %s:%s" % (type(sl), sl))

    q = u'Fl\xfcgel'
    logger.info("q %s:%s" % (type(q), q))

    ql = q.encode('utf-8')
    logger.info("ql %s:%s" % (type(q), ql))

if __name__ == "__main__":
    test_Concepts()