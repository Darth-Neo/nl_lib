import os
import sys

from Concepts import Concepts

import Logger
logger = Logger.setupLogging(__name__)
   
if __name__ == "__main__":
    
    #conceptTerm = 'Words'
    conceptTerm = 'Search'

    logger.info("Starting...")
    
    concepts = Concepts("LOG", conceptTerm, load=True)
    
    concepts.logConcepts()

