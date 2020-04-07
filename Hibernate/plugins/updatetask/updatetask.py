import os
import sys
from lib.python.servicelib import *
from model.AcpTask import AcpTask
if __name__ == '__main__':
    
    try:
       taskid = getValue("taskid")
       from model.conf.init_database import session
       tasks = session.query(AcpTask).filter(AcpTask.id == taskid).first()
       if tasks != None:
           tasks.option_str="fsdfds"
           session.commit()
       else:
           print "NODATA"
    except Exception,e:
       print e
       print traceback.format_exc()
