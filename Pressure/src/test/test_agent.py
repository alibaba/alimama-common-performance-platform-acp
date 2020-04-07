#coding=utf-8
import sys
import time
sys.path.append("..")
from task.agent import *
from task.task import *

task = Task.get_task("t1498135392228")
agent1 = task.add_agent("11.251.247.139", "11.251.247.139_2", 4000, 1)
agent1.set_qps("150")
#task.add_agent("1.1.1.2", "a12305", 1000, 2)
#task.add_agent([("1.1.1.1", "a10067")])
#task.delete_all_agent()
