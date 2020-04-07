#coding=utf-8
import sys
import json
import os
path = os.path.split(os.path.realpath(__file__))[0]
sys.path.append(path+"/..")
from common.util import *
from common.zk import *
from task.agent import *
from task.task import *
import urllib2
DO_NOT_CHECK_QUERY_FLAG = True
class Host:

    def __init__(self, ip, id=-1, query="", status="init", available=10, total=10):
        self.ip = ip
        self.id = id
        self.query = query
        self.status = status
        self.available = available
        self.total = total

    @classmethod
    def get_all_host(self):
        zk = ZK(CONF.zk_address)
        root = zk.get_node(CONF.host_path)
        list_node = root.get_child("list")
        host_list = []
        for host_node in list_node.list_children():
            host = Host(host_node.get_name())
            host.get_info_from_zk()
            if host.checkSpecialNode("spe") or host.checkSpecialNode("erpc"):
                continue
            host_list.append(host)
        return host_list

    @classmethod
    def get_spe_host(self,target,task):
        zk = ZK(CONF.zk_address)
        root = zk.get_node(CONF.host_path)
        list_node = root.get_child("list")
        spe_host_list = []

        option =  task.get_task_info()["option"]
        jsobObj1 = json.loads(task.get_task_info()["option"])
        firstCluster = "3"
        #firstCluster = str(jsobObj1['cluster'])

        for host_node in list_node.list_children():
            host = Host(host_node.get_name())
            if firstCluster == '3':     
                host.get_info_from_zk()
                spe_host_list.append(host)
            elif firstCluster == '2':   
                if host.checkSpecialNode("spe") and host.checkSpecialNode("2"): 
                    host.get_info_from_zk()
                    spe_host_list.append(host)
            else:
                if host.checkSpecialNode("spe"):
                    if host.checkSpecialNode("3"):
                        continue
                    if host.checkSpecialNode("2"):
                        continue
                    else:
                        host.get_info_from_zk()
                        spe_host_list.append(host)

        return spe_host_list







    # 汇总host上的query情况
    @classmethod
    def report(self):
        host_list = Host.get_all_host()
        total_num = len(host_list)
        result = {}
        for host in host_list:
            if len(host.query) > 0:
                dict = json.loads(host.query)
                for key in dict:
                    for query in dict[key]:
                        if not result.has_key(key):
                            result[key] = {}
                        if not result[key].has_key(query):
                            result[key][query] = {"yes": 0, "no": total_num}
                        result[key][query]["yes"] += 1
                        result[key][query]["no"] -= 1
        zk = ZK(CONF.zk_address)
        node = zk.get_node(CONF.host_path)
        node.set_value(json.dumps(result))

    @classmethod
    def get_query_list(self):
        query_set = {}
        zk = ZK(CONF.zk_address)
        node = zk.get_node(CONF.host_path)
        value = node.get_value()
        if 0 == len(value):
            return query_set
        else:
            dict = json.loads(value)
            for key in dict:
                for query_key in dict[key]:
                    # 超过60%的host上存在query, 则认为该query可用
                    yes_num = dict[key][query_key]["yes"]
                    no_num = dict[key][query_key]["no"]
                    if float(yes_num)/(yes_num + no_num) >= 0.5:
                        if not query_set.has_key(key):
                            query_set[key] = []
                        query_set[key].append(query_key)
        return query_set

    # 若query_path为data目录，返回data目录下最新的query
    @classmethod
    def get_real_query(self, query_path):
        query_set = Host.get_query_list()
        dir_set = {}
        for key in query_set:
            for query in query_set[key]:
                if query == query_path:
                    return query
                if key == "temp" or key =="userdefine":
                    continue
                index = query.rfind("/")
                dir_name = query[:index]
                if not dir_set.has_key(dir_name):
                    dir_set[dir_name] = []
                dir_set[dir_name].append(query)
        # 判断是否为data目录
        for key in dir_set:
            if key == query_path:
               dir_set[key].sort(reverse=True)
               return dir_set[key][0]
        return ""

    @classmethod
    def add_host(self, ip):
        host_list = Host.get_all_host()
        num_list = []
        max_num = 1000
        for i in range(max_num):
            num_list.append(True)
        for host in host_list:
            if ip == host.ip:
                return True
            num_list[host.id] = False
        for i in range(len(num_list)):
            if num_list[i]:
                host = Host(ip, i)
                host.create_in_zk()
                return True
        return False

    @classmethod
    def delete_host(self, ip):
        host_list = Host.get_all_host()
        for host in host_list:
            if host.ip == ip:
                host.delete_in_zk()
                return True

    @classmethod
    def allocate_agent(self, task, max_qps, resource, agent_num):
        retJson = ""
        available_list = []
        query = task.get_task_info()["query_path"]
        query_type = task.get_task_info()["query_type"]
        target = task.get_task_info()["target"]
        available_num = 0
        host_list = []
        if query_type == "http" or query_type == "https":
           host_list = Host.get_spe_host(target,task)
        else:
           host_list = Host.get_all_host() 
           CONF.log.error("get all host num: %d" % (len(host_list)))
        for host in host_list:
            if DO_NOT_CHECK_QUERY_FLAG:
                if host.available >= resource:
                    available_list.append(host)
                    available_num += host.available/resource
            else:
                if host.available >= resource and host.has_query(query):
                    available_list.append(host)
                    available_num += host.available/resource
        if available_num < agent_num:
            CONF.log.error("qq: %s resource not enough: available %d, need %d" % (query_type,available_num, agent_num))
            return False
        available_list.sort(key=lambda host:int(host.available), reverse=True)
        allocate_num = 0
        if True:
            while allocate_num < agent_num:
                for host in available_list:
                    if host.available >= resource:
                        if host.allocate(task, max_qps, resource):
                            allocate_num += 1
                    if allocate_num >= agent_num:
                        break
        return True

    @classmethod
    def release_agent(self, task, agent_num):
        agent_list = task.get_all_agent()
        if agent_num > len(agent_list):
            CONF.log.error("agents not enough: %d/%d" % (agent_num, len(agent_list)))
            return False
        if agent_num < 0:
            agent_num = len(agent_list)
        release_num = 0
        for agent in agent_list:
            host = Host(agent.host)
            host.get_info_from_zk()
            if host.release(agent):
                release_num += 1
            if release_num >= agent_num:
                break
        return True

    @classmethod
    def release_agent_for_special(self, task, agent_num):
        agent_list = task.get_all_agent()
        if agent_num > len(agent_list):
            CONF.log.error("agents not enough: %d/%d" % (agent_num, len(agent_list)))
            return False
        if agent_num < 0:
            agent_num = len(agent_list)
        release_num = 0
        for agent in agent_list:
            host = Host(agent.host)
            host.get_info_from_zk()
            if release_num >= agent_num:
                break
            try:
                if host.release(agent):
                    release_num += 1
            except Exception,e:
                print str(e)
                continue
        return True

    @classmethod
    def release_agent_ignore_task(self, task_id):
        zk = ZK(CONF.zk_address)
        root = zk.get_node(CONF.host_path)
        list_node = root.get_child("list")
        host_list = []
        for host_node in list_node.list_children():
            host = Host(host_node.get_name())
            try:
                if host.release_for_special(task_id):
                    pass
                    #release_num += 1
            except Exception,e:
                print str(e)
                continue
        return True

    def has_query(self, query_path):
        if 0 == len(self.query):
            return False
        dict = json.loads(self.query)
        for key in dict:
            for query in dict[key]:
                if query_path == query:
                    return True
        return False

    # 获取zk上的seq号，用于编码agent_id
    def get_seq(self):
        zk = ZK(CONF.zk_address)
        root = zk.get_node(CONF.host_path)
        seq_node = root.get_child("lastSeq")
        return int(seq_node.get_value())

    def set_seq(self, seq):
        zk = ZK(CONF.zk_address)
        root = zk.get_node(CONF.host_path)
        seq_node = root.get_child("lastSeq")
        seq_node.set_value(str(seq))

    # 获取zk上agentList的值
    def get_agent_in_zk(self):
        zk = ZK(CONF.zk_address)
        root = zk.get_node(CONF.host_path)
        list_node = root.get_child("list")
        host_node = list_node.get_child(self.ip)
        value_list = []
        if not host_node.has_child("agentList"):
            return value_list
        agent_list_node = host_node.get_child("agentList")
        value = agent_list_node.get_value()
        if len(value) > 0:
            value_list = json.loads(value)
        return value_list

    def add_agent_in_zk(self, task_id, agent_id, query_type):
        zk = ZK(CONF.zk_address)
        root = zk.get_node(CONF.host_path)
        list_node = root.get_child("list")
        host_node = list_node.get_child(self.ip)
        agent_list_node = host_node.get_child("agentList")
        value = agent_list_node.get_value()
        agent_list = []
        if len(value) > 0:
            agent_list = json.loads(value)
        # 检查是否重复添加
        for dict in agent_list:
            if task_id == dict["task_id"] and agent_id == dict["agent_id"]:
                return True
        agent_list.append({"task_id":task_id, "agent_id":agent_id, "query_type":query_type})
        agent_list_node.set_value(json.dumps(agent_list))
        return True

    def delete_agent_in_zk(self, task_id, agent_id, query_type):
        zk = ZK(CONF.zk_address)
        root = zk.get_node(CONF.host_path)
        list_node = root.get_child("list")
        host_node = list_node.get_child(self.ip)
        agent_list_node = host_node.get_child("agentList")
        value = agent_list_node.get_value()
        agent_list = []
        if len(value) > 0:
            agent_list = json.loads(value)
        # 检查是否重复添加
        for dict in agent_list:
            if task_id == dict["task_id"] and agent_id == dict["agent_id"]:
                agent_list.remove(dict)
                agent_list_node.set_value(json.dumps(agent_list))
                return True
        return False

    def delete_agent_in_zk_for_special(self, task_id, agent_id, query_type):
        ### agent_id is no use for this case, only by task_id
        zk = ZK(CONF.zk_address)
        root = zk.get_node(CONF.host_path)
        list_node = root.get_child("list")
        host_node = list_node.get_child(self.ip)
        agent_list_node = host_node.get_child("agentList")
        value = agent_list_node.get_value()
        agent_list = []
        #if len(value) > 0:
        agent_list = json.loads(value)
        # 检查是否重复添加
#        agent_list_node.set_value("")
        for dict in agent_list:
            #if task_id == dict["task_id"] and agent_id == dict["agent_id"]:
            if task_id == dict["task_id"]:
#                print dict
#                print task_id
                agent_list.remove(dict)
                agent_list_node.set_value(json.dumps(agent_list))
                return True
        return True 

    def allocate(self, task, max_qps, resource):
        query = task.get_task_info()["query_path"]
        type = task.get_task_info()["query_type"]
        if not self.has_query(query):
            if not DO_NOT_CHECK_QUERY_FLAG:
                CONF.log.error("query %s not exist: %s" % (query, self.ip))
                return False
            else:
                CONF.log.error("DO_NOT_CHECK_QUERY!")
        if self.available < resource:
            CONF.log.error("resource not enough: %s" % self.ip)
            return False
        seq = self.get_seq() + 1
        agent_id = "%s_%s" % (self.ip, seq)
        # 在task下创建agent
        task.add_agent(self.ip, agent_id, max_qps, resource)
        if not self.add_agent_in_zk(task.task_id, agent_id, type):
            CONF.log.error("start agent fail: %s" % self.ip)
            return False
        self.set_seq(seq)
        self.available -= resource
        self.status = "occupied"
        self.update_info_from_zk()
        return True

    def release(self, agent):
        if not self.delete_agent_in_zk(agent.task_id, agent.agent_id, agent.query_type):
            CONF.log.error("stop agent fail: %s" % self.ip)
            return False
        self.available += int(agent.resource_num)
        if self.available == self.total:
            self.status = "idle"
        self.update_info_from_zk()
        Agent.delete_agent(agent)
        return True

    def release_for_special(self, task_id):
        if not self.delete_agent_in_zk_for_special(task_id, -1, "-1"):
            CONF.log.error("stop agent fail: %s" % self.ip)
            return False
#        self.available += int(agent.resource_num)
#        if self.available == self.total:
#            self.status = "idle"
#        self.update_info_from_zk()
#        Agent.delete_agent(agent)
        return True

    def create_in_zk(self):
        zk = ZK(CONF.zk_address)
        root = zk.get_node(CONF.host_path)
        list_node = root.get_child("list")
        host_node = list_node.add_child(self.ip)
        host_node.set_value(str(self.id))
        host_node.add_child("ip").set_value(self.ip)
        host_node.add_child("query").set_value(self.query)
        host_node.add_child("status").set_value(self.status)
        host_node.add_child("availableRes").set_value(str(self.available))
        host_node.add_child("totalRes").set_value(str(self.total))
        host_node.add_child("agentList")

    def get_info_from_zk(self):
        zk = ZK(CONF.zk_address)
        root = zk.get_node(CONF.host_path)
        list_node = root.get_child("list")
        host_node = list_node.get_child(self.ip)
        self.id = int(host_node.get_value())
        self.query = host_node.get_child("query").get_value()
        self.status = host_node.get_child("status").get_value()
        self.available = int(host_node.get_child("availableRes").get_value())
        self.total = int(host_node.get_child("totalRes").get_value())

    def checkSpecialNode(self,key):
        zk = ZK(CONF.zk_address)
        root = zk.get_node(CONF.host_path)
        list_node = root.get_child("list")
        host_node = list_node.get_child(self.ip)
        self.id = int(host_node.get_value())
        return host_node.has_child(key)

    def update_info_from_zk(self):
        zk = ZK(CONF.zk_address)
        root = zk.get_node(CONF.host_path)
        list_node = root.get_child("list")
        host_node = list_node.get_child(self.ip)
        host_node.set_value(str(self.id))
        host_node.get_child("ip").set_value(self.ip)
        host_node.get_child("query").set_value(self.query)
        host_node.get_child("status").set_value(self.status)
        host_node.get_child("availableRes").set_value(str(self.available))
        host_node.get_child("totalRes").set_value(str(self.total))

    def delete_in_zk(self):
        zk = ZK(CONF.zk_address)
        root = zk.get_node(CONF.host_path)
        list_node = root.get_child("list")
        host_node = list_node.get_child(self.ip)
        host_node.delete()
