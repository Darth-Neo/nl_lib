import os
import pytest
from nl_lib.Logger import *
logger = setupLogging(__name__)
logger.setLevel(INFO)

__author__ = u'james.morris'

if __name__ == u"__main__":
    lib = u"%s%s%s" % (os.getcwd(), os.sep, u"nl_lib")
    os.chdir(lib)

    # options in setup.cfg
    pytest.main()
