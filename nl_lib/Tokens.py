#!/usr/bin/env python
#
# Concept Class for NLP
#
import nltk
from pattern.en import parse
from pattern.en import parsetree
from pattern.en import wordnet
from pattern.en import Sentence

from Logger import *
logger = setupLogging(__name__)
logger.setLevel(DEBUG)

from Constants import *


__VERSION__ = u'0.1'
__author__ = u'morrj140'


def sentenceTokensPattern(sentence, projectsConcepts, wordsConcepts):
    stop.append(u"The")
    stop.append(u"This")
    stop.append(u"We")
    stop.append(u"Currently")
    cleanSentence = ' '.join([word for word in sentence.split() if word not in stop])
  
    pt = parsetree(cleanSentence, relations=True, lemmata=True)

    logger.debug(u"s: .%s." % pt)
    
    for sentence in pt:
        logger.debug(u"sentence: .%s." % sentence)

        try:
            if len(sentences.subjects) > 0:
                subject = sentence.subjects[0]
                verb = sentence.verbs[0]
                predicate = sentence.objects[0]

                logger.info(u"%s.%s(%s)" % (subject, verb, predicate))

                # Add concept to words
                w = wordsConcepts.addConceptKeyType(subject, verb)
                w.addConceptKeyType(projectsConcepts.name, u"Project")
            else:
                addChunks(sentence, projectsConcepts, wordsConcepts)
        except:
            pass


def sentenceTokensNLTK(sentence, projectsConcepts, wordsConcepts):
    logger.debug(u"Sentence: " + sentence)
        
    for word, pos in nltk.pos_tag(nltk.wordpunct_tokenize(sentence)):
        logger.debug(u"Word: " + word + u" POS: " + pos)

        if pos == u"NNS":
            # Add word concept to project
            w = projectsConcepts.addConceptKeyType(word, u"Word")
            w.addConceptKeyType(pos, u"POS")

            # Add concept to words
            w = wordsConcepts.addConceptKeyType(word, u"Word")
            w.addConceptKeyType(pos, u"POS")

            # syns = wn.synsets(word)
            # for s in syns:
            #   logger.debug("definition:" + s.definition)

            #   logger.debug("examples:")
            #   for b in s.examples:
            #      logger.debug(b)
                
            #   for l in s.lemmas:
            #      logger.debug("Synonym: " + l.name)
            #      wl = wordConcepts.addConcept(l.name, "Synonym")


def sentenceTokensPatternChunks(sentence, projectsConcepts, wordsConcepts):
    sent = Sentence(parse(sentence))
    for chunk in sent.chunks:
        wordChunk = chunk.string

        if chunk.type == u"NP":
            logger.debug(u"NP: .%s." % (wordChunk))
            
            # Add word concept to project
            d = projectsConcepts.addConceptKeyType(u"Descriptions", u"Words")
            w = d.addConceptKeyType(wordChunk, u"Word")
            w.addConceptKeyType(chunk.type, u"POS")

            # Add concept to words
            w = wordsConcepts.addConceptKeyType(wordChunk, u"Word")
            w.addConceptKeyType(chunk.type, u"POS")
            w.addConceptKeyType(projectsConcepts.name, u"Project")


def synsetsWordNet(word):
    s = wordnet.synsets(word)[0]

    logger.info(u"Definition: %s" % s.gloss)
    logger.info(u" Synonyms : %s" % s.synonyms)
    logger.info(u" Hypernyms: %s" % s.hypernyms())
    logger.info(u" Hyponyms : %s" % s.hyponyms())
    logger.info(u" Holonyms : %s" % s.holonyms())
    logger.info(u" Meronyms : %s" % s.meronyms())
