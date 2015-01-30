#!/usr/bin/env python
#
# Concept Testing
#
__VERSION__ = 0.1
__author__ = 'morrj140'

import os
import sys

from nl_lib.Constants import *
from nl_lib.Concepts import Concepts
from nl_lib import Logger
logger = Logger.setupLogging(__name__)
   
if __name__ == "__main__":
    import doctest
    #doctest.testmod()
    doctest.testfile("test_Concepts.txt")