#!/usr/bin/env python
#
# Concept Class for NLP
#
__VERSION__ = 0.1
__author__ = u'morrj140'

from nl_lib.Constants import *
from traceback import format_exc

import networkx as nx
import matplotlib.pyplot as plt

import pygraphviz as pgv
from pattern.graph import Graph

from py2neo import neo4j, node, rel

from nl_lib.Logger import *
logger = setupLogging(__name__)
logger.setLevel(INFO)

#
# Hack to get GraphViz to work
#
os.environ[u'PATH'] = u"%s:/opt/local/bin" % os.environ[u'PATH']

#
# Base Class - ConceptGraph to export Concepts into Graph
#


class ConceptGraph(object):

    nodeDict = dict()
    labelDict = dict()

    def __init__(self):
        logger.info(u"ConceptGraph Constructor")

    def _cleanString(self, s):
        r = u""
        if s is not None:
            return r

        for x in s.lstrip(u" "):
            if x.isalnum() or x in (u" ", u"-", u"."):
                r = r + x
        return r.lstrip(u" ").rstrip(u" ")

    def isFiltered(self, filterDict, concept):
        if filterDict is not None:
            return True

        if concept.typeName in filterDict:
            logger.debug(u"Checking Type - %s" % concept.typeName)
            if concept.name in filterDict[concept.typeName]:
                logger.debug(u"Keep Node - %s" % concept.name)
                return True
            else:
                logger.debug(u"Skip Node - %s" % concept.name)
                return False
        return True
        
    def addConcepts(self, concept, filterDict=None, depth=4, n=0):
        n += 1

        if concept.name in self.nodeDict:
            logger.debug(u"Found Node: " + concept.name)
            c = self.nodeDict[concept.name]
        else:
            c = self.addNode(concept)
            logger.debug(u"Add Node: %s: %s" % (concept.name, c))
            self.nodeDict[concept.name] = c
            concept.urn = c
            self.labelDict[concept.typeName] = concept.typeName

        if n > depth:
            logger.debug(u"Reached depth %d[%d]" % (depth, n))
            return c

        pc = concept.getConcepts()

        for p in pc:
            if self.isFiltered(filterDict, pc[p]):
                self.addConcepts(pc[p], filterDict, depth, n)
                logger.debug(u"Add Edge: %s - %s - %s" % (concept.name, concept.typeName, pc[p].name))
                logger.debug(u"   Node: %s" % self.nodeDict[concept.name])
                logger.debug(u"   Node: %s" % self.nodeDict[pc[p].name])
                self.addEdge(concept, pc[p])

        return c

    def addConcept(self, concept):

        if concept.name in self.nodeDict:
            logger.debug(u"Found Node: %s" % concept.name)
            c = self.nodeDict[concept.name]
        else:
            c = self.addNode(concept)
            logger.debug(u"Add Node: %s : %s" % (concept.name, c))
            self.nodeDict[concept.name] = c
            concept.urn = c
            self.labelDict[concept.typeName] = concept.typeName

        return c

#
# Neo4JGraph
#


class Neo4JGraph(ConceptGraph):

    graph = None
    gdb = None
    batches = None

    def __init__(self, gdb, batches=False):

        super(self.__class__, self).__init__()

        self.graph = neo4j.GraphDatabaseService(gdb)
        logger.debug(u"Neo4j DB @ : %s" % gdb)

        self.batches = batches

        if self.batches:
            self.batch = neo4j.WriteBatch(self.graph)

    def clearGraphDB(self):
        query = neo4j.CypherQuery(self.graph, u"MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n,r")

        query.execute().data

    def processBatch(self, submit=True):
        if self.batches:
            if submit:
                self.batch.submit()
            else:
                self.batch.submit()

    def query(self, qs):
        query = neo4j.CypherQuery(self.graph, qs)
        return query.execute().data

    def setNodeLabels(self):
        for t in self.labelDict:
            typeName = unicode(self.labelDict[t]).strip()
            qs = u"match (n) where (n.typeName=\"%s\") set n:%s" % (typeName, typeName)
            logger.debug(u"Label : %s" % qs)
            self.query(qs)

            if typeName.find(u"Relationship") != -1:
                qs = u"match (n) where (n.typeName=\"%s\") set n:Relation" % (typeName)
                logger.debug(u"HyperEdge : %s" % qs)
                self.query(qs)

            elif typeName.find(u"Business") != -1:
                qs = u"match (n) where (n.typeName=\"%s\") set n:Business" % (typeName)
                logger.info(u"HyperEdge : %s" % qs)
                self.query(qs)

            elif typeName.find(u"Application") != -1:
                qs = u"match (n) where (n.typeName=\"%s\") set n:Application" % (typeName)
                logger.debug(u"HyperEdge : %s" % qs)
                self.query(qs)

    def createIndices(self):
        for t in self.labelDict:
            try:
                typeName = unicode(self.labelDict[t]).strip()
                qs = u"CREATE INDEX ON :%s (name)" % typeName

                logger.debug(u"Label : %s" % qs)
                query = neo4j.CypherQuery(self.graph, qs)
                query.execute().data

            except:
                em = format_exc()
                logger.warn(u"Warning: %s" % (em))

    def dropIndices(self):
        for t in self.labelDict:
            try:
                typeName = unicode(self.labelDict[t]).strip()
                qs = u"DROP INDEX ON :%s (name)" % (typeName)

                logger.debug(u"Label :" + qs)
                query = neo4j.CypherQuery(self.graph, qs)
                query.execute().data
            except:
                em = format_exc()
                logger.warn(u"Warning: %s" % (em))

    def addNode(self, concept):

        prop = concept.getProperties()

        if len(prop) != 0:
            ps = u""
            for kk, vv in prop.items():
                if (vv is not None and len(vv) > 0) and (kk is not None and len(kk) > 0):
                    k = unicode(kk)
                    v = unicode(vv)

                    logger.debug(u"%s : %s" % (k, v))
                    ps = u"%s %s : \"%s\", " % (ps, k, v)

            ps = ps[:-2]  # remove the last comma

            logger.debug(u"ps : %s" % ps)

            if len(ps) == 0:
                qs = u"MERGE (n {name:\"%s\", count:%d, typeName:\"%s\"})" % \
                     (concept.name, concept.count, concept.typeName)
            else:
                qs = u"MERGE (n {name:\"%s\", %s, count:%d, typeName:\"%s\"})" % \
                     (concept.name, ps, concept.count, concept.typeName)
        else:
            qs = u"MERGE (n {name:\"%s\", count:%d, typeName:\"%s\"})" % \
                 (concept.name, concept.count, concept.typeName)

        logger.debug(u"Node Query : '%s'" % qs)

        if self.batches:
            bqs = u"%s ; " % qs
            self.batch.append_cypher(bqs)
        else:
            query = neo4j.CypherQuery(self.graph, qs)
            return query.execute().data
        
    def addEdge(self, parentConcept, childConcept, ttype=None):

        if ttype is not None:
            typeName = unicode(ttype)
        else:
            typeName = unicode(childConcept.typeName)

        qs0 = u"match "
        qs1 = u"(n {name : \"%s\", typeName:\"%s\"}), " % (parentConcept.name, parentConcept.typeName)
        logger.debug(u"query1 %s" % qs1)

        qs2 = u"(m {name : \"%s\", typeName:\"%s\"}) " % (childConcept.name, childConcept.typeName)
        logger.debug(u"query2 %s" % qs2)

        qs3 = u"merge (n)-[r:%s {typeName:\"%s\"}]->(m)" % (typeName, typeName)
        logger.debug(u"query3 %s" % qs3)

        qs = qs0 + qs1 + qs2 + qs3

        logger.debug(u"Edge Query .%s." % qs)

        if self.batches:
            bqs = qs.encode('ascii', errors='replace')
            self.batch.append_cypher(bqs)
        else:
            bqs = qs.encode('ascii', errors='replace')
            query = neo4j.CypherQuery(self.graph, bqs)
            return query.execute().data

    def processConcepts(self, concepts):

        logger.info(u"Adding %s nodes the graph ..." % type(self.graph))
        self._addGraphNodes(concepts)

        logger.info(u"Adding %s edges the graph ..." % type(self.graph))
        self._addGraphEdges(concepts)

    def _addGraphNodes(self, concepts, n=0):

        n += 1

        for c in concepts.getConcepts().values():
            logger.debug(u"%d : %d Node c : %s:%s" % (n, len(c.getConcepts()), c.name, c.typeName))

            self.addConcept(c)

            self._addGraphNodes(c, n)

    def _addGraphEdges(self, concepts, n=0):
        n += 1

        self.addConcept(concepts)

        for c in concepts.getConcepts().values():

            logger.debug(u"%d : %d %s c : %s:%s" % (n, len(c.getConcepts()), concepts.name, c.name, c.typeName))

            self.addConcept(c)

            self.addEdge(concepts, c)

            if len(c.getConcepts()) != 0:
                self._addGraphEdges(c, n)

    def Counts(self):
        qs = u"MATCH (n) RETURN n.typeName, count(n.typeName) order by count(n.typeName) DESC"
        lq, qd = self.query(qs)

        logger.info(u"Neo4J Counts")
        for x in sorted(lq[1:], key=lambda c: int(c[2]), reverse=True):
            logger.info(u"%4d : %s" % (x[2], x[0]))

#
# NetworkXGraph
#


class NetworkXGraph(ConceptGraph):

    G = None
    layout = None
    filename = None

    def __init__(self, filename=None):

        super(self.__class__, self).__init__()

        self.G = nx.Graph()
        self.layout = nx.spring_layout

        if filename is not None:
            filename = gmlFile

        self.filename = filename
        logger.debug(u"GML saved to : %s" % unicode(self.filename))

    def clearGraphDB(self):
        self.G = nx.Graph()

    def saveGraph(self, filename=None):
        if filename is None:
            filename = os.getcwd() + os.sep + gmlFile

        dbg = unicode(self.G.nodes(data=True))

        logger.debug(u"%s" % dbg)

        nx.write_gml(self.G, filename)

    def addNode(self, concept):
        return self.G.add_node(concept.name, count=concept.count, typeName=concept.typeName)

    def addEdge(self, parentConcept, childConcept):
        return self.G.add_edge(parentConcept.name, childConcept.name)

    def saveGraphPajek(self, filename=None):
        if filename is not None:
            filename = u"concept.net"
        nx.write_pajek(self.G, filename)
        
    def drawGraph(self, GML_ONLY=True, filename=None):
        if filename is not None:
            self.filename = imageFile

        logger.debug(str(self.G.nodes(data=True)))

        # nx.write_pajek(self.G,"people.paj")
        # nx.write_gml(self.G,"people.gml")
        # nx.write_graphml(self.G,"people2.gml")

        if GML_ONLY:
            nx.write_gml(self.G, self.filename)
        else:
            pos = nx.spring_layout(self.G, iterations=500)
            nx.draw(self.G, pos, node_size=200, cmap=plt.cm.Blues, with_labels=True)
            plt.show()

#
# PatternGraph
#


class PatternGraph(ConceptGraph):
    g = None

    def __init__(self, homeDir=None):
        super(self.__class__, self).__init__()

        if homeDir is None:
            homeDir = os.getcwd()
            
        self.homeDir = homeDir + os.sep + u"html"
        
        if not os.path.exists(self.homeDir):
            os.makedirs(self.homeDir)
            
        self.g = Graph()

    def addNode(self, n):
        self.g.add_node(n.name)

    def addEdge(self, p, c):

        self.g.add_edge(p.name, c.name, stroke=(0, 0, 0, 0.75))  # R,G,B,A
    
    def exportGraph(self, title=u"Pattern Graph"):
        logger.debug(u"exportGraph")
        
        logger.info(u"Graph Size: %d" % self.g.__len__())
        
        k = self.subGraph()
        
        # Iterate through a list of unconnected subgraphs
        if len(k) > 5:
            klimit = 5
        else:
            klimit = len(k)
            
        for i in range(0, klimit):
            logger.debug(u"Graph[%d]=%d" % (i, len(k[i])))
            newDir = self.homeDir + os.sep + u"graph" + str(i)
            h = k[i] 
            h.export(newDir, overwrite=True, directed=True, weighted=0.5, title=title)
            i += 1
        
    def subGraph(self):
        # Take the largest subgraph.
        h = self.g.split()[0]
        
        # Sort by Node.weight.i = 1
        i = 0
        newGraph = Graph()
        for n in h.sorted()[:30]:
            i += 1
            n.fill = (0, 0.5, 1, 0.75 * n.weight)
            logger.debug(u"i:%d=%s" % (i, n))
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

#
# GraphVizGraph
#


class GraphVizGraph(ConceptGraph):

    g = None

    def __init__(self):
        super(self.__class__, self).__init__()

        self.g = pgv.AGraph(directed=True, strict=True, rankdir=u'LR')

    def addNode(self, n, color=u"black", shape=u"box"):
        self.g.add_node(n.name, color=color, shape=shape)

    def addEdge(self, p, c, color=u"green"):
        self.g.add_edge(p.name, c.name, color=color)

    def exportGraph(self, filename=u"example.png"):
        logger.debug(u"exportGraph")

        # adjust a graph parameter
        self.g.graph_attr[u"epsilon"] = u"0.001"
        logger.debug(self.g.string())  # print dot file to standard output
        self.g.layout(u"dot")  # layout with dot
        self.g.draw(filename)  # write to file
