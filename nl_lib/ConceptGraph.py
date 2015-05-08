#!/usr/bin/env python
#
# Concept Class for NLP
#
__VERSION__ = 0.1
__author__ = 'morrj140'

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

delchars = ''.join(c for c in map(chr, range(256)) if not c.isalnum())

#
# Base Class - ConceptGraph to export Concepts into Graph
#
class ConceptGraph(object):
    nodeDict = dict()
    labelDict = dict()

    def _cleanString(self, s):
        r = ""
        if s == None:
            return r

        for x in s.lstrip(" "):
            if x.isalnum() or x in (" ", "-", "."):
                r = r + x
        return r.lstrip(" ").rstrip(" ")

    def __init__(self):
        logger.info(u"ConceptGraph Constructor")

    def isFiltered(self, filterDict, concept):
        if filterDict == None:
            return True

        if filterDict.has_key(concept.typeName):
            logger.debug(u"Checking Type - " + concept.typeName)
            if concept.name in filterDict[concept.typeName]:
                logger.debug(u"Keep Node - " + concept.name)
                return True
            else:
                logger.debug(u"Skip Node - " + concept.name)
                return False
        return True
        
    def addConcepts(self, concept, filterDict=None, depth=4, n=0):
        n += 1

        if self.nodeDict.has_key(concept.name):
            logger.debug(u"Found Node: " + concept.name)
            c = self.nodeDict[concept.name]
        else:
            c = self.addNode(concept)
            logger.debug(u"Add Node: " + concept.name + ": " + str(c))
            self.nodeDict[concept.name] = c
            concept.urn = c
            self.labelDict[concept.typeName] = concept.typeName

        if (n > depth):
            logger.debug(u"Reached depth["+ str(depth) + "] = " + str(n))
            return c

        pc = concept.getConcepts()

        for p in pc:
            if self.isFiltered(filterDict, pc[p]):
                self.addConcepts(pc[p], filterDict, depth, n)
                logger.debug(u"Add Edge: " + concept.name + " - " + concept.typeName + " - " + pc[p].name)
                logger.debug(u"   Node: " + str(self.nodeDict[concept.name]))
                logger.debug(u"   Node: " + str(self.nodeDict[pc[p].name]))
                self.addEdge(concept, pc[p])

        return c

    def addConcept(self, concept):

        if self.nodeDict.has_key(concept.name):
            logger.debug(u"Found Node: " + concept.name)
            c = self.nodeDict[concept.name]
        else:
            c = self.addNode(concept)
            logger.debug(u"Add Node: " + concept.name + ": " + str(c))
            self.nodeDict[concept.name] = c
            concept.urn = c
            self.labelDict[concept.typeName] = concept.typeName


#
# Neo4JGraph
#
class Neo4JGraph(ConceptGraph):
    graph = None
    gdb = None
    batches = None

    delchars = ''.join(c for c in map(chr, range(255)) if (not c.isalnum()))

    def __init__(self, gdb, batches=False):

        self.graph = neo4j.GraphDatabaseService(gdb)
        logger.debug(u"Neo4j DB @ :" + gdb)

        self.batches = batches

        if self.batches == True:
            self.batch = neo4j.WriteBatch(self.graph)

    def clearGraphDB(self):
        query = neo4j.CypherQuery(self.graph, u"MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n,r")

        query.execute().data

    def processBatch(self, submit=True):
        if self.batches == True:
            if submit == True:
                self.batch.submit()
            else:
                self.batch.submit()

    def query(self, qs):
        query = neo4j.CypherQuery(self.graph, qs)
        return query.execute().data

    def setNodeLabels(self):
        for t in self.labelDict:
            typeName = self.labelDict[t].translate(None, self.delchars).strip()
            qs = u"match (n) where (n.typeName=\"%s\") set n:%s" % (typeName, typeName)
            logger.debug(u"Label :" + qs)
            query = self.query(qs)

            if typeName.find(u"Relationship") != -1:
                qs = u"match (n) where (n.typeName=\"%s\") set n:Relation" % (typeName)
                logger.debug(u"HyperEdge :" + qs)
                query = self.query(qs)

            elif typeName.find(u"Business") != -1:
                qs = u"match (n) where (n.typeName=\"%s\") set n:Business" % (typeName)
                logger.info(u"HyperEdge :" + qs)
                query = self.query(qs)

            elif typeName.find(u"Application") != -1:
                qs = u"match (n) where (n.typeName=\"%s\") set n:Application" % (typeName)
                logger.debug(u"HyperEdge :" + qs)
                query = self.query(qs)

    def createIndices(self):
        for t in self.labelDict:
            try:
                typeName = self.labelDict[t].translate(None, self.delchars).strip()
                qs = u"CREATE INDEX ON :%s (name)" % (typeName)
                #qs = "match (n) where (n.typeName=\"%s\") set n:%s" % (typeName, typeName)
                logger.debug(u"Label :" + qs)
                query = neo4j.CypherQuery(self.graph, qs)
                query.execute().data
            except:
                em = format_exc()
                logger.warn(u"Warning: %s" % (em))

    def dropIndices(self):
        for t in self.labelDict:
            try:
                typeName = self.labelDict[t].translate(None, self.delchars).strip()
                qs = u"DROP INDEX ON :%s (name)" % (typeName)
                #qs = "match (n) where (n.typeName=\"%s\") set n:%s" % (typeName, typeName)
                logger.debug(u"Label :" + qs)
                query = neo4j.CypherQuery(self.graph, qs)
                query.execute().data
            except:
                em = format_exc()
                logger.warn(u"Warning: %s" % (em))

    def addNode(self, concept):

        prop = concept.getProperties()

        if len(prop) != 0:
            ps = ""
            for kk, vv in prop.items():
                if (vv != None and len(vv) > 0) and (kk != None and len(kk) > 0):
                    k = self._cleanString(kk)
                    v = self._cleanString(vv)

                    logger.debug(u"%s : %s" % (k, v))
                    ps = ps + u" %s : \"%s\", " % (k, v)

            ps = ps[:-2] # remove the last comma

            logger.debug(u"ps : %s" % ps)

            if len(ps) == 0:
                qs = u"MERGE (n {name:\"%s\", count:%d, typeName:\"%s\"})" % (concept.name, concept.count, concept.typeName)
            else:
                qs = u"MERGE (n {name:\"%s\", %s, count:%d, typeName:\"%s\"})" % (concept.name, ps, concept.count, concept.typeName)
        else:
            qs = u"MERGE (n {name:\"%s\", count:%d, typeName:\"%s\"})" % (concept.name, concept.count, concept.typeName)

        logger.debug(u"Node Query : '%s'" % qs)

        if self.batches == True:
            bqs = qs + " ; "
            self.batch.append_cypher(bqs)
        else:
            query = neo4j.CypherQuery(self.graph, qs)
            return query.execute().data
        
    def addEdge (self, parentConcept, childConcept, type=None):

        if type!=None:
            typeName = type
        else:
            typeName = childConcept.typeName

        qs0 = u"match "
        qs1 = u"(n {name : \"%s\", typeName:\"%s\"}), " % (parentConcept.name, parentConcept.typeName)
        logger.debug(u"query1 %s" % qs1)

        qs2 = u"(m {name : \"%s\", typeName:\"%s\"}) " % (childConcept.name, childConcept.typeName)
        logger.debug(u"query2 %s" % qs2)

        qs3 = u"merge (n)-[r:%s {typeName:\"%s\"}]->(m)" % (typeName, typeName)
        logger.debug(u"query3 %s" % qs3)

        qs = qs0 + qs1 + qs2 + qs3

        logger.debug(u"Edge Query .%s." % qs)

        if self.batches == True:
            self.batch.append_cypher(qs)
        else:
            query = neo4j.CypherQuery(self.graph, qs)
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
        self.G=nx.Graph()
        self.layout=nx.spring_layout
        if filename == None:
            filename = gmlFile
        self.filename = filename
        logger.debug("GML saved to :" + self.filename)

    def clearGraphDB(self):
        self.G=nx.Graph()

    def saveGraph(self, filename=None):
        if filename == None:
            filename = os.getcwd() + os.sep + gmlFile
        logger.debug(str(self.G.nodes(data=True)))
        nx.write_gml(self.G, filename)

    def addNode(self, concept):
        return self.G.add_node(concept.name, count=concept.count, typeName=concept.typeName)

    def addEdge (self, parentConcept, childConcept, type=None):
        if type!=None:
            typeName = type
        else:
            typeName = childConcept.typeName

        return self.G.add_edge(parentConcept.name, childConcept.name)

    def saveGraphPajek(self, filename=None):
        if filename == None:
            filename = "concept.net"
        nx.write_pajek(self.G,filename)
        
    def drawGraph(self, GML_ONLY=True, filename=None):
        if filename == None:
            filename = imageFile
        logger.debug(str(self.G.nodes(data=True)))

        #nx.write_pajek(self.G,"people.paj")
        #nx.write_gml(self.G,"people.gml")
        #nx.write_graphml(self.G,"people2.gml")

        if GML_ONLY == True:
            nx.write_gml(self.G, self.filename)
        else:
            pos=nx.spring_layout(self.G,iterations=500)
            nx.draw(self.G, pos, node_size=200,cmap=plt.cm.Blues, with_labels=True)
            plt.show()

    def drawSocialGraph(self):
        graph = self.G
        nx.draw_graphviz(graph,
                 node_size = [16 * graph.degree(n) for n in graph],
                 node_color = [graph.depth[n] for n in graph],
                 with_labels = False)
        plt.show()

#
# PatternGraph
#
class PatternGraph(ConceptGraph):
    g = None

    def __init__(self, homeDir=None):   

        if homeDir == None:
            homeDir = os.curdir
            
        self.homeDir = homeDir + os.sep + 'html'
        
        if not os.path.exists(self.homeDir):
            os.makedirs(self.homeDir)
            
        self.g = Graph()

    def addNode(self, n):
        self.g.add_node(n.name)

    def addEdge(self, p, c, type=None):
        if type!=None:
            typeName = type
        else:
            typeName = c.typeName

        self.g.add_edge(p.name, c.name, stroke=(0,0,0,0.75)) # R,G,B,A
    
    def exportGraph(self, title="Pattern Graph"):
        logger.debug("exportGraph")
        
        logger.info("Graph Size: %d" % self.g.__len__())
        
        k = self.subGraph()
        
        # Iterate through a list of unconnected subgraphs
        if len(k) > 5:
            klimit = 5
        else:
            klimit = len(k)
            
        for i in range(0, klimit):
            logger.debug("Graph[%d]=%d" % (i, len(k[i])))
            newDir = self.homeDir + os.sep + "graph" + str(i)
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
            i = i + 1
            n.fill = (0, 0.5, 1, 0.75 * n.weight)
            logger.debug("i:%d=%s" % (i, n))
            newGraph.add_node(n.id)
            logger.debug("edges : %s" % n.edges)
    
            for e in n.edges:
                logger.debug("edge1 : %s, edge2 : %s" % (e.node1.id, e.node2.id))
                if e.node1.id == n.id:
                    newGraph.add_node(e.node2.id)
                else:
                    newGraph.add_node(e.node1.id)
                newGraph.add_edge(e.node1.id, e.node2.id, stroke=(0,0,0,0.75))
        
        h = newGraph.split()
        
        return h

#
# GraphVizGraph
#
class GraphVizGraph(ConceptGraph):
    g = None

    def __init__(self):
        self.g = pgv.AGraph(directed=True,strict=True,rankdir='LR')

        #
        # Hack to get GraphViz to work
        #
        os.environ[u'PATH'] = u"%s:/opt/local/bin" % os.environ[u'PATH']

    def addNode(self, n, color="black", shape="box"):
        self.g.add_node(n.name, color=color, shape=shape)

    def addEdge(self, p, c, color='green'):
        self.g.add_edge(p.name, c.name, color=color)

    def exportGraph(self, filename="example.png"):
        logger.debug("exportGraph")

        # adjust a graph parameter
        self.g.graph_attr['epsilon']='0.001'
        logger.debug(self.g.string()) # print dot file to standard output
        self.g.layout('dot') # layout with dot
        self.g.draw(filename) # write to file
