__author__ = 'morrj140'
import os

# Common Filenames
testDir = os.getcwd() + os.sep + u"test" + os.sep
testHomeDir = testDir + u"html"

conceptsTest = testDir + u"test.p"

exportFileTest = testDir + u"export.p"
exportFileGMLTest = testDir + u"export.gml"
exportFileImageTest = testDir + u"export.png"

listFiles = [u"corpus.mm", u"corpus.mm.index",
             u"Dictionary.dict", u"model.lsi",
             u"model.lsi.projection", u"topicsDict.p"]

gdb = u"http://localhost:7474/db/data/"

from sys import platform as _platform
if _platform == u"linux" or _platform == u"linux2":
    resetNeo4J = u"/home/james.morris/bin/reset.sh"
elif _platform == u"darwin":
    resetNeo4J = u"/Users/morrj140/Development/neo4j/bin/reset.sh"
elif _platform == u"win32":
    resetNeo4J = None
else:
    resetNeo4J = None


