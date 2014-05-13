import os
import networkx as nx
import matplotlib.pyplot as plt
from py2neo import neo4j, node, rel
from pattern.graph  import Graph

from nl_lib import Logger
from nl_lib import Constants
from nl_lib import Concepts

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
                logger.info("Keep Node - " + concept.name)
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
        concept.name = concept.name.translate(None, delchars)
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
        logger.info("Neo4j DB @ :" + gdb)

    def clearGraphDB(self):
        query = neo4j.CypherQuery(self.db, "START n=node(*) MATCH n-[r?]-m WITH n, r DELETE n, r")
        query.execute().data

    delchars = ''.join(c for c in map(chr, range(255)) if (not c.isalnum()))

    def setNodeLabels(self):
        for t in self.labelDict:
            try:
                typeName = self.labelDict[t].translate(None, self.delchars).strip()
                qs = "match (n) where (n.typeName=\"" + typeName + "\") set n:" + typeName
                logger.info("Label :" + qs)
                query = neo4j.CypherQuery(self.db, qs)
                query.execute().data
            except:
                logger.error(str(sys.exc_info()[0]))

    def addNode(self, concept):
        return self.db.create(node(name=concept.name, count=concept.count, typeName=concept.typeName))

    def addEdge (self, parentConcept, childConcept):
        return self.db.create(rel(self.nodeDict[childConcept.name][0],
                       (parentConcept.typeName, {"count": parentConcept.count}),
                       self.nodeDict[parentConcept.name][0]))
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
            filename = Constants.gmlFile
        self.filename = filename
        logger.info("GML saved to :" + self.filename)

    def clearGraphDB(self):
        self.G=nx.Graph()

    def saveGraph(self, filename=None):
        if filename == None:
            filename = os.getcwd() + os.sep + Constants.gmlFile
        logger.debug(str(self.G.nodes(data=True)))
        nx.write_gml(self.G, filename)

    def addNode(self, concept):
        return self.G.add_node(concept.name, count=concept.count, typeName=concept.typeName)

    def addEdge (self, parentConcept, childConcept):
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

    def drawEgoGraph(self):
        logger.debug(str(self.G.nodes(data=True)))

        # find node with largest degree
        node_and_degree=self.G.degree()
        (largest_hub,degree)=sorted(node_and_degree.items(),key=itemgetter(1))[-1]

        # Create ego graph of main hub
        hub_ego=nx.ego_graph(self.G,largest_hub)

        # Draw graph
        pos=nx.spring_layout(hub_ego)
        nx.draw(hub_ego,pos,node_color='b',node_size=50,with_labels=True)

        # Draw ego as large and red
        nx.draw_networkx_nodes(hub_ego,pos,nodelist=[largest_hub],node_size=300,node_color='r')
        plt.savefig('ego_graph.png')
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

    def addEdge(self, p, c):
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
            logger.info("Graph[%d]=%d" % (i, len(k[i])))
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
            logger.info("i:%d=%s" % (i, n))
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
