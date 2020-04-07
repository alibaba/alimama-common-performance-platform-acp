#coding:utf-8
import os,sys
path = os.path.split(os.path.realpath(__file__))[0]
sys.path.append(path+"/..")
import time
from common.util import *
from kazoo.client import KazooClient
import kazoo.exceptions 
from agentctl import AgentCtl
from kazoolock import ZooKeeperLock
from task.task import Task
from task.agent import Agent
from host import Host
import json
from common.zk import *

def singleton(cls, *args, **kw):
    instances = {}
    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return _singleton

@singleton
class ResManager(object):
    '''
    资源管理模块
    '''

    def __init__(self):
        self._zk_client = KazooClient(hosts=CONF.zk_address)
        self._zk_client.start()
        CONF.log.debug("zk client started, zk_address = %s"%(CONF.zk_address))
        self._zk_client.ensure_path(os.path.join(CONF.host_path),"list")
        self.zkHostLock = ZooKeeperLock(CONF.zk_address,"host_lock",os.path.join(CONF.host_path,"lock"))
        self.hostRootPath = os.path.join(CONF.host_path,"list")

    def allocate_agent(self, taskObj, count, agentRes, agentMaxQps):
        '''
        为指定的任务分配压测Agent
        '''

        CONF.log.info(\
            "[Enter]allocate_agent. taskObj=%s, count=%s, agentRes=%s, agentMaxQps=%s"\
                %(taskObj.__dict__, count, agentRes, agentMaxQps))
        # get task id
        taskId = taskObj.task_id
        queryType = taskObj.query_type
        
        # 根据task的query_type获得相应agent类型所占用的资源和MaxQps
        # 这里有一个约束：一个任务中只包含一种类型的压测Agent(资源占用相同)

        # 更新 Host 相关zk 节点
        try:
            # 获取host列表(过滤掉error状态的host)
            hostList = self.read_hosts(nonerr=True)

            # 取host锁
            self._acquire_host_lock()

            # 取transaction
            transaction = self._zk_client.transaction()

            # 本次的agent 分配列表
            agentAllocateList = []

            # 在初始获取lastSeq，所有分配结束后才更新lastSeq到zk
            lastSeq = self._getLastSeq()

            # 广度优先分配资源
            while count > 0:
                # 获取最多resource的host列表
                mostResourcefulHostList = self._select_most_resourceful_hosts(hostList)

                # 如果最多resource的host依然无法满足agentRes则分配失败
                if int(mostResourcefulHostList[0].availableRes) < agentRes:
                    CONF.log.debug("最多resource的host依然无法满足agentRes则分配失败(availableRes=%s,agnetRes=%s)"\
                        %(int(mostResourcefulHostList[0].availableRes),agentRes))

                    break

                for hostObj in mostResourcefulHostList:
                    hostIp = hostObj.ip
                    availableRes = int(hostObj.availableRes)

                    # 当前主机资源满足需求，则分配一个agent在上面
                    if availableRes >= agentRes:
                        lastSeq += 1
                        agentId = "%s_%s"%(hostIp,lastSeq)

                        CONF.log.info("allocate one agent on %s. (availableRes=%s, agentRes=%s)"%(hostIp,availableRes,agentRes))
                        agentAllocateList.append({"hostIp":hostIp, "agentId":agentId, "agentRes":agentRes, "taskId":taskId, "queryType":queryType})

                        availableRes -= agentRes
                        hostObj.availableRes = str(availableRes)
                        hostObj.status = "occupied"

                        count -= 1

                        # 更新zk (availableRes)
                        availableResPath = os.path.join(self.hostRootPath,hostIp,"availableRes")
                        statusPath = os.path.join(self.hostRootPath,hostIp,"status")

                        self._zk_client.ensure_path(availableResPath)
                        self._zk_client.ensure_path(statusPath)

                        transaction.set_data(availableResPath,hostObj.availableRes)
                        transaction.set_data(statusPath,hostObj.status)

                        # 分配完成
                        if count == 0:
                            break

            # 资源不足
            if count > 0:
                raise Exception("资源不足(taskObj = %s, count = %d)"%(taskObj.__dict__, count))

            # 分配成功，更新zk(lastSeq)
            lastSeqPath = os.path.join(CONF.host_path,"lastSeq")
            self._zk_client.ensure_path(lastSeqPath)
            transaction.set_data(lastSeqPath,str(lastSeq))

        finally:
            # 释放host锁
            self._release_host_lock()

        # 调用任务管理模块更新任务相关的resource信息
        for agentObj in agentAllocateList:
            taskObj.add_agent(agentObj.get("hostIp"),agentObj.get("agentId"),agentMaxQps,agentRes)

        # 执行transaction, 更新Host zk 节点
        transaction.commit()

        # 初始化AgentCtl，启动Agent
        for agentObj in agentAllocateList:
            agentCtl = AgentCtl(agentObj.get("hostIp"),agentObj.get("agentId"),agentObj.get("taskId"), agentObj.get("queryType"))
            agentCtl.create()

        CONF.log.debug("[Exit]allocate_agent. taskObj=%s, count=%s, agentRes=%s, agentMaxQps=%s"\
                        %(taskObj.__dict__, count, agentRes, agentMaxQps))

    def _select_most_resourceful_hosts(self,hostlist):
        '''
        utility function.
        从给定hostlist中选出拥有最多availableRes的hosts

        Input:
            hostlist:   hostObj的列表
        Output:
            给定hostlist中拥有最多availableRes的hostObj
            (列表，因为有可能有多个availableRes相同的host
        '''

        CONF.log.debug("[Enter] _select_most_resourceful_hosts(), hostlist[0] = %s(type=%s,len=%d)"%(hostlist[0].__dict__,type(hostlist),len(hostlist)))

        # 1. Sort by availableRes
        sortedHostList = sorted(hostlist,key=lambda host:int(host.availableRes), reverse=True)

        # 2. 遍历取出availableRes最多的返回
        maxAvailableRes = int(sortedHostList[0].availableRes)
        for idx in range(len(sortedHostList)):
            hostObj = sortedHostList[idx]
            if int(hostObj.availableRes) < maxAvailableRes:
                return sortedHostList[:idx]

        return sortedHostList

    def _getLastSeq(self):
        path = "/acp/host/lastSeq"
        result = self._zk_client.get(path)[0]
        return int(result)
            
    def getHostStatus(self,hostIp):
        status_path = os.path.join(self.hostRootPath,hostIp,"status") 
        return self._zk_client.get(status_path)[0]

    def release_agents_for_task(self, taskObj, count):
        '''
        释放指定task,指定数量的agent

        taskObj:    描述task的对象
        count:      待释放agent的数量
        '''

        CONF.log.debug("[Enter]release_agent_for_task: %s"%(taskObj.__dict__))
        agentsForTask = taskObj.get_all_agent()
        if count > len(agentsForTask):
            raise Exception("count > number of agents for task: %s"%(str(taskObj)))

        # 选取count个待释放agent
        agentsToBeReleased = agentsForTask[:count]
        for agent in agentsToBeReleased:
            self.release_agent(agent)
        CONF.log.debug("[Exit]release_agent_for_task: %s"%(taskObj.__dict__))

    def release_all_agents(self, taskObj):
        agentsForTask = taskObj.get_all_agent()
        for agent in agentsForTask:
            self.release_agent(agent)

    def release_agent(self, agentObj):
        '''
        释放指定的Agent
        '''
        CONF.log.debug("[Enter]release_agent: %s"%(agentObj.__dict__))
        agentCtl = AgentCtl(agentObj.host,agentObj.agent_id,agentObj.task_id,agentObj.query_type)

        # 通知Agent Daemon停agent
        agentCtl.delete()

        # 取锁, 然后更新Host节点(availableRes)
        self._acquire_host_lock()
        try:
            # 更新availableRes
            availableResPath = os.path.join(self.hostRootPath,agentCtl.hostIp,"availableRes")
            currentValue = int(self._zk_client.get(availableResPath)[0])
            agentRes = int(agentObj.resource_num)
            currentValue += agentRes

            transaction = self._zk_client.transaction()

            # 取得totalRes
            totalResPath = os.path.join(self.hostRootPath,agentCtl.hostIp,"totalRes")
            totalRes = int(self._zk_client.get(totalResPath)[0])

            # 更新availableRes on zk
            transaction.set_data(availableResPath,str(currentValue))

            # 如果host上所有资源都被释放则置host状态为idle
            if currentValue == totalRes:
                statusPath = os.path.join(self.hostRootPath,agentCtl.hostIp,"status")
                CONF.log.debug("release_agent() set host status to idle")
                transaction.set_data(statusPath,"idle")

            # 通知task manager释放Agent资源
            Agent.delete_agent(agentObj)
            transaction.commit()
            CONF.log.debug("[Exit]release_agent(), reset availableRes data (path=%s, value=%s)"%(availableResPath,str(currentValue)))
        finally:
            # 释放锁
            self._release_host_lock()
  
    def read_hosts(self,filter=None,nonerr=False):
        try:
            CONF.log.debug("[Enter]read_hosts()")
            # 取锁
            self._acquire_host_lock()

            # 取所有host根节点
            hostIpList = self._zk_client.get_children(self.hostRootPath)

            ret = []
            for hostIp in hostIpList:
                # 构造一个hostObj
                hostObj = Host(hostIp)

                hostpath = os.path.join(self.hostRootPath,hostIp) 
                hostAttrList = self._zk_client.get_children(hostpath)
                
                for attr in hostAttrList:
                    attrpath = os.path.join(self.hostRootPath,hostIp,attr)
                    value = self._zk_client.get(attrpath)[0]
                    setattr(hostObj,attr,value)
                    CONF.log.debug("setattr: %s=%s"%(attr,value))

                # 过滤掉error状态的host
                if nonerr and hostObj.status == "error":
                    continue

                # 检查当前hostObj是否满足filter条件, 满足则添加到结果集
                if filter == None or set(filter.items()).issubset(set(hostObj.__dict__.items())):
                    ret.append(hostObj)

            CONF.log.debug("[Exit]read_hosts(), ret = %s, len=%d, ret[0] = %s"%(ret,len(ret),ret[0].__dict__))
            return ret
        finally:
            # 释放锁
            self._release_host_lock()

    def add_hosts(self,hostList):
        '''
        hostObj: {
            "ip":"1.1.1.1", "totalRes": 4,
            "availableRes": 4, "status": idle
        }
        '''

        CONF.log.info("[Enter]add_hosts()")
        try: 
            # 取锁
            self._acquire_host_lock()

            for hostObj in hostList:
                # 创建host根节点
                hostPath = os.path.join(self.hostRootPath,hostObj.ip)
                if self._zk_client.exists(hostPath):
                    raise Exception("The zk path \"%s\" already exists"%(hostPath))
    
                transaction = self._zk_client.transaction()
                transaction.create(hostPath)
    
                # 创建host属性节点
                for k,v in hostObj.__dict__.items():
                    keyPath = os.path.join(hostPath,k)
                    transaction.create(keyPath)
                    transaction.set_data(keyPath,str(v))
    
                transaction.commit()
            CONF.log.info("[Exit]add_hosts()")
        finally:
            # 释放锁
            self._release_host_lock()

    def del_hosts(self,hostList):
        CONF.log.info("[Enter]del_hosts()")
        try:
            # 取锁
            self._acquire_host_lock()

            for hostObj in hostList:
                # 删除host根节点
                hostPath = os.path.join(self.hostRootPath,hostObj.ip)
                if not self._zk_client.exists(hostPath):
                    raise Exception("the zk path \"%s\" does not exist."%(hostPath))

                self._zk_client.delete(hostPath,recursive=True)
            CONF.log.info("[Exit]del_hosts()")
        finally:
            # 释放锁
            self._release_host_lock()

    def _acquire_host_lock(self):
        ret = self.zkHostLock.acquire()
        if not ret:
            raise Exception("acquire host lock failed.")

    def _release_host_lock(self):
        self.zkHostLock.release()

    def stopZkClient(self):
        CONF.log.debug("[Enter]stopZkClient()")
        if self._zk_client != None:
            self._zk_client.stop() 
        self._zk_client = None

    def __del__(self):
        #self.stopZkClient()
        pass
