#coding=utf-8
import sys
import time
sys.path.append("..")
from host.host import *

#host.get_info_from_zk()
host = Host("3.3.3.3", id=1)
host.create_in_zk()
