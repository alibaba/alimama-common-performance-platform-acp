#coding=utf-8
import sys
import time
sys.path.append("..")
from task.task import *

target = ""
qps = "150"
source = "acp_jobid"
query_path = "testcase"
query_type = "11"
option = "{}"
task1 = Task.create_task(target, qps, source, query_path, query_type, option)
