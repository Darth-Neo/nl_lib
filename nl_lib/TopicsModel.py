import os
import sys

from gensim import corpora, models, similarities
from gensim.models import lsimodel

from nl_lib import Logger, Concepts, Tokens
logger = Logger.setupLogging(__name__)

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

    dictFilename   = "Dictionary.dict"
    corpusFilename = "corpus.mm"
    lsiFilename    = "model.lsi"
    indexFilename  = "topic.index"
    topicsFileneme = "topicsDict.p"

    texts = None

    # Compute similarity between documents / projects
    similarityThreshold = 0.95

    delchars = ''.join(c for c in map(chr, range(255)) if (not c.isalnum() and c != ' '))

    def __init__(self, directory=None, st=None):

        if directory == None:
            directory = os.getcwd() + os.sep

        if st != None:
            self.similarityThreshold = st
            
        self.corpusFile = directory + self.corpusFilename
        self.lsiFile = directory + self.lsiFilename
        self.indexFile = directory + self.indexFilename
        self.dictFile  = directory + self.dictFilename
        self.topicsFile  = directory + self.topicsFileneme

    #def __iter__(self):
    #    for line in open('mycorpus.txt'):
    #        # assume there's one document per line, tokens separated by whitespace
    #        yield dictionary.doc2bow(line.lower().split())

    def saveTopics(self, topics):
        wordConcepts = Concepts.Concepts("TopicConcepts", "Topics")
        for topic in topics:
            logger.debug("Topic:" + topic[0])
            w = wordConcepts.addConceptKeyType(topic[0], "Topic")
            w.count = topic[1]
        Concepts.Concepts.saveConcepts(wordConcepts, self.topicsFile)
        return wordConcepts

    def saveDictionary(self):
        if (self.dictionary != None) :
            self.dictionary.save(self.dictFile)

    def loadDictionary(self):
        if (os.path.isfile(self.dictFile)) :
            return corpora.Dictionary.load(self.dictFile)

    def saveCorpus(self):
        if (self.corpus != None) :
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
           logger.info("Text[" + str(texts.index(text)) + "] :  " + text)

    def logTopics(self, topics):

        if topics == None or len(topics) == 0:
            logger.error("Nothing to log!")
            return None
        l = sorted(topics, key=lambda c: abs(c[1]), reverse=True)
        for topic in l:
            logger.info("Topic[" + str(topic[0]) + "]=" + str(topic[1]))

    @staticmethod
    def convertMetric(metric):
        c = metric
        d = float(c)
        return int(d * 100.0)

    def computeTopics(self, texts, nt=50, nw=5):
        self.texts = texts

        if texts == None or len(texts) == 0:
            logger.error("No texts to use!")
            return None

        # test set
        self.dictionary = corpora.Dictionary(texts)

        # training set
        self.corpus = [self.dictionary.doc2bow(text) for text in texts]

        #logger.info("corpus ready")
        #for c1 in self.corpus:
        #    for c2 in c1:
        #       logger.info("word: %s  count:%s  index:%s" % (self.dictionary[c2[0]], c2[1], c2[0]))

        tfidf = models.TfidfModel(self.corpus)
        logger.debug("tfidf: " + str(tfidf))

        corpus_tfidf = tfidf[self.corpus]
        logger.debug("corpus_tfidf: " + str(corpus_tfidf))

        # I can print out the topics for LSI
        self.lsi = lsimodel.LsiModel(corpus_tfidf, id2word=self.dictionary, num_topics=nt)
        logger.debug("LSI Complete")
        corpus_lsi = self.lsi[self.corpus]

        logger.debug("lsi.print_topics: " + str(self.lsi.print_topics))

        count = 1
        topics = list()
        words = list()

        self.saveLSI()
        self.saveCorpus()
        self.saveDictionary()

        lsiList = self.lsi.print_topics(num_topics=nt, num_words=nw)

        tp = dict()

        for top in lsiList:
          logger.debug("Topic [" + str(lsiList.index(top)) + "] " + str(top))

          for wordcluster in top.split(" +"):
              key = wordcluster.split("*")[1].lower().strip("\"")
              value = TopicsModel.convertMetric(wordcluster.split("*")[0])

              if tp.has_key(key):
                tp[key] += abs(value)
              else:
                tp[key] = abs(value)

        return tp.items()

    def computeSimilar(self, j, documentsList, threshold = 0.98):

        doc = documentsList[j]

        vec_bow = self.dictionary.doc2bow(doc)

        # convert the query to LSI space
        vec_lsi = self.lsi[vec_bow]
        logger.debug("vec_lsi: %s" % (vec_lsi))

        self.index = similarities.MatrixSimilarity(self.lsi[self.corpus])
        #self.index.save(self.index)

        # perform a similarity query against the corpus
        sims = self.index[vec_lsi]

        logger.debug("len       : %s" % (sims))
        logger.debug("similarity: %s" % (sims))
        logger.debug("type      : %s" % (type(sims)))
        logger.debug("shape     : %s" % (sims.shape))

        simsList = sims.tolist()
        #simsList = list(enumerate(sims))

        logger.debug("len       : %s" % (len(simsList)))
        logger.debug("similarity: %s" % (simsList))
        logger.debug("type      : %s" % (type(simsList)))

        documentSimilarity = list()

        for i in range(0, len(simsList)-1):
            if (simsList[i] > threshold) and (documentsList[j] != documentsList[i])  :
                logger.debug("Document     : %s" % (documentsList[j]))
                logger.debug("Similar[%s]: %s" % (documentsList[i], simsList[i]))

                sl = list()
                sl.append(str(simsList[i]))
                sl.append(documentsList[j])
                sl.append(documentsList[i])
                documentSimilarity.append(sl)

        logger.debug("Document Similarity List %s" % (documentSimilarity))

        return documentSimilarity

    def loadWords(self, concepts):
        documents = list()
        texts = list()

        wordcount = 0

        # Iterate through the Concepts
        logger.debug("Concept Name:" + concepts.name)

        pc = concepts.getConcepts()
        for p in pc.values():
            logger.debug("Concept: %s" % p.name)

            # Iterate through the Words
            wc = p.getConcepts()
            for w in wc.values():
                logger.debug("Word: %s" % w.name)
                texts.append(w.name)
                wordcount += 1

            documents.append(texts)
            texts = list()

        return documents, wordcount
    
    def loadConceptsWords(self, concepts, delim=" "):
        documents = list()
        texts = list()

        wordcount = 0

        # Iterate through the Concepts
        logger.debug("Concept Name:" + concepts.name)

        for document in concepts.getConcepts().values():
            logger.debug("Doc: %s" % document.name)

            for sentence in document.getConcepts().values():
                logger.debug("  sent: %s" % sentence.name)

                for word in sentence.name.split(delim):
                    if len(word) > 1:
                        logger.debug("    Word: %s" % word)
                        texts.append(word.lower().strip())
                        wordcount += 1

            documents.append(texts)
            texts = list()

        return documents, wordcount
