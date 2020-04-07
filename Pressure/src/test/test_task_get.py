#coding=utf-8
import sys
sys.path.append("..")
from task.task import *

for task in Task.get_all_task():
    print task.get_task_info()
