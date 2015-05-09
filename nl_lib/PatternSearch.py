#!/usr/bin/env python
#
# Concept Class for NLP
#
__VERSION__ = 0.1
__author__ = u'morrj140'

import sys
import os

from pattern.web    import Bing, Google, Wikipedia, plaintext, encode_utf8, URL, extension, download
from pattern.en     import parsetree
from pattern.search import search

from nl_lib import Logger
logger = Logger.setupLogging(__name__)

from nl_lib.Constants import *
from nl_lib.Concepts import Concepts
from nl_lib.TopicCloud import TopicCloud
from nl_lib.ConceptGraph import PatternGraph, NetworkXGraph, Graph
    
AGENT = u"Mozilla/5.0 (X11; Linux x86_64; rv:20.0) Gecko/20100101 Firefox/20.0"


class PatternSearch(object):    
    urlConcepts = None
    wordConcepts = None
    searchTerm = None
    
    homeDir = None
    htmlFile = None
    
    g=None
    
    urlConcepts = None
    wordConcepts = None
        
    def __init__(self, searchTerm, homeDir=None):
        self.searchTerm = searchTerm       

        if homeDir == None:
            homeDir = os.curdir
            
        self.homeDir = homeDir + os.sep + u'cms'
        
        if not os.path.exists(self.homeDir):
            os.makedirs(self.homeDir)
            
        self.htmlFile = self.homeDir + os.sep + u"links.html"
        
        self.urlConcepts = Concepts(self.searchTerm, u"URLs")
        self.wordConcepts = Concepts(self.searchTerm, u"Words")
    
        self.g = PatternGraph()
        
    def htmlSearch(self, html, url):
        logger.debug(u"htmlSearch URL : %s" % url)
        logger.debug(u"html : %s" % html[:20])
               
        s = html.lower()
        s = plaintext(s)
        s = parsetree(s)
        
        #self.logSentences(s)

        # Execute a Regular Expression Search
        p = r'(NN)+'
        q = search(p, s)

        #self.logPOS(q)

        # Iterate over all the words in the POS
        logger.debug(u"  q.Length=%d" % len(q))
        logger.debug(u"  q[]=%s" % q)
        
        self.g, self.urlConcepts, self.wordConcepts = self.addNodes(self.g, q, url, self.urlConcepts, self.wordConcepts)

        return self.urlConcepts, self.wordConcepts

    def patternSearch(self, n=12, m=50):
        logger.info(u"patternSearch")
     
        proxyList = list()
        proxyList.append(u"3128")
        proxyList.append(u"206.217.138.154")
        
        logger.info(u"proxyList - %s" % proxyList)
     
        engine = Google(license=None, throttle=0.5, language=None)
        #engine = Bing(license=None, throttle=0.5, language=None)
    
        for i in range(n):                
            logger.info(u"Search %d" % i)
            results = engine.search(self.searchTerm, start=i+1, count=m, cached=False, proxy=proxyList)
            
            for r in results:
                logger.debug(u"Result=%s" % Concepts.encode_utf8(r.text))
                url = Concepts.encode_utf8(r.url)
                logger.debug(u"URL=%s" % url)
                
                #if url[-4:] == ".com":
                #    continue
                        
                s = r.text.lower()
                s = plaintext(s)
                s = parsetree(s)
    
                #self.logSentences(s)
    
                # Execute a Regular Expression Search
                #p = r'(NN)+ (VB)+'
                p = r'(NN)+'
                q = search(p, s)
    
                #logPOS(q)
    
                # Iterate over all the words in the POS
                logger.debug(u"  q.Length=%d" % len(q))
                logger.debug(u"  q[]=%s" % q)
    
                self.g, self.urlConcepts, self.wordConcepts = self.addNodes(self.g, q, url, self.urlConcepts, self.wordConcepts)
        
        return self.urlConcepts, self.wordConcepts
    
    def savePatternConcepts(self):
        logger.debug(u"Save Concepts")

        Concepts.saveConcepts(self.urlConcepts, u"URLs.p")
        Concepts.saveConcepts(self.wordConcepts, u"Words.p")
        
    def exportGraph(self):
        self.g.exportGraph()
        
        logger.debug(u"Save HTML")
        # save URL-Words
        self.saveURL_HTML()
        
        logger.debug(u"Create Tag Cloud")
        tc = TopicCloud(self.wordConcepts, self.homeDir)  
        tc.createCloudImage()
        logger.debug(u"Complete createTopicsCloud")
        
    def subGraph(self):
        # Take the largest subgraph.
        h = self.g.split()[0]
        
        # Sort by Node.weight.i = 1
        i = 0
        newGraph = Graph()
        for n in h.sorted()[:30]:
            i += 1
            n.fill = (0, 0.5, 1, 0.75 * n.weight)
            logger.info(u"i:%d=%s" % (i, n))
            newGraph.add_node(n.id)
            logger.debug(u"edges : %s" % n.edges)
    
            for e in n.edges:
                logger.debug(u"edge1 : %s, edge2 : %s" % (e.node1.id, e.node2.id))
                if e.node1.id == n.id:
                    newGraph.add_node(e.node2.id)
                else:
                    newGraph.add_node(e.node1.id)
                newGraph.add_edge(e.node1.id, e.node2.id, stroke=(0, 0, 0, 0.75))
        
        h = newGraph.split()
        
        return h
    
    def saveURL_HTML(self):
        logger.debug(u"saveURL_HTML")
        
        # self.urlConcepts.logConcepts()
        
        e = self.urlConcepts.sortConcepts(u"URL")
        
        logger.debug(u"len(e)=%d" % len(e))
    
        head  = \
            u"<!doctype html>\n" \
            u"<html>\n" \
            u"<head>\n" \
                u"\t<title>Search Words</title>\n" \
                u"\t<meta charset=\"utf-8\">\n" \
                u"\t<meta http-equiv=\"refresh\" content=\"300\">\n" \
                u"<link rel=\"stylesheet\" href=\"style.css\" type=\"text/css\" media=\"screen\" />" \
            u"</head>\n" \
            u"<body>\n" \
                u"\t<div id=url>\n" \
                u"<table border=\"1\" width=\"100%\">\n"
        body = u" "
        for x in e:
            if x[1] > 1:
                tableCol1 = u"<td align=\"right\" width=\"30%%\"><a href=\"%s\">[%d](%d)-%s</a></td>\n" % (x[0], x[1] ,x[2], x[0])
                tableCol2 = u"<td align=\"left\" width=\"70%%\">[%d]=[%s]</td>\n" % (len(x[3]), str(x[3]))
                tableRow  = u"<tr>\n%s\n%s\n</tr>\n" % (tableCol1, tableCol2)
                body = u"%s%s" % (body, tableRow)
    
        foot = \
            u"</table>\n" \
            u"</body>\n" \
            u"\t</div>\n" \
            u"</body>\n" \
            u"</html>"
    
        html = u"".join(s for s in (str(head), u"Links for ", self.searchTerm, u"<br>\n", str(body), str(foot)))
    
        logger.debug(head + body + foot)
            
        logger.info(u"Savings links : %s" % self.htmlFile)
        
        cf = open(self.htmlFile, u"wb")
        cf.write(html)
        cf.close()

    def loglengthOfConcepts(self):
        lwc = len(self.wordConcepts.getConcepts())
        luc = len(self.urlConcepts.getConcepts())
        logger.info(u"wordsConcepts - %d" % lwc)
        logger.info(u"urlConcepts   - %d" % luc)
        
        return lwc, luc

    def _logSentences(self, s):
        for sentence in s:
            for chunk in sentence.chunks:
                for word in chunk.words:
                    logger.debug(word)

    def _logPOS(self, q):
        for word in q[0].words:
            logger.info(word.string + word.tag)

    def addNodes(self, g, q, url, urlConcepts, wordConcepts):
        nodeURL = dict()
        logger.debug(u"---url %s" % url)
        for w in q:
            logger.debug(u"  w.Length=%d" % len(w))
            logger.debug(u"  w=%s" % w)
            i = 1
            for c in w:
                urls = urlConcepts.addConceptKeyType(url, u"URL")
                cc = urls.addConceptKeyType(Concepts.encode_utf8(c.string), u"Word")
                
                chunk = wordConcepts.addConceptKeyType(Concepts.encode_utf8(c.string), u"Word")
                chunk.addConceptKeyType(Concepts.encode_utf8(c.chunk), u"Chunk")
    
                logger.debug(u"  " + Concepts.encode_utf8(c.string))
    
                if i == 1:
                    i = 2
                    logger.debug(u"--" + Concepts.encode_utf8(c.string))
                    pp = cc
                    g.addNode(cc)
                else:
                    logger.debug(u"--" + Concepts.encode_utf8(c.string))
                    g.addNode(cc)
                    g.addEdge(pp, cc)
                        
        return g, urlConcepts, wordConcepts
