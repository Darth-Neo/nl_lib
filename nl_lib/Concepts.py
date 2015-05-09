#!/usr/bin/env python
#
# Concept Class for NLP
#
__VERSION__ = 0.1
__author__ = 'morrj140'

import os
import sys
import pickle

from nl_lib import Logger
logger = Logger.setupLogging(__name__)

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
    
    # delchars = u''.join(c for c in map(chr, range(255)) if (not c.isalnum() and c != ' '))

    def __init__(self, name=None, typeName=None):
        self.name = unicode(name)
        self.typeName = unicode(typeName)
        self.cd = dict()
        self.properties = dict()
        self.count = 0

        logger.debug(u"Init Concept - %s:%s" % (self.name, self.typeName))

    def __getitem__(self, id):
        try:
            return dict.__getitem__(self.cd, id)

        except KeyError:
            raise KeyError, u"no concept with id '%s'" % id

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

    def _cleanString(self, name):
        '''
        :param name: name
        :return: string
        Note: Encode a string to UTF-8
        Note: Decode a string to Unicode
        '''
        try:
            if isinstance(name, (str, unicode)):
                return name.encode(u'utf-8', errors=u'ignore')
            else:
                n = name.translate(None, self.delchars).strip()
            u = unicode(n, u"utf-8", errors=u'ignore')
            return u.encode(u"utf-8", errors=u"ignore")
        except:
            return u" "

    def dictChildrenType(self, typeName, n=4, conceptFilter=None):
        logger.debug(u"dictChildrenType %s" % typeName)
        if n < 1:
            return None

        if conceptFilter is None:
            conceptFilter = dict()

        pc = self.getConcepts()

        for p in pc.values():
            if p.typeName == typeName:
                if not conceptFilter.has_key(p.name):
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
        logger.debug(u"sortConcepts - %s" % unicode(typeName))

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

        return sorted(nl, key=lambda c: abs(c[1]), reverse=False)

    def _logProperties(self, c, spaces):

        prop = c.getProperties()

        if prop is not None:
            for k , v in prop.items():
                logger.info(u"%sKey %s => Value %s" % (spaces, k, v))
    
    def logConcepts(self, n=0):
        pc = self.getConcepts()

        spaces = u" " * n

        for p in pc.values():
            logger.info(u"%s%s[%d]{%s}->Count=%s" % (spaces, p.name, len(p.name), p.typeName, p.count))
            self._logProperties(p, spaces)

            p.logConcepts(n+1)

    def cleanConcepts(self, n=0):
        pc = self.getConcepts()

        spaces = u" " * n

        for p in pc.values():
            logger.debug(u"%s%s[%d]{%s}->Count=%s" % (spaces, p.name, len(p.name), p.typeName, p.count))
            p.name = p.name.strip(u"\"")
            p.typeName = p.typeName.strip(u"\"")
            p.cleanConcepts(n+1)

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

    def printConcepts(self, n=0):
        pc = self.getConcepts()

        spaces = u" " * n

        if len(self.name) > 1:
            print(u"%s%s" % (spaces, self.name))

        for p in pc.values():
            p.printConcepts(n+1)

    def addConceptKeyType(self, keyConcept, typeConcept):

        k = unicode(keyConcept)  # self.cleanString(keyConcept)
        t = unicode(typeConcept)  # self.cleanString(typeConcept)

        self.incCount()

        if self.cd.has_key(k):
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
            logger.debug(u"%s:%s" % (p.name, p.typeName))
            self.addConcept(p)
        
    @staticmethod
    def saveConcepts(concepts, conceptFile):
        try:
            logger.info(u"Saving Concepts : %s : %s[%d][%s]" % (conceptFile, concepts.name, concepts.count, concepts.typeName))
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
            logger.info(u"Loaded Concepts : %s : %s[%d][%s]" % (conceptFile, concepts.name, concepts.count, concepts.typeName))
            cf.close()
        except:
            logger.error(str(sys.exc_info()[0]))
            
        return concepts

    @staticmethod
    def _decode_utf8(v, encoding=u"utf-8"):
        """ Returns the given value as a Unicode string (if possible).
        """
        try:
            if isinstance(encoding, basestring):
                encoding = ((encoding, u"ignore"),) + ((u"windows-1252",), (u"utf-8", u"ignore"))
            if isinstance(v, str):
                for e in encoding:
                    try: return v.decode(*e)
                    except:
                        logger.error(str(sys.exc_info()[0]))
                return v
            return unicode(v)
        except:
            return u" "
        
    @staticmethod
    def _encode_utf8(v, encoding=u"utf-8"):
        """ Returns the given value as a Python byte string (if possible).
        """
        try:
            if isinstance(encoding, basestring):
                encoding = ((encoding, u"ignore"),) + ((u"windows-1252",), (u"utf-8", u"ignore"))
            if isinstance(v, unicode):
                for e in encoding:
                    try: return v.encode(*e)
                    except:
                        logger.error(str(sys.exc_info()[0]))
                return v
            return str(v)
        except:
            return " "

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
            return rs + u"\n"

        for c in concepts.getConcepts().values():
            rs = rs + Concepts._lineCSV(c, cstr)
            logger.debug(u"%s%s[%s]" % (spaces, n, rs))

        logger.debug(u"%s%d[%s]" % (spaces, n, rs))

        return rs

    @staticmethod
    def outputConceptsToCSV(concepts, fileExport):
        n = 0

        # f = open(fileExport,'w')
        # f.write("Model, Source, Type, Relationship, type, Target, Type\n")

        for c in concepts.getConcepts():
            n += 1
            fl = Concepts._lineCSV(concepts, None)
            logger.info(u"fl : %s[%s]" % (fl[:-1], n))

        # f.close()
        # logger.info("Save Model : %s" % fileExport)

if __name__ == u"__main__":
    import doctest
    doctest.testmod()
