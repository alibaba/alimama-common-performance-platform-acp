#coding=utf-8
import time
import os
import signal
import sys
import math
path = os.path.split(os.path.realpath(__file__))[0]
sys.path.append(path+"/..")
from task.task import *
from task.agent import *
from res_manager.res_manager import *
from host.host import *
from common.util import *
import json

import urllib
import urllib2
import traceback
is_stop = False
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def queryAcp(url):
    res = ''
    try:
        req = urllib2.Request(url)
        res_data = urllib2.urlopen(req)
        res = res_data.read()
    except Exception,e:
        CONF.log.error(str(e))
        CONF.log.error(traceback.format_exc())
        res = '-1'
    return res

def start_action(task):
    try:
        print "you can broadcast start action"
    except Exception,e:
        CONF.log.error(str(e))
        CONF.log.error(traceback.format_exc())

def end_action(task):
    try:
        print "you can broadcast  end cation"
    except Exception,e:
        CONF.log.error(str(e))
        CONF.log.error(traceback.format_exc())



        




def report_current_action(task,action):
    print "report @!!!"
    ### common  ###

def get_total_qps(task):
    info = task.get_task_info()
    total_qps = float(info["qps"])
    return total_qps

def get_max_qps(task):
    info = task.get_task_info()
    query_type = info["query_type"]
    max_qps = float(CONF.maxqps[query_type])
    return max_qps

def get_agent_num(task):
    num = len(task.get_all_agent())
    return num

def get_resource_num(task):
    info = task.get_task_info()
    query_type = info["query_type"]
    num = CONF.resource[query_type]
    return num
def term_signal_handler(signum, frame):
    global is_stop
    is_stop = True
def schedule(pid_file):
    global is_stop
    file = open(pid_file, "w")
    pid = os.getpid()
    file.write(str(pid))
    file.close()
    signal.signal(signal.SIGTERM, term_signal_handler)
    while True:
        if is_stop:
            break
        try:
            Host.report()
        except:
            CONF.log.exception("exception in schedule")
        try:
            task_list = Task.get_all_task()
        except:
            CONF.log.exception("exception in schedule")
        for task in task_list:
            try:
                status = task.get_status()
                max_qps = get_max_qps(task)
                resource_num = int(get_resource_num(task))
                if get_total_qps(task) < 1.0:
                    report_current_action(task.get_task_info(),'停止压力-1')
                    task.set_qps("1")
                if status == "start":
                    start_action(task.get_task_info())
                    report_current_action(task.get_task_info(),'开启压力')
                    total_qps = get_total_qps(task)
                    require_num = int(math.ceil(total_qps/max_qps))
                    agent_qps = int(math.ceil(total_qps/require_num))
                    if not Host.allocate_agent(task, int(max_qps), resource_num, require_num):
                        CONF.log.error("分配agent失败")
                    task.set_agent_qps(agent_qps)
                    task.set_status("running")
                elif status == "running":
                    total_qps = get_total_qps(task)
                    require_num = int(math.ceil(total_qps/max_qps))
                    current_num = get_agent_num(task)
                    if require_num > current_num:
                        report_current_action(task.get_task_info(),'增加压力')
                        add_num = require_num - current_num
                        agent_qps = int(math.ceil(total_qps/require_num))
                        if not Host.allocate_agent(task, int(max_qps), resource_num, add_num):
                            CONF.log.error("分配agent失败")
                        task.set_agent_qps(agent_qps)
                    elif current_num > require_num:
                        report_current_action(task.get_task_info(),'减少压力')
                        reduce_num = current_num - require_num
                        agent_qps = int(math.ceil(total_qps/require_num))
                        if not Host.release_agent(task, reduce_num):
                            CONF.log.error("回收agent失败")
                        task.set_agent_qps(agent_qps)
                    else:
                        agent_qps = int(math.ceil(total_qps/current_num))
                        CONF.log.error("保持当前qps:%s" %(str(agent_qps)))
                        task.set_agent_qps(agent_qps)
                elif status == "stop":
                    end_action(task.get_task_info())
                    report_current_action(task.get_task_info(),'停止压力')
                    try:
                        Host.release_agent(task, -1)
                        Task.delete_task(task.get_id())
                    except Exception,e:
                        CONF.log.error("FATAL:")
                        CONF.log.error(str(e))
                        CONF.log.error(traceback.format_exc())
                        continue
                        
            except:
                CONF.log.exception("exception in schedule")
        time.sleep(3)
