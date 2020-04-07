#coding=utf-8
import sys
import time
import json
import os
path = os.path.split(os.path.realpath(__file__))[0]
sys.path.append(path+"/..")
from common.util import *
from common.zk import *
from agent import *

class Task:

    def __init__(self, id, target, qps, source, query_path, query_type, option, status):
        self.task_id = id
        self.target = target
        self.qps = qps
        self.source = source
        self.query_path = query_path
        self.status = status
        self.option = option
        self.query_type = query_type

    @classmethod
    def create_task(self, target, qps, source, query_path, query_type, option):
        status = "start"
        time.sleep(0.002)
        id = "t" + str(int(round(time.time()*1000)))
        task = Task(id, target, qps, source, query_path, query_type, option, status)
        task.create_in_zk()
        return task

    @classmethod
    def delete_task(self, task_id):
        task = Task.get_task(task_id)
        task.delete_in_zk()

    @classmethod
    def get_task(self, task_id):
        path = CONF.task_path + "/" + task_id
        zk = ZK(CONF.zk_address)
        root = zk.get_node(path)
        if not root:
            return None
        else:
            task = Task.get_task_by_zknode(root)
            return task

    @classmethod
    def get_all_task(self):
        zk = ZK(CONF.zk_address)
        root = zk.get_node(CONF.task_path)
        task_list = []
        for child in root.list_children():
            task = Task.get_task_by_zknode(child)
            task_list.append(task)
        return task_list

    @classmethod
    def get_task_by_zknode(self, node):
        status = node.get_value()
        info_node = node.get_child("info")
        info = json.loads(info_node.get_value())
        id = node.get_name()
        target = info["target"]
        qps = info["qps"]
        source = info["source"]
        query_path = info["query_path"]
        option = info["option"]
        query_type = info["query_type"]
        task = Task(id, target, qps, source, query_path, query_type, option, status)
        return task
            
    def get_status(self):
        return self.status

    def get_id(self):
        return self.task_id

    def get_current_qps(self):
        total_qps = 0
        for agent in self.get_all_agent():
            info = agent.get_agent_info()
            agent_qps = int(info["qps"])
            total_qps += agent_qps
        return total_qps

    def get_task_info(self):
        info = {}
        info["target"] = self.target
        info["qps"] = self.qps
        info["source"] = self.source
        info["query_path"] = self.query_path
        info["option"] = self.option
        info["query_type"] = self.query_type
        return info

    def add_agent(self, host, agent_id, max_qps, resource_num):
        agent = Agent(self.task_id, agent_id, host, self.target, "1", self.source, self.query_path, self.query_type, self.option, str(max_qps), str(resource_num))
        agent.create_in_zk()
        return agent

    def get_all_agent(self):
        zk = ZK(CONF.zk_address)
        path = "%s/%s/resource/" % (CONF.task_path, self.task_id)
        root = zk.get_node(path)
        agent_list = []
        for host_node in root.list_children():
            for agent_node in host_node.list_children():
                info_node = agent_node.get_child("info")
                try:
                    info = json.loads(info_node.get_value())
                except Exception,e:
                    print e
                    continue
                target = info["target"]
                qps = info["qps"]
                source = info["source"]
                query_path = info["query_path"]
                query_type = info["query_type"]
                option = info["option"]
                max_qps = info["max_qps"]
                resource_num = info["resource_num"]
                agent = Agent(self.task_id, agent_node.get_name(), host_node.get_name(), target, qps, source, query_path, query_type, option, max_qps, resource_num)
                agent_list.append(agent)
        return agent_list

    def set_status(self, status):
        self.status = status
        zk = ZK(CONF.zk_address)
        path = CONF.task_path + "/" + self.task_id
        root = zk.get_node(path)
        root.set_value(status)

    def set_qps(self, qps):
        self.qps = qps
        zk = ZK(CONF.zk_address)
        path = CONF.task_path + "/" + self.task_id + "/info"
        node = zk.get_node(path)
        node.set_value(json.dumps(self.get_task_info()))

    def set_agent_qps(self, qps):
        QPS_INDEX= 10
        for agent in self.get_all_agent():
            dic = agent.get_agent_info()
            #CONF.log.error("current conf:")
            #CONF.log.error(json.dumps(dic))
           # CONF.log.error("\n\n")
          #  agent.set_qps(str(QPS_INDEX))
          #  QPS_INDEX = QPS_INDEX+10
            agent.set_qps(str(qps))

    def delete_all_agent(self):
        agent_list = self.get_all_agent()
        for agent in agent_list:
            agent.delete_in_zk()

    def create_in_zk(self):
        zk = ZK(CONF.zk_address)
        root = zk.get_node(CONF.task_path)
        t_node = root.add_child(self.task_id, self.status)
        t_node.add_child("resource")
        info_node = t_node.add_child("info", json.dumps(self.get_task_info()))

    def delete_in_zk(self):
        zk = ZK(CONF.zk_address)
        path = CONF.task_path + "/" + self.task_id
        node = zk.get_node(path)
        lock = node.get_lock()
        lock.acquire(timeout=0.002)
        node.delete()
        lock.release()
