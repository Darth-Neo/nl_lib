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
    
    delchars = ''.join(c for c in map(chr, range(255)) if (not c.isalnum() and c != ' '))

    def __init__(self, name=None, typeName=None):
        logger.debug("Init Concept - %s:%s" % (name, typeName))
        
        self.name = self.cleanString(name)
        self.typeName = self.cleanString(typeName)
        self.cd = dict()
        self.count = 1

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

    def cleanString(self, name):
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

    def sdp(self, x, y):
        try:
            z = int((float(x * y) / float(x + y)) * 100.00)
        except:
            z = 0
        logger.debug("z - %3.2f" % z)
        return z

    def sortConcepts(self, typeName):
        logger.info("sortConcepts - %s" % typeName)

        typeNameDict = self.dictChildrenType(typeName)
        logger.info("typeNameDict : %s" % typeNameDict)

        nl = list()
        for n in typeNameDict:
            logger.info("n - %s" % n)
            cl = list()
            cl.append(typeNameDict[n].name) #0
            wl = list();
            c = typeNameDict[n].getConcepts()
            for v in c:
                wl.append(c[v].name)
            cl.append(self.sdp(typeNameDict[n].count, len(wl))) #1
            cl.append(typeNameDict[n].count) #2
            cl.append(wl) #3
            cl.append(len(wl)) #4
            nl.append(cl)

        return sorted(nl, key=lambda c: abs(c[1]), reverse=False)
    
    def logConcepts(self, n=0):
        pc = self.getConcepts()

        spaces = " " * n

        for p in pc.values():
            logger.info("%s%s[%d]{%s}->Count=%s" % (spaces, p.name, len(p.name), p.typeName, p.count))
            p.logConcepts(n+1)

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
            self.cd[k] = c
            logger.debug("Not found: %s->%s" % (k, t))
        return c

    def addConcept(self, concept):
        logger.debug("addConcept: %s " % concept.name)
        self.cd[concept.name] = concept
        
    def addListConcepts(self, listConcepts, typeConcept):
        for p in listConcepts:
            logger.debug(p + ":" + typeConcept)
            self.addConcept(p, typeConcept)
        
    @staticmethod
    def saveConcepts(conceptDict, conceptFile):
        try:
            logger.debug("Save %s" % (conceptFile))
            cf = open(conceptFile, "wb")
            pickle.dump(conceptDict, cf)
            cf.close()
        except:
            logger.error(str(sys.exc_info()[0]))

    @staticmethod        
    def loadConcepts(conceptFile):
        conceptDict = None
        try:
            logger.debug("Load %s" % (conceptFile))
            cf = open(conceptFile, "rb")
            conceptDict = pickle.load(cf)
            cf.close()
        except:
            logger.error(str(sys.exc_info()[0]))
            
        return conceptDict

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

if __name__ == "__main__":
    import doctest
    doctest.testmod()
