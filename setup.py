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
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
    ],

    # What does your project relate to?
    keywords='nlp setuptools development',

    # List run-time dependencies here.  These will be installed by pip when your
    # project is installed.
    install_requires=['nltk', 'pattern', 'gensim', 'networkx', 'matplotlib', 'pywordcloud', 'wordcloud',
                      'numpy', 'py2neo', 'pygraphviz', 'pytest', 'pytest-cov', 'python-docx', 'python-pptx'],)


