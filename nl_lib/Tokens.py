#!/usr/bin/env python
#
# Concept Class for NLP
#
__VERSION__ = 0.1
__author__ = 'morrj140'

import os
import sys

import nltk
from nltk import tokenize, tag, chunk
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords

from pattern.en import parse
from pattern.en import tag
from pattern.en import parsetree
from pattern.en import wordnet
from pattern.en import Sentence

from nl_lib import Logger, Concepts
logger = Logger.setupLogging(__name__)

def sentenceTokensPattern (sentence, projectsConcepts, wordsConcepts):
    stop.append("The")
    stop.append("This")
    stop.append("We")
    stop.append("Currently")
    cleanSentence = ' '.join([word for word in sentence.split() if word not in stop])
  
    pt = parsetree(cleanSentence, relations=True, lemmata=True)

    logger.debug("s: .%s." % pt)
    
    for sentence in pt:
        logger.debug("sentence: .%s." % sentence)

        try:
            if len(sentences.subjects) > 0:
                subject = sentence.subjects[0]
                verb = sentence.verbs[0]
                predicate = sentence.objects[0]

                logger.info("%s.%s(%s)" % (subject, verb, predicate))

                # Add concept to words
                w = wordsConcepts.addConceptKeyType(subject, verb)
                w.addConceptKeyType(projectsConcepts.name, "Project")
            else:
                addChunks(sentence, projectsConcepts, wordsConcepts)
        except:
            pass

def sentenceTokensNLTK (sentence, projectsConcepts, wordsConcepts):
    logger.debug("Sentence: " + sentence)
        
    for word, pos in nltk.pos_tag(nltk.wordpunct_tokenize(sentence)):
        logger.debug("Word: " + word + " POS: " + pos)

        if pos == "NNS":
            # Add word concept to project
            w = projectsConcepts.addConceptKeyType(word, "Word")
            w.addConceptKeyType(pos, "POS")

            # Add concept to words
            w = wordsConcepts.addConceptKeyType(word, "Word")
            w.addConceptKeyType(pos, "POS")

            #syns = wn.synsets(word)
            #for s in syns:
                #logger.debug("definition:" + s.definition)

                #logger.debug("examples:")
                #for b in s.examples:
                #    logger.debug(b)
                
                #for l in s.lemmas:
                #    logger.debug("Synonym: " + l.name)
                #    wl = wordConcepts.addConcept(l.name, "Synonym")

def sentenceTokensPatternChunks(sentence, projectsConcepts, wordsConcepts):
    sent = Sentence(parse(sentence))
    for chunk in sent.chunks:
        wordChunk = chunk.string

        if chunk.type == "NP":
            logger.debug("NP: .%s." % (wordChunk))
            
            # Add word concept to project
            d = projectsConcepts.addConceptKeyType("Descriptions", "Words")
            w = d.addConceptKeyType(wordChunk, "Word")
            p = w.addConceptKeyType(chunk.type, "POS")

            # Add concept to words
            w = wordsConcepts.addConceptKeyType(wordChunk, "Word")
            w.addConceptKeyType(chunk.type, "POS")
            w.addConceptKeyType(projectsConcepts.name, "Project")

def synsetsWordNet(word):
    s = wordnet.synsets(word)[0]

    logger.info("Definition: %s" % s.gloss)
    logger.info(" Synonyms : %s" % s.synonyms)
    logger.info(" Hypernyms: %s" % s.hypernyms())
    logger.info(" Hyponyms : %s" % s.hyponyms())
    logger.info(" Holonyms : %s" % s.holonyms())
    logger.info(" Meronyms : %s" % s.meronyms())
