#coding:utf-8
import os
import sys
sys.path.append("..")
from common.util import *
from monitor import *
from task.task import Task
from task.agent import Agent
from res_manager.res_manager import ResManager
import random
import urllib2
import json

class Rule:
    '''
    Rule为监控时的一个具体监控项

    success：   绑定了在一次监控success时要执行的Action实例
    failure:    绑定了在一次监控failure时要执行的Action实例

    注：此类为基类，实际使用是要写具体实现类并将实际检查逻辑写在run()里面
    '''
    COUNT = 0

    def __init__(self,failure=None, success=None):
        Rule.COUNT += 1

        # 确保success和failure为tuple or list
        if not (type(failure) in (tuple,list)):
            failure = tuple([failure])
        if not (type(success) in (tuple,list)):
            success = tuple([failure])

        self.failure = failure
        self.success = success

    def run(self):
        pass

class DemoRule(Rule):
    '''
    最简单的Rule，用作Demo
    '''
    def __init__(self,name,checkitem,failure=(),success=()):
        Rule.__init__(self,failure,success)
        self.name = name
        self.checkitem = checkitem

    def run(self,*args):
        if random.randint(0,1): 
            return Success("This is a success message in DemoRule")
        else:
            return Failure("This is a failure message in DemoRule")

class CheckACPHosts(Rule):
    '''
    检查ACP资源池中的Host是否都活着

    success:    资源池中所有Hosts都活着(对Agent的请求有回复)
    failure:    资源池中出现异常Hosts(对Agent请求没有返回或返回错误码)
    '''
    def __init__(self,hostlist,failure=(),success=()):
        Rule.__init__(self,failure,success)
        self.hostlist = hostlist
        self.error_hosts = []
        self.alive_hosts = []

    def run(self,*args):
        self.error_hosts = []
        self.alive_hosts = []
        for hostname in self.hostlist:
            if self.hostIsAlive(hostname):
                self.alive_hosts.append(hostname)
            else:
                self.error_hosts.append(hostname)

        if len(self.error_hosts) == 0:
            return Success(self.successMessage())
        else:
            info = {"error_hosts":self.error_hosts}
            result = Failure(self.failureMessage())
            result.info = info
            return result

    def hostIsAlive(self,hostname):
        url = 'http://%s:9090%s'%(hostname,CONF.press_agent.get("heartbeat_url"))
        try:
            output = urllib2.urlopen(url).read()
            outputObj = json.loads(output)
            if outputObj.get("ret_code") != 0:
                print "agent heartbeat returns non-zero: %s"%(output)
                return False
            else:
                return True
        except Exception,e:
            print "agent heartbeat check exception: %s"%(str(e))
            return False

    def successMessage(self):
        message = \
        '''\
ACP Host Check Success
======================
The following Hosts are alive:\n'''

        for hostname in self.alive_hosts:
            message += hostname + "\n"

        return message


    def failureMessage(self):
        message = \
        '''\
ACP Host Check Failed
======================
The following Hosts are dead!!!:\n'''

        for hostname in self.error_hosts:
            message += hostname + "\n"

        message += "The following Hosts are alive:\n"

        for hostname in self.alive_hosts:
            message += hostname + "\n"

        return message


class CheckACPActiveAgents(Rule):
    
    def __init__(self,failure=(),success=()):
        Rule.__init__(self,failure,success)
        self.resMgr = ResManager()
    
    def run(self,*args):
        dead_agents = []
        task_list = Task.get_all_task()
        for taskObj in task_list:
            agent_list = taskObj.get_all_agent()
            for agentObj in agent_list:
                if not agentObj.heartbeat():
                    dead_agents.append(agentObj)

        if len(dead_agents) == 0:
            logging.debug("[Exit]CheckACPActiveAgents...success")
            return Success("CheckACPActiveAgents...success.")
        else:
            logging.debug("[Exit]CheckACPActiveAgents...failure")
            result = Failure(self.failureMessage(dead_agents))
            info = {"dead_agents":dead_agents}
            result.info = info
            return result

    def failureMessage(self,dead_agents):
        output = "The following agents are dead:\n"
        for agentObj in dead_agents:
            output += "%s on %s\n"%(agentObj.agent_id, agentObj.host_ip)
        return output
