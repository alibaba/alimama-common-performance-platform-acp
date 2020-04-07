import os
import sys
from lib.python.servicelib import *
from model.AcpTask import AcpTask
import json
#import traceback
if __name__ == '__main__':
    try:
       from model.conf.init_database import session
       tasks = session.query(AcpTask).all()
       retList = []
       for task in tasks:
           unit={}
           unit['id'] = task.id
           unit['timestamp'] = task.timestamp
           unit['taskid'] = task.taskid
           unit['acpid'] = task.acpid
           unit['target'] = task.target
           unit['query'] = task.query
           unit['qps'] = task.qps
           unit['protocol'] = task.protocol
           unit['source'] = task.source
           unit['option_str'] = task.option_str
           unit['owner'] = task.owner
           unit['json_conf'] = task.json_conf
           retList.append(unit)
       print json.dumps(retList)
    except Exception,e:
       print str(e)
#       print traceback.format_exc()
