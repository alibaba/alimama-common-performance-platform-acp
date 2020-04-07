#coding=utf-8
import sys
import time
import json
sys.path.append("..")
from host.host import *

for host in Host.get_all_host():
    host.delete_in_zk()
