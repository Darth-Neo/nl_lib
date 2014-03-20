from nl_lib import Logger
logger = Logger.setupLogging(__name__)

from nl_lib import Concepts

def cleanPeople(name):
    r = " "
    for c in name:
        if c.isalpha() or c == ',':
            r += c
            logger.debug("r = %s" % r)
        else:
            r += " "
    return r

def splitPeople(people):
    logger.debug("SplitPeople: " + people)

    pl = people.split(",")
    logger.debug(pl)

    peopleList = list()

    count = len(pl)
    logger.debug("Count = %s" % count)
     
    if count > 1:
        
        while count > 0:
            logger.debug("count: " + str(count))
            lfName = pl[count-2] + "," + pl[count-1]
            lfName = cleanPeople(lfName)
            logger.debug("lfName=" + lfName)
            n = Concepts.Concepts(lfName, "Person")

            peopleList.append(lfName)
            count = count - 2
    
    else:
        result = ''.join([i for i in people if i.isalpha()])
        if len(result) > 0:
            peopleList.append(result)
         
    return peopleList
