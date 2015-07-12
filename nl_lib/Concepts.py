#!/usr/bin/env python
#
# Concept Class for NLP
#
__VERSION__ = 0.1
__author__ = 'morrj140'

import os
import sys
import pickle
from __future__ import print_function

from Logger import *
logger = setupLogging(__name__)
logger.setLevel(INFO)

#
# Concept Class which support recursive concepts via a dictionary
#


class Concepts(object):
    name = None
    typeName = None
    count = 0
    urn = None
    cd = None
    conceptFile = None
    properties = None

    def __init__(self, name=None, typeName=None):
        self.name = self._convertConcepts(name)
        self.typeName = self._convertConcepts(typeName)
        self.cd = dict()
        self.properties = dict()
        self.count = 0

        logger.debug(u"Init Concept - %s:%s" % (self.name, self.typeName))

    def __getitem__(self, _id):
        try:
            return dict.__getitem__(self.cd, _id)

        except KeyError:
            raise KeyError, u"no concept with id '%s'" % _id

    def incCount(self):
        self.count += 1
        return self.count

    def getConcepts(self):
        return self.cd

    def setProperties(self, props):

        if isinstance(props, dict):
            self.properties = props
        else:
            logger.warn(u"Props given not Dict()!")

    def getProperties(self):
        return self.properties

    def dictChildrenType(self, typeName, n=4, conceptFilter=None):

        typeName = self._convertConcepts(typeName)
        logger.debug(u"dictChildrenType %s" % typeName)
        if n < 1:
            return None

        if conceptFilter is None:
            conceptFilter = dict()

        pc = self.getConcepts()

        for p in pc.values():
            if p.typeName == typeName:
                if p.name not in conceptFilter:
                    conceptFilter[p.name] = p

            p.dictChildrenType(typeName, n-1, conceptFilter)

        return conceptFilter

    def _sdp(self, x, y):
        try:
            z = int((float(x * y) / float(x + y)) * 100.00)
        except:
            z = 0
        logger.debug(u"z - %3.2f" % z)
        return z

    def sortConcepts(self, typeName):
        typeName = self._convertConcepts(typeName)
        logger.debug(u"sortConcepts - %s" % typeName)

        typeNameDict = self.dictChildrenType(typeName)
        logger.debug(u"typeNameDict : %s" % typeNameDict)

        nl = list()
        for n in typeNameDict:
            logger.info(u"n - %s" % n)

            cl = list()
            cl.append(typeNameDict[n].name)  # 0

            wl = list()
            c = typeNameDict[n].getConcepts()

            for v in c:
                wl.append(unicode(c[v].name))

            cl.append(self._sdp(typeNameDict[n].count, len(wl)))  # 1
            cl.append(typeNameDict[n].count)  # 2
            cl.append(wl)  # 3
            cl.append(len(wl))  # 4
            nl.append(cl)

        return sorted(nl, key=lambda cc: abs(cc[1]), reverse=False)

    def listCSVConcepts(self, lcsv=None, n=0):
        pc = self.getConcepts()

        commas = u"," * n

        if lcsv is None:
            lcsv = list()

        if len(self.name) > 1:
            output = u"%s%s,%s" % (commas, self.name, self.typeName)
            lcsv.append(output)

        for p in pc.values():
            p.listCSVConcepts(lcsv, n+2)

        return lcsv

    def _fProperties(self, c, spaces, f=None):
        prop = c.getProperties()

        if prop is not None:
            for k, v in prop.items():
                if f is None:
                    print(u"%sKey %s => Value %s" % (spaces, k, v))
                else:
                    f(u"%sKey %s => Value %s" % (spaces, k, v))
    
    def logConcepts(self, n=0):
        pc = self.getConcepts()
        spaces = u" " * n
        f = logger.info

        for p in pc.values():
            logger.info(u"%s%s[%d]{%s}->Count=%s" % (spaces, p.name, len(p.name), p.typeName, p.count))
            self._fProperties(p, spaces, f)
            p.logConcepts(n+1)

    def _printProperties(self, c, spaces):
        prop = c.getProperties()

        if prop is not None:
            for k, v in prop.items():
                print(u"%sKey %s => Value %s" % (spaces, k, v))

    def printConcepts(self, n=0):
        pc = self.getConcepts()
        spaces = u" " * n
	f = print

        if n == 0:
            print(u"%s" % os.linesep)

        for p in pc.values():
            if n == 0:
                print(u"%s" % os.linesep)

            print(u"%s%s" % (spaces, p.name))
            self._fProperties(p, spaces, f)
            p.printConcepts(n+1)


    def addConceptKeyType(self, keyConcept, typeConcept):

        k = self._convertConcepts(keyConcept)
        t = self._convertConcepts(typeConcept)

        self.incCount()

        if k in self.cd:
            c = self.cd[k]
            logger.debug(u"Found:     %s\tCount:%s" % (k, c.count))
        else:
            c = Concepts(k, t)
            self.cd[k] = c
            logger.debug(u"Not found: %s->%s" % (k, t))

        return c

    def addConcept(self, concept):
        logger.debug(u"addConcept: %s " % concept.name)
        self.cd[concept.name] = concept
        
    def addListConcepts(self, listConcepts):
        for p in listConcepts:
            p.name = self._convertConcepts(p.name)
            p.typeName = self._convertConcepts(p.typeName)
            logger.debug(u"%s:%s" % (p.name, p.typeName))
            self.addConcept(p)

    def _cleanConcepts(self, n=0):

        logger.info(u"%s : %s", self.name, self.typeName)
        pc = self.getConcepts()

        spaces = u" " * n

        for p in pc.values():
            logger.debug(u"%s%s[%d]{%s}->Count=%s" % (spaces, p.name, len(p.name), p.typeName, p.count))
            p.name = self._convertConcepts(p.name)
            p.typeName = self._convertConcepts(p.typeName.strip(u"\""))
            p.cleanConcepts(n+1)

    @staticmethod
    def _convertConcepts(s):

        try:
            if isinstance(s, str):
                s = s.decode(u"ascii", errors=u"replace")
                s = s.encode(u"utf-8", errors=u"replace")
        except Exception, msg:
            logger.warn(u"Ops.. %s" % msg)
        return s

    @staticmethod
    def saveConcepts(concepts, conceptFile):
        try:
            logger.info(u"Saving Concepts : %s : %s[%d][%s]"
                        % (conceptFile, concepts.name, concepts.count, concepts.typeName))
            cf = open(conceptFile, u"wb")
            pickle.dump(concepts, cf)
            cf.close()
        except:
            logger.error(str(sys.exc_info()[0]))

    @staticmethod        
    def loadConcepts(conceptFile):
        concepts = None

        if not os.path.exists(conceptFile):
            logger.error(u"%s : Does Not Exist!" % conceptFile)

        try:
            cf = open(conceptFile, u"rb")
            concepts = pickle.load(cf)
            logger.info(u"Loaded Concepts : %s : %s[%d][%s]"
                        % (conceptFile, concepts.name, concepts.count, concepts.typeName))
            cf.close()
        except:
            logger.error(str(sys.exc_info()[0]))
            
        return concepts

    @staticmethod
    def _lineCSV(concepts, cstr=None, n=0):
        n += 1

        spaces = u" " * n

        if cstr is not None:
            rs = u"%s," % concepts.name
        else:
            rs = cstr

        logger.debug(u"%s%d[%s]" % (spaces, n, rs))

        if len(concepts.getConcepts().values()) == 0:
            return u"%s\n" % rs

        for c in concepts.getConcepts().values():
            rs = u"%s%s" % (rs, Concepts._lineCSV(c, cstr))
            logger.debug(u"%s%s[%s]" % (spaces, n, rs))

        logger.debug(u"%s%d[%s]" % (spaces, n, rs))

        return rs

    @staticmethod
    def outputConceptsToCSV(concepts, fileExport=None):
        n = 0

        if fileExport is not None:
            pass

        # f = open(fileExport,'w')
        # f.write("Model, Source, Type, Relationship, type, Target, Type\n")

        for c in concepts.getConcepts().values():
            n += 1
            fl = Concepts._lineCSV(c, None)
            logger.info(u"fl : %s[%s]" % (fl[:-1], n))

        # f.close()
        # logger.info("Save Model : %s" % fileExport)

if __name__ == u"__main__":
    import doctest
    doctest.testmod()
