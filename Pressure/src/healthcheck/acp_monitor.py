#coding:utf-8
import sys
sys.path.append("..")
from healthcheck.monitor import *
from healthcheck.rules import *
from healthcheck.actions import *
from common.util import *
import time
import os

def start_acp_monitor(pid_file):
    try:
        file = open(pid_file,"w")
        pid = os.getpid()
        file.write(str(pid))
        file.close()

        # 定义Action
        #logActionForSuccess = Log("/home/jingyi.mjy/projects/acp-pressure/src/test/monitor_pass.log")
        logActionForFailure = Log(CONF.monitor_failure_log)
        emailActionForFailure = Email(recipient=['jingyi.mjy@alibaba-inc.com','qiuhua.lqh@alibaba-inc.com'],subject='ACP Host Check Failed!')
        markBadHostActionForFailure = MarkACPErrorHosts(CONF.zk_address)
        processACPDeadAgents = ProcessACPDeadAgents()

        # 定义Rule
        checkACPHostsRule = CheckACPHosts(
                                CONF.press_hosts,
                                failure=[logActionForFailure, emailActionForFailure, markBadHostActionForFailure]
                            )

        checkACPActiveAgents = CheckACPActiveAgents(
                                failure=[logActionForFailure,processACPDeadAgents]
                            )

        # 装配并启动monitor
        Monitor("ACP Health Monitor", [checkACPHostsRule,checkACPActiveAgents]).run()
        #Monitor("ACP Health Monitor - checkACPActiveAgents",checkACPActiveAgents).run()

    except Exception,e:
        CONF.log.exception("exception in acp monitor: %s"%(str(e)))
