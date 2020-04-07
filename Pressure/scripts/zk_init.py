#coding=utf-8
import sys
import os
path = os.path.split(os.path.realpath(__file__))[0]
sys.path.append(path+"/../src")
from common.zk import *
from common.util import *

zk = ZK(CONF.zk_address)
root = zk.get_node(CONF.root)
if root:
    root.delete()
zk.create_node(CONF.task_path)
host = zk.create_node(CONF.host_path)
host.add_child("list")
lastSeqNode = host.add_child("lastSeq")
lastSeqNode.set_value("1")
