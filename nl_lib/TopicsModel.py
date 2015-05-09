#!/usr/bin/env python
#
# Concept Class for NLP
#
__VERSION__ = 0.1
__author__ = u'morrj140'

import os
import sys

from gensim import corpora, models, similarities
from gensim.models import lsimodel

from nl_lib.Logger import *
logger = setupLogging(__name__)
logger.setLevel(INFO)

from nl_lib.Concepts import Concepts
#
# TopicModel to analyze topic concepts via Gensim
#
class TopicsModel(object):
    dictFile       = None
    corpusFile     = None
    lsiFile        = None
    topicsFile     = None
    indexFile      = None
    documentTopics = None

    dictFilename   = u"Dictionary.dict"
    corpusFilename = u"corpus.mm"
    lsiFilename    = u"model.lsi"
    indexFilename  = u"topic.index"
    topicsFileneme = u"topicsDict.p"

    texts = None

    # Compute similarity between documents / projects
    similarityThreshold = 0.95

    def __init__(self, directory=None, st=None):

        if directory is None:
            directory = os.getcwd() + os.sep

        if st is not None:
            self.similarityThreshold = st
            
        self.corpusFile = directory + self.corpusFilename
        self.lsiFile = directory + self.lsiFilename
        self.indexFile = directory + self.indexFilename
        self.dictFile  = directory + self.dictFilename
        self.topicsFile  = directory + self.topicsFileneme

    # def __iter__(self):
    #    for line in open('mycorpus.txt'):
    #        # assume there's one document per line, tokens separated by whitespace
    #        yield dictionary.doc2bow(line.lower().split())

    def saveTopics(self, topics):
        wordConcepts = Concepts(u"TopicConcepts", u"Topics")
        for topic in topics:
            logger.debug(u"Topic:" + topic[0])
            w = wordConcepts.addConceptKeyType(topic[0], u"Topic")
            w.count = topic[1]
        Concepts.saveConcepts(wordConcepts, self.topicsFile)
        return wordConcepts

    def saveDictionary(self):
        if (self.dictionary is not None):
            self.dictionary.save(self.dictFile)

    def loadDictionary(self):
        if (os.path.isfile(self.dictFile)):
            return corpora.Dictionary.load(self.dictFile)

    def saveCorpus(self):
        if (self.corpus is not None):
            corpora.MmCorpus.serialize(self.corpusFile, self.corpus)

    def loadCorpus(self):
        if (os.path.isfile(self.corpusFile)):
            self.corpus = corpora.MmCorpus(self.corpusFile)
            return self.corpus

    def saveLSI(self):
        self.lsi.save(self.lsiFile)

    def loadLSI(self):
        self.lsi = models.LsiModel.load(self.lsiFile)
        return self.lsi

    def logTexts(self, texts):
        for text in texts:
            logger.info(u"Text[" + str(texts.index(text)) + u"] :  " + text)

    def logTopics(self, topics):

        if topics is None or len(topics) == 0:
            logger.error(u"Nothing to log!")
            return None
        l = sorted(topics, key=lambda c: abs(c[1]), reverse=True)
        for topic in l:
            logger.info(u"Topic[" + str(topic[0]) + u"]=" + str(topic[1]))

    @staticmethod
    def convertMetric(metric):
        c = metric
        d = float(c)
        return int(d * 100.0)

    def computeTopics(self, texts, nt=50, nw=5):
        self.texts = texts

        if texts is None or len(texts) == 0:
            logger.error(u"No texts to use!")
            return None

        # test set
        self.dictionary = corpora.Dictionary(texts)

        # training set
        self.corpus = [self.dictionary.doc2bow(text) for text in texts]

        # logger.info("corpus ready")
        # for c1 in self.corpus:
        #    for c2 in c1:
        #       logger.info("word: %s  count:%s  index:%s" % (self.dictionary[c2[0]], c2[1], c2[0]))

        tfidf = models.TfidfModel(self.corpus)
        logger.debug(u"tfidf: " + str(tfidf))

        corpus_tfidf = tfidf[self.corpus]
        logger.debug(u"corpus_tfidf: " + str(corpus_tfidf))

        # I can print out the topics for LSI
        self.lsi = lsimodel.LsiModel(corpus_tfidf, id2word=self.dictionary, num_topics=nt)
        logger.debug(u"LSI Complete")
        corpus_lsi = self.lsi[self.corpus]

        logger.debug(u"lsi.print_topics: " + str(self.lsi.print_topics))

        count = 1
        topics = list()
        words = list()

        self.saveLSI()
        self.saveCorpus()
        self.saveDictionary()

        lsiList = self.lsi.print_topics(num_topics=nt, num_words=nw)

        tp = dict()

        for top in lsiList:
            logger.debug(u"Topic [" + str(lsiList.index(top)) + u"] " + str(top))

            for wordcluster in top.split(u" +"):
                key = wordcluster.split(u"*")[1].lower().strip(u"\"")
                value = TopicsModel.convertMetric(wordcluster.split(u"*")[0])

                if key in tp:
                    tp[key] += abs(value)
                else:
                    tp[key] = abs(value)

        return tp.items()

    def computeSimilar(self, j, documentsList, threshold=0.98):

        doc = documentsList[j]

        vec_bow = self.dictionary.doc2bow(doc)

        # convert the query to LSI space
        vec_lsi = self.lsi[vec_bow]
        logger.debug(u"vec_lsi: %s" % (vec_lsi))

        self.index = similarities.MatrixSimilarity(self.lsi[self.corpus])
        # self.index.save(self.index)

        # perform a similarity query against the corpus
        sims = self.index[vec_lsi]

        logger.debug(u"len       : %s" % (sims))
        logger.debug(u"similarity: %s" % (sims))
        logger.debug(u"type      : %s" % (type(sims)))
        logger.debug(u"shape     : %s" % (sims.shape))

        simsList = sims.tolist()
        # simsList = list(enumerate(sims))

        logger.debug(u"len       : %s" % (len(simsList)))
        logger.debug(u"similarity: %s" % (simsList))
        logger.debug(u"type      : %s" % (type(simsList)))

        documentSimilarity = list()

        for i in range(0, len(simsList)-1):
            if (simsList[i] > threshold) and (documentsList[j] != documentsList[i])  :
                logger.debug(u"Document     : %s" % (documentsList[j]))
                logger.debug(u"Similar[%s]: %s" % (documentsList[i], simsList[i]))

                sl = list()
                sl.append(str(simsList[i]))
                sl.append(documentsList[j])
                sl.append(documentsList[i])
                documentSimilarity.append(sl)

        logger.debug(u"Document Similarity List %s" % (documentSimilarity))

        return documentSimilarity

    def loadWords(self, concepts):
        documents = list()
        texts = list()

        wordcount = 0

        # Iterate through the Concepts
        logger.debug(u"Concept Name:" + unicode(concepts.name))

        pc = concepts.getConcepts()
        for p in pc.values():
            logger.debug(u"Concept: %s" % unicode(p.name))

            # Iterate through the Words
            wc = p.getConcepts()
            for w in wc.values():
                logger.debug(u"Word: %s" % unicode(w.name))
                texts.append(w.name)
                wordcount += 1

            documents.append(texts)
            texts = list()

        return documents, wordcount
    
    def loadConceptsWords(self, concepts, delim=u" "):
        documents = list()
        texts = list()

        wordcount = 0

        # Iterate through the Concepts
        logger.debug(u"Concept Name:" + concepts.name)

        for document in concepts.getConcepts().values():
            logger.debug(u"Doc: %s" % document.name)

            for sentence in document.getConcepts().values():
                logger.debug(u"  sent: %s" % sentence.name)

                for word in sentence.name.split(delim):
                    if len(word) > 1:
                        logger.debug(u"    Word: %s" % word)
                        texts.append(word.lower().strip())
                        wordcount += 1

            documents.append(texts)
            texts = list()

        return documents, wordcount
