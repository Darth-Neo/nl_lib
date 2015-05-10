#!/usr/bin/env python
#
# Concept Class for NLP
#
import re
import urllib

__VERSION__ = 0.1
__author__ = 'morrj140'

page = u'https://hidemyass.com/proxy-list/search-225734'
pass1 = re.compile("\&lt;td\&gt;\&lt;span\&gt;.*\..*\..*\..*\&lt;/span\&gt;\&lt;/td\&gt;\t\n.*\&lt;td\&gt;\n.*")
pass2 = re.compile("\d+")


def listHideMe():
    chunkList = []
    ipList = []

    for chunk in pass1.findall(urllib.urlopen(page).read(), re.I):
        chunkList.append(chunk)

    for chunks in chunkList:
        chunks = re.sub("""&lt;span style=\"display:none\"&gt;\d+&lt;/span&gt;""", '', chunks)
        chunks = re.sub("""&lt;div style=\"display:none\"&gt;\d+&lt;/div&gt;""", '', chunks)
        chunks = re.sub("""\"\d+\"""", '', chunks)

    for ippart in pass2.findall(chunks):
        ipList.append(ippart)

    for i in ipList:
        print (i)
 
if __name__ == '__main__':
    listHideMe()
