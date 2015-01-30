#!/usr/bin/env python
#
# Concept Class for NLP
#
__VERSION__ = 0.1
__author__ = 'morrj140'

import os
import sys
import networkx as nx
import matplotlib.pyplot as plt
from py2neo import neo4j, node, rel
from pattern.graph  import Graph

from nl_lib import Logger
logger = Logger.setupLogging(__name__)

from nl_lib.Constants import *
from nl_lib.Concepts import Concepts

from traceback import format_exc

import pygraphviz as pgv

logger = Logger.setupLogging(__name__)

delchars = ''.join(c for c in map(chr, range(256)) if not c.isalnum())

#
# Base Class - ConceptGraph to export Concepts into Graph
#
class ConceptGraph(object):
    nodeDict = dict()
    labelDict = dict()

    def __init__(self):
        logger.info("ConceptGraph Constructor")

    def isFiltered(self, filterDict, concept):
        if filterDict == None:
            return True

        if filterDict.has_key(concept.typeName):
            logger.debug("Checking Type - " + concept.typeName)
            if concept.name in filterDict[concept.typeName]:
                logger.debug("Keep Node - " + concept.name)
                return True
            else:
                logger.debug("Skip Node - " + concept.name)
                return False
        return True
        
    def addConcepts(self, concept, filterDict=None, depth=2, n=0):
        n = n + 1

        if self.nodeDict.has_key(concept.name):
            logger.debug("Found Node: " + concept.name)
            c = self.nodeDict[concept.name]
        else:
            c = self.addNode(concept)
            logger.debug("Add Node: " + concept.name + ": " + str(c))
            self.nodeDict[concept.name] = c
            concept.urn = c
            self.labelDict[concept.typeName] = concept.typeName

        if (n > depth):
            logger.debug("Reached depth["+ str(depth) + "] = " + str(n))
            return c

        pc = concept.getConcepts()

        for p in pc:
            if self.isFiltered(filterDict, pc[p]):
                self.addConcepts(pc[p], filterDict, depth, n)
                logger.debug("Add Edge: " + concept.name + " - " + concept.typeName + " - " + pc[p].name)
                logger.debug("   Node: " + str(self.nodeDict[concept.name]))
                logger.debug("   Node: " + str(self.nodeDict[pc[p].name]))
                self.addEdge(concept, pc[p])
        return c

    def addConcept(self, concept):
        #concept.name = concept.name.translate(None, delchars)
        if self.nodeDict.has_key(concept.name):
            logger.debug("Found Node: " + concept.name)
            c = self.nodeDict[concept.name]
        else:
            c = self.addNode(concept)
            logger.debug("Add Node: " + concept.name + ": " + str(c))
            self.nodeDict[concept.name] = c
            concept.urn = c
            self.labelDict[concept.typeName] = concept.typeName

#
# Neo4JGraph
#
class Neo4JGraph(ConceptGraph):
    db = None
    gdb = None

    def __init__(self, gdb):
        self.gdb = gdb
        self.db = neo4j.GraphDatabaseService(gdb)
        logger.debug("Neo4j DB @ :" + gdb)

    def clearGraphDB(self):
        query = neo4j.CypherQuery(self.db, "MATCH (n) DELETE n")
        query.execute().data

    def query(self, qs):
        query = neo4j.CypherQuery(self.db, qs)
        return query.execute().data

    delchars = ''.join(c for c in map(chr, range(255)) if (not c.isalnum()))

    def setNodeLabels(self):
        for t in self.labelDict:
            try:
                typeName = self.labelDict[t].translate(None, self.delchars).strip()
                qs = "match (n) where (n.typeName=\"" + typeName + "\") set n:" + typeName
                logger.info("Label :" + qs)
                query = self.query(qs)
                query.execute().data
            except:
                em = format_exc()
                logger.warn("Warning: %s" % (em))

    def createIndices(self):
        for t in self.labelDict:
            try:
                typeName = self.labelDict[t].translate(None, self.delchars).strip()
                qs = "CREATE INDEX ON :%s (name)" % (typeName)
                #qs = "match (n) where (n.typeName=\"%s\") set n:%s" % (typeName, typeName)
                logger.info("Label :" + qs)
                query = neo4j.CypherQuery(self.db, qs)
                query.execute().data
            except:
                em = format_exc()
                logger.warn("Warning: %s" % (em))

    def dropIndices(self):
        for t in self.labelDict:
            try:
                typeName = self.labelDict[t].translate(None, self.delchars).strip()
                qs = "DROP INDEX ON :%s (name)" % (typeName)
                #qs = "match (n) where (n.typeName=\"%s\") set n:%s" % (typeName, typeName)
                logger.info("Label :" + qs)
                query = neo4j.CypherQuery(self.db, qs)
                query.execute().data
            except:
                em = format_exc()
                logger.warn("Warning: %s" % (em))

    def addNode(self, concept):
        qs = "MERGE (n {name:\"%s\", count:%d, typeName:\"%s\"})" % (concept.name, concept.count, concept.typeName)

        logger.debug("Node Query : '%s'" % qs)

        query = neo4j.CypherQuery(self.db, qs)

        return query.execute().data

        #return self.db.create(node(name=concept.name, count=concept.count, typeName=concept.typeName))
        
    def addEdge (self, parentConcept, childConcept, type=None):
        if type!=None:
            typeName = type
        else:
            typeName = childConcept.typeName

        qs0 = "match "
        qs1 = "(n {name : \"%s\", typeName:\"%s\"}), " % (parentConcept.name, parentConcept.typeName)
        logger.debug("query1 %s" % qs1)

        qs2 = "(m {name : \"%s\", typeName:\"%s\"}) " % (childConcept.name, childConcept.typeName)
        logger.debug("query2 %s" % qs2)

        qs3 = "merge (n)-[r:%s {typeName:\"%s\"}]->(m)" % (typeName, typeName)
        logger.debug("query3 %s" % qs3)

        qs = qs0 + qs1 + qs2 + qs3

        logger.debug("Edge Query %s" % qs)

        query = neo4j.CypherQuery(self.db, qs)

        return query.execute().data

        #return self.db.create(rel(self.nodeDict[childConcept.name][0],
        #               (typeName, {"count": parentConcept.count}),
        #               self.nodeDict[parentConcept.name][0]))
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
        
    def drawGraph(self, filename=None):
        if filename == None:
            filename = imageFile
        logger.debug(str(self.G.nodes(data=True)))

        #nx.write_pajek(self.G,"people.paj")
        #nx.write_gml(self.G,"people.gml")
        #nx.write_graphml(self.G,"people2.gml")

        nx.write_gml(self.G, self.filename)

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
