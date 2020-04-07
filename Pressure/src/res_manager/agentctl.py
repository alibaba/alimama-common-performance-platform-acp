#coding:utf-8
import urllib2
from common.util import *
import json

class AgentCtl:
    '''
    压测AGent控制器

    一个压测Agent控制器实例包含了一系列与Agent daemon交互的方法        
    '''
    def __init__(self, ip, agentId, taskId, queryType):
        '''
        初始化函数

        ip:         agent所在主机IP
        agentid:    全局唯一的压测Agent Id (由Resource Manager生成并指定)
        taskId:     任何一个Agent的创建都是由一个task触发的，这里记录所触发的taskId
        '''

        self.hostIp = ip
        self.agentId = agentId
        self.taskId = taskId
        self.queryType = queryType

    def create(self):
        '''
        (通知Agent Daemon)创建一个压测Agent
        '''
        url = "http://%s:9090/create?task_id=%s&agent_id=%s&query_type=%s"%\
            (self.hostIp, self.taskId, self.agentId, self.queryType)

        CONF.log.info("[Enter]AgentCtl.create(), url = %s"%(url))
        result = urllib2.urlopen(url).read()
        result_json = json.loads(result)
        CONF.log.debug(result_json)

        if result_json.get("code") != "true":
            errmsg = "AgentCtl returns failure result: \n"
            errmsg += "agentId: %s\n"%(self.agentId)
            errmsg += "taskId: %s\n"%(self.taskId)
            errmsg += "url: %s\n"%(url)
            errmsg += "info: %s\n"%(result_json.get("msg"))
            raise Exception(errmsg)
        
        return result

    def delete(self):
        '''
        (通知 Agent Daemon)销毁一个压测Agent
        '''
        url = "http://%s:9090/delete?task_id=%s&agent_id=%s&query_type=%s"%\
            (self.hostIp, self.taskId, self.agentId, self.queryType)

        CONF.log.info("[Enter]AgentCtl.delete(), url = %s"%(url))

        try:
            result = urllib2.urlopen(url).read()
            result_json = json.loads(result)
            CONF.log.debug(result_json)
        except Exception,e:
            CONF.log.error("Exception during relase agent: %s"%(str(e)))
            return None

        if result_json.get("code") != "true":
            errmsg = "AgentCtl returns failure result: \n"
            errmsg += "agentId: %s\n"%(self.agentId)
            errmsg += "taskId: %s\n"%(self.taskId)
            errmsg += "url: %s\n"%(url)
            errmsg += "info: %s\n"%(result_json.get("msg"))
            #raise Exception(errmsg)
            CONF.log.error(errmsg)

        return result
