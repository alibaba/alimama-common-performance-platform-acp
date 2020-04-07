#coding=utf-8
import sys
import time
import json
import os
path = os.path.split(os.path.realpath(__file__))[0]
sys.path.append(path+"/..")
from common.util import *
from common.zk import *

class Agent:

    def __init__(self, task_id, agent_id, host, target, qps, source, query_path, query_type, option, max_qps, resource_num):
        self.task_id = task_id
        self.agent_id = agent_id
        self.host = host
        self.target = target
        self.qps = qps
        self.source = source
        self.query_path = query_path
        self.query_type = query_type
        self.option = option
        self.max_qps = max_qps
        self.resource_num = resource_num

    @classmethod
    def delete_agent(self, agent):
        agent.delete_in_zk()

    def get_agent_info(self):
        info = {}
        info["target"] = self.target
        info["qps"] = self.qps
        info["source"] = self.source
        info["query_path"] = self.query_path
        info["query_type"] = self.query_type
        info["option"] = self.option
        info["max_qps"] = self.max_qps
        info["resource_num"] = self.resource_num
        return info

    def get_host(self):
        return self.host

    def get_task_id(self):
        return self.task_id

    def get_id(self):
        return self.agent_id

    def heartbeat(self):
        zk = ZK(CONF.zk_address)
        path = "%s/%s/resource/%s/%s" % (CONF.task_path, self.task_id, self.host, self.agent_id)
        agent_node = zk.get_node(path)
        if agent_node.has_child("heartbeat"):
            return True
        else:
            return False

    def set_qps(self, qps):
        self.qps = qps
        zk = ZK(CONF.zk_address)
        path = "%s/%s/resource/%s/%s/info" % (CONF.task_path, self.task_id, self.host, self.agent_id)
        node = zk.get_node(path)
        node.set_value(json.dumps(self.get_agent_info()))

    def create_in_zk(self):
        zk = ZK(CONF.zk_address)
        path = CONF.task_path + "/" + self.task_id
        root = zk.get_node(path)
        lock = root.get_lock()
        lock.acquire(timeout=0.002)
        rs_node = root.get_child("resource")
        host_node = None
        if not rs_node.has_child(self.host):
            host_node = rs_node.add_child(self.host)
        else:
            host_node = rs_node.get_child(self.host)
        agent_node = host_node.add_child(self.agent_id)
        agent_node.add_child("info", json.dumps(self.get_agent_info()))
        agent_node.add_child("output")
        lock.release()

    def delete_in_zk(self):
        zk = ZK(CONF.zk_address)
        path = CONF.task_path + "/" + self.task_id
        root = zk.get_node(path)
        lock = root.get_lock()
        lock.acquire(timeout=0.002)
        rs_node = root.get_child("resource")
        host_node = rs_node.get_child(self.host)
        if host_node.has_child(self.agent_id) and len(host_node.list_children()) == 1:
            host_node.delete()
        else:
            agent_node = host_node.get_child(self.agent_id)
            agent_node.delete()
        lock.release()
        
