#coding=utf-8
import sys
import os
path = os.path.split(os.path.realpath(__file__))[0]
sys.path.append(path+"/../src")
from task.task import *

for task in Task.get_all_task():
    task.set_status("stop")
