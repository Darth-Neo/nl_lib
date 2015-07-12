# -*- coding: utf-8 -*-

# #!/usr/bin/python
#
# nl_lib Testing
#
__author__ = u'morrj140'
__VERSION__ = u'0.2'

import shutil
import pytest

from test_Constants import *

from Logger import *
logger = setupLogging(__name__)
logger.setLevel(INFO)

from Constants import *
from Concepts import Concepts
from ConceptGraph import PatternGraph, GraphVizGraph, NetworkXGraph, Neo4JGraph

#
# Hack to get GraphViz to work
#
os.environ[u'PATH'] = u"%s:/opt/local/bin" % os.environ[u'PATH']

@pytest.fixture(scope="module")
def cleandir():
    cwd = os.getcwd()

    listFiles = list()
    listFiles.append(exportFileTest)
    listFiles.append(exportFileImageTest)
    listFiles.append(exportFileGMLTest)

    for lf in listFiles:
        ftr = cwd + os.sep + u"test" + os.sep + lf

        if os.path.exists(ftr):
            logger.info(u"remove : %s" % ftr)
            os.remove(ftr)

@pytest.mark.ConceptsGraph
def test_PatternGraph(cleandir):

    if __name__ == u"__main__":
        cleandir()

    try:
        shutil.rmtree(testHomeDir)
    except:
        pass

    assert (os.path.isdir(testHomeDir) is False)
    assert (os.path.isfile(conceptsTest) is True)
    concepts = Concepts.loadConcepts(conceptsTest)

    graph = PatternGraph(testDir)

    logger.info(u"Adding %s nodes the graph ..." % type(graph))
    graph.addGraphNodes(concepts)

    logger.info(u"Adding %s edges the graph ..." % type(graph))
    graph.addGraphEdges(concepts)

    logger.info(u"Exporting Graph")
    graph.exportGraph()

    assert (os.path.isdir(testHomeDir) is True)

@pytest.mark.ConceptsGraph
def test_NetworkXGraph(cleandir):

    if __name__ == u"__main__":
        cleandir()

    assert (os.path.isfile(conceptsTest) is True)
    concepts = Concepts.loadConcepts(conceptsTest)

    graph = NetworkXGraph(filename=exportFileGMLTest)

    logger.info(u"Adding %s nodes the graph ..." % type(graph))
    graph.addGraphNodes(concepts)

    logger.info(u"Adding %s edges the graph ..." % type(graph))
    graph.addGraphEdges(concepts)

    graph.saveGraph(filename=exportFileGMLTest)
    logger.info(u"Saved Graph - %s" % exportFileGMLTest)

    assert (os.path.isfile(exportFileGMLTest) is True)

@pytest.mark.ConceptsGraph
def test_GraphVizGraph(cleandir):

    if __name__ == u"__main__":
        cleandir()

    assert (os.path.isfile(conceptsTest) is True)
    concepts = Concepts.loadConcepts(conceptsTest)

    graph = GraphVizGraph()

    logger.info(u"Adding %s nodes the graph ..." % type(graph))
    graph.addGraphNodes(concepts)

    logger.info(u"Adding %s edges the graph ..." % type(graph))
    graph.addGraphEdges(concepts)

    graph.exportGraph(filename=exportFileImageTest)
    logger.info(u"Saved Graph - %s" % exportFileImageTest)

    assert (os.path.isfile(exportFileImageTest) is True)


@pytest.mark.ConceptsGraph
def test_Neo4JGraph():

    assert (os.path.isfile(conceptsTest) is True)
    concepts = Concepts.loadConcepts(conceptsTest)

    graph = Neo4JGraph(gdb)

    # concepts.logConcepts()

    logger.info(u"Adding %s nodes the graph ..." % type(graph))
    graph.addGraphNodes(concepts)

    logger.info(u"Adding %s edges the graph ..." % type(graph))
    graph.addGraphEdges(concepts)

    qs = u"MATCH (n) RETURN n.typeName, count(n.typeName) as Count order by Count DESC"
    qd = graph.query(qs)

    logger.info(u"Neo4J Counts")

    assert qd is not None


if __name__ == u"__main__":
    test_NetworkXGraph(cleandir)

    test_GraphVizGraph(cleandir)

    test_PatternGraph(cleandir)

    test_Neo4JGraph()