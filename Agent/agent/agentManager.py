#coding:utf-8
import json
import sys
import time
import os
import threading
from zk import *
from util import *
from agent import *
from data import *
import socket
import multiprocessing

def start_agent(task_id, agent_id, query_type):
    CONF.log.debug("entry start_agent %s", agent_id)
    agent_type = CONF.agent_type[query_type]
    zk = ZK(CONF.zk_address)
    host = socket.gethostbyname(socket.gethostname())
    if "http" == agent_type:
        CONF.log.debug("entry abench %s", agent_type)
        agent = AbenchAgent(zk, host, task_id, agent_id)
    else:
        agent = OtherAgent(zk, host, task_id, agent_id)
    # 检查压测日志
    if not agent.check():
        raise Exception("check fail in start_agent: task_id=%s, agent_id=%s, query_type=%s" % (task_id, agent_id, query_type))
    agent.start()
    agent_list = get_agent_list()
    agent_list.append(agent)
    set_agent_list(agent_list)
    CONF.log.info("press agent (task_id=%s, agent_id=%s, query_type=%s) start" % (task_id, agent_id, query_type))

def stop_agent(task_id, agent_id, query_type):
    agent_list = get_agent_list()
    for agent in agent_list:
        if agent.task_id == task_id and agent.agent_id == agent_id:
            agent.stop()
            agent_list.remove(agent)
    set_agent_list(agent_list)
    return True

# 比较agent_list与zk节点的差异，创建或停止agent
def check_agent_list(agent_list):
    zk = ZK(CONF.zk_address)
    ip = socket.gethostbyname(socket.gethostname())
    path = CONF.host_path + "/" + ip
    root = zk.get_node(path)
    value_list = None
    if not root.has_child("agentList"):
        root.add_child("agentList")
    value = root.get_child("agentList").get_value()
    if 0 == len(value):
        value_list = []
    else:
        value_list = json.loads(value)
    # 检查是否需要创建agent
    for dict in value_list:
        flag = True
        for agent in agent_list:
            if dict["task_id"] == agent.task_id and dict["agent_id"] == agent.agent_id:
                flag = False
        if flag:
            query_type = dict["query_type"]
            task_id = dict["task_id"]
            agent_id = dict["agent_id"]
            agent_type = CONF.agent_type[query_type]
            if "abench" == agent_type:
                agent = AbenchAgent(zk, ip, task_id, agent_id)
            elif "proto_type_1" == agent_type:
                agent = OtherAgent(zk, ip, task_id, agent_id)
            if not agent.check():
                raise Exception("check fail in start_agent: task_id=%s, agent_id=%s, query_type=%s" % (task_id, agent_id, query_type))
            agent.start()
            agent_list.append(agent)
    # 检查是否需要停止agent
    for agent in agent_list:
        flag = True
        for dict in value_list:
            if dict["task_id"] == agent.task_id and dict["agent_id"] == agent.agent_id:
                flag = False
        if flag:
            agent.stop()
            agent_list.remove(agent)

def work():
    change_status()
    agent_list = []
    while True:
        try:
            check_agent_list(agent_list)
            for agent in agent_list:
                try:
                    agent.monitor_zk()
                    alive = agent.is_alive()
                    if not alive:
                        agent.start()
                        CONF.log.exception("restart bench tool!")
                    agent.heartbeat(alive)
                    agent.output_to_zk()
                except:
                    CONF.log.exception("exception in work")
        except:
            CONF.log.exception("exception in work")
        time.sleep(1) 

def get_id():
    ip = socket.gethostbyname(socket.gethostname())
    zk = ZK(CONF.zk_address)
    path = CONF.host_path + "/" + ip
    node = zk.get_node(path)
    return node.get_value()

def change_status():
    ip = socket.gethostbyname(socket.gethostname())
    zk = ZK(CONF.zk_address)
    path = CONF.host_path + "/" + ip
    root = zk.get_node(path)
    status_node = root.get_child("status")
    if "init" == status_node.get_value():
        status_node.set_value("idle")

    # 管理数据下载、删除和汇报
def data():
    try:
        id = get_id()
        if not id or "" == id:
            CONF.log.error("无法获取机器id")
            return False
        data_list = []
        daily = DailyData(int(id))
        userdefine = UserDefineData(int(id))
        temp = TempData()
        data_list.append(daily)
        #data_list.append(userdefine)
        #data_list.append(temp)
    except:
        CONF.log.exception("exception in data")
    while True:
        try:
            ip = socket.gethostbyname(socket.gethostname())
            zk = ZK(CONF.zk_address)
            path = CONF.host_path + "/" + ip
            root = zk.get_node(path)
            query_node = None
            if not root.has_child("query"):
                query_node = root.add_child("query")
            else:
                query_node = root.get_child("query")
        except:
            CONF.log.exception("exception in data")
        query = {}
        for data in data_list:
            try:
                data.download()
                data.delete()
                data_query = data.report()
                query = dict(query, **data_query)
            except:
                CONF.log.exception("exception in data")
        query_node.set_value(json.dumps(query))
        time.sleep(60)

def start_manager(pid_file):
    file = open(pid_file, "w")
    pid = os.getpid()
    file.write(str(pid))
    file.close()
    multiprocessing.Process(target=work, args=()).start()
    #multiprocessing.Process(target=data, args=()).start()
    std_file = open(CONF.log_file, "w+")
    sys.stdout = std_file
    sys.stderr = std_file
    app = AgentApplication(urls, globals())
    port = 9090
    app.run(port)
