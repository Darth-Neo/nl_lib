#!/usr/bin/env python
#
# Concept Class for NLP
#
__VERSION__ = '0.2'
__author__ = 'morrj140'

from setuptools import setup, find_packages
import codecs
import os
import re

here = os.path.abspath(os.path.dirname(__file__))

setup(name='nl_lib',
      version=__VERSION__,
      description='Tools for Natural Language Processing',
      url='http://github.com/darth-neo/nl_lib',
      author='Darth Neo',
      author_email='morrisspid.james@gmail.com',
      license='MIT',
      packages=['nl_lib'],
      zip_safe=False,
      
      classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],

    # What does your project relate to?
    keywords='nlp setuptools development',

    # List run-time dependencies here.  These will be installed by pip when your
    # project is installed. Note: installation order is reversed
    install_requires=['nltk==3.0.2', 'Pattern==2.6', 'gensim==0.10.3', 'networkx==1.9.1', 'matplotlib==1.4.3',
                      'pywordcloud==0.2.2', 'py2neo==1.6.4', 'pygraphviz==1.2', 'pytest==2.6.4', 'pytest==2.6.4',
                      'python-docx==0.8.5', 'python-pptx==0.5.7', 'Cython==0.22'],)


