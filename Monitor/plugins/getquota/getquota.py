
import os
import sys
from lib.python.servicelib import *
import random
if __name__ == '__main__':
    try:
       a = open("/tmp/PIEMON_RET")
       line = a.readlines()
       qps =  line[-1].split("	")[0]
       print qps
    except Exception,e:
       print e
       print traceback.format_exc()
