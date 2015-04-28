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
    
    delchars = ''.join(c for c in map(chr, range(255)) if (not c.isalnum() and c != ' '))

    def __init__(self, name=None, typeName=None):
        logger.debug("Init Concept - %s:%s" % (name, typeName))
        
        self.name = self.cleanString(name)
        self.typeName = self.cleanString(typeName)
        self.cd = dict()
        self.properties = dict()
        self.count = 0

    def __getitem__(self, id):
        try:
            return dict.__getitem__(self.cd, id)
        except KeyError:
            raise KeyError, "no concept with id '%s'" % id

    def incCount(self):
        self.count = self.count + 1
        return self.count

    def getConcepts(self):
        return self.cd

    def setProperties(self, props):

        if isinstance(props, dict):
            self.properties = props
        else:
            logger.warn("Props given not Dict()!")

    def getProperties(self):
        return self.properties

    def cleanString(self, name):
        '''
        :param name: name
        :return: string
        Note: Encode a string to UTF-8
        Note: Decode a string to Unicode
        '''
        try:
            if isinstance(name, (str, unicode)):
                return name.encode('utf-8',errors='ignore')
            else:
                n = name.translate(None, self.delchars).strip()
            u = unicode(n, "utf-8", errors='ignore' )
            return u.encode( "utf-8", errors="ignore" )
        except:
            return " "

    def dictChildrenType(self, typeName, n=4, conceptFilter=None):
        logger.debug("dictChildrenType %s" % typeName)
        if n < 1:
            return None

        if conceptFilter == None:
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
        logger.debug("z - %3.2f" % z)
        return z

    def sortConcepts(self, typeName):
        logger.debug("sortConcepts - %s" % typeName)

        typeNameDict = self.dictChildrenType(typeName)
        logger.debug("typeNameDict : %s" % typeNameDict)

        nl = list()
        for n in typeNameDict:
            logger.info("n - %s" % n)
            cl = list()
            cl.append(typeNameDict[n].name) #0
            wl = list();
            c = typeNameDict[n].getConcepts()
            for v in c:
                wl.append(c[v].name)
            cl.append(self._sdp(typeNameDict[n].count, len(wl))) #1
            cl.append(typeNameDict[n].count) #2
            cl.append(wl) #3
            cl.append(len(wl)) #4
            nl.append(cl)

        return sorted(nl, key=lambda c: abs(c[1]), reverse=False)

    def _logProperties(self, c, spaces):

        prop = c.getProperties()

        if prop != None:
            for k , v in prop.items():
                logger.info("%sKey %s => Value %s" % (spaces, k, v))
    
    def logConcepts(self, n=0):
        pc = self.getConcepts()

        spaces = " " * n

        for p in pc.values():
            logger.info("%s%s[%d]{%s}->Count=%s" % (spaces, p.name, len(p.name), p.typeName, p.count))
            self._logProperties(p, spaces)

            p.logConcepts(n+1)

    def cleanConcepts(self, n=0):
        pc = self.getConcepts()

        spaces = " " * n

        for p in pc.values():
            logger.debug("%s%s[%d]{%s}->Count=%s" % (spaces, p.name, len(p.name), p.typeName, p.count))
            p.name = p.name.strip("\"")
            p.typeName = p.typeName.strip("\"")
            p.cleanConcepts(n+1)

    def listCSVConcepts(self, lcsv= None, n=0):
        pc = self.getConcepts()

        commas = "," * n

        if lcsv == None:
            lcsv = list()

        if len(self.name) > 1:
            output = "%s%s,%s" % (commas, self.name, self.typeName)
            lcsv.append(output)

        for p in pc.values():
            p.listCSVConcepts(lcsv, n+2)

        return lcsv

    def printConcepts(self, n=0):
        pc = self.getConcepts()

        spaces = " " * n

        if len(self.name) > 1:
            print("%s%s" % (spaces, self.name))

        for p in pc.values():
            p.printConcepts(n+1)

    def addConceptKeyType(self, keyConcept, typeConcept):
        k = self.cleanString(keyConcept)
        t = self.cleanString(typeConcept)
        
        if self.cd.has_key(k):
            c = self.cd[k]
            c.incCount()
            logger.debug("Found:     %s\tCount:%s" % (k, c.count))
        else:
            c = Concepts(k, t)
            c.incCount()
            self.cd[k] = c
            logger.debug("Not found: %s->%s" % (k, t))

        return c

    def addConcept(self, concept):
        logger.debug("addConcept: %s " % concept.name)
        self.cd[concept.name] = concept
        
    def addListConcepts(self, listConcepts):
        for p in listConcepts:
            logger.debug("%s:%s" % (p.name, p.typeName))
            self.addConcept(p)
        
    @staticmethod
    def saveConcepts(concepts, conceptFile):
        try:
            logger.info("Saving Concepts : %s : %s[%d][%s]" % (conceptFile, concepts.name, concepts.count, concepts.typeName))
            cf = open(conceptFile, "wb")
            pickle.dump(concepts, cf)
            cf.close()
        except:
            logger.error(str(sys.exc_info()[0]))

    @staticmethod        
    def loadConcepts(conceptFile):
        concepts = None

        if not os.path.exists(conceptFile):
            logger.error("%s : Does Not Exist!" % conceptFile)

        try:
            cf = open(conceptFile, "rb")
            concepts = pickle.load(cf)
            logger.info("Loaded Concepts : %s : %s[%d][%s]" % (conceptFile, concepts.name, concepts.count, concepts.typeName))
            cf.close()
        except:
            logger.error(str(sys.exc_info()[0]))
            
        return concepts

    @staticmethod
    def decode_utf8(v, encoding="utf-8"):
        """ Returns the given value as a Unicode string (if possible).
        """
        try:
            if isinstance(encoding, basestring):
                encoding = ((encoding,"ignore"),) + (("windows-1252",), ("utf-8", "ignore"))
            if isinstance(v, str):
                for e in encoding:
                    try: return v.decode(*e)
                    except:
                        logger.error(str(sys.exc_info()[0]))
                return v
            return unicode(v)
        except:
            return " "
        
    @staticmethod
    def encode_utf8(v, encoding="utf-8"):
        """ Returns the given value as a Python byte string (if possible).
        """
        try:
            if isinstance(encoding, basestring):
                encoding = ((encoding, "ignore"),) + (("windows-1252",), ("utf-8", "ignore"))
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

        spaces = " " * n

        if cstr == None:
            rs = "%s," % concepts.name
        else:
            rs = cstr

        logger.debug("%s%d[%s]" % (spaces, n, rs))

        if len(concepts.getConcepts().values()) == 0:
            return rs + "\n"

        for c in concepts.getConcepts().values():
            rs = rs + Concepts._lineCSV(c, cstr)
            logger.debug("%s%s[%s]" % (spaces, n, rs))

        logger.debug("%s%d[%s]" % (spaces, n, rs))

        return rs
    @staticmethod
    def outputConceptsToCSV(concepts, fileExport):
        n = 0

        #f = open(fileExport,'w')
        #f.write("Model, Source, Type, Relationship, type, Target, Type\n")

        for c in concepts.getConcepts():
            n += 1
            fl = Concepts._lineCSV(concepts, None)
            logger.info("fl : %s[%s]" % (fl[:-1], n))

        #f.close()
        #logger.info("Save Model : %s" % fileExport)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
