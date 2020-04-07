import os
import sys
from lib.python.servicelib import *
from model.AcpTask import AcpTask
if __name__ == '__main__':
    try:
       from model.conf.init_database import session
       task = AcpTask()
       task.timestamp = getValue("timestamp")
       task.taskid = getValue("taskid")
       task.acpid = getValue("acpid")
       task.target = getValue("target")
       task.query = getValue("query")
       task.qps = getValue("qps")
       task.protocol = getValue("protocol")
       task.source = "running"
       task.option_str = getValue("option_str")
       task.owner = getValue("owner")
       task.json_conf = getValue("json_conf")
       session.add(task)
    except Exception,e:
       print e
       print traceback.format_exc()
