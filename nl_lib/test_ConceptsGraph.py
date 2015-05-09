# -*- coding: utf-8 -*-

# #!/usr/bin/python
#
# nl_lib Testing
#
__author__ = u'morrj140'
__VERSION__ = u'0.2'

from nl_lib.Logger import *
logger = setupLogging(__name__)
logger.setLevel(INFO)

from Constants import *
from Concepts import Concepts
from ConceptGraph import Neo4JGraph, PatternGraph, GraphVizGraph, NetworkXGraph

import pytest
from test_Constants import *

import shutil

#
# Hack to get GraphViz to work
#
os.environ[u'PATH'] = u"%s:/opt/local/bin" % os.environ[u'PATH']


def _addGraphNodes(graph, concepts, n=0):
    n += 1

    for c in concepts.getConcepts().values():
        logger.debug(u"%d : %d Node c : %s:%s" % (n, len(c.getConcepts()), c.name, c.typeName))

        graph.addConcept(c)

        _addGraphNodes(graph, c, n)


def _addGraphEdges(graph, concepts, n=0):
    n += 1

    graph.addConcept(concepts)

    for c in concepts.getConcepts().values():

        logger.debug(u"%d : %d %s c : %s:%s" % (n, len(c.getConcepts()), concepts.name, c.name, c.typeName))

        graph.addConcept(c)

        graph.addEdge(concepts, c)

        if len(c.getConcepts()) != 0:
            _addGraphEdges(graph, c, n)

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
    _addGraphNodes(graph, concepts)

    logger.info(u"Adding %s edges the graph ..." % type(graph))
    _addGraphEdges(graph, concepts)

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
    _addGraphNodes(graph, concepts)

    logger.info(u"Adding %s edges the graph ..." % type(graph))
    _addGraphEdges(graph, concepts)

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
    _addGraphNodes(graph, concepts)

    logger.info(u"Adding %s edges the graph ..." % type(graph))
    _addGraphEdges(graph, concepts)

    graph.exportGraph(filename=exportFileImageTest)
    logger.info(u"Saved Graph - %s" % exportFileImageTest)

    assert (os.path.isfile(exportFileImageTest) is True)

if __name__ == u"__main__":
    test_NetworkXGraph(cleandir)
    test_GraphVizGraph(cleandir)
    test_PatternGraph(cleandir)