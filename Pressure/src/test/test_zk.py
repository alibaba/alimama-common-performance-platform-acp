import sys
sys.path.append("..")
from common.zk import *

zk = ZK("localhost:2181")
root = zk.get_node("/")
acp_node = root.add_child("acp2")
task_node = acp_node.add_child("task")
host_node = acp_node.add_child("host")
task_node.add_child("list")
