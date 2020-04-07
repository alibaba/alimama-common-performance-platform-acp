#coding:utf-8
import json
import socket
import time
from zk import *
from util import *
import subprocess
import psutil
import os
import re

class Agent:

    def __init__(self, zk, host, task_id, agent_id):
        self.zk = zk
        self.host = host
        self.task_id = task_id
        self.agent_id = agent_id
        self.pid = 0
        self.info = self.get_info_from_zk()

    def get_info_from_zk(self):
        path = CONF.task_path + "/" + self.task_id
        root = self.zk.get_node(path)
        resource_node = root.get_child("resource")
        host_node = resource_node.get_child(self.host)
        agent_node = host_node.get_child(self.agent_id)
        info_node = agent_node.get_child("info")
        info = json.loads(info_node.get_value())
        CONF.log.debug("get_info_from_zk: [%s]" % info)
        return info

    def delete_in_zk(self):
        path = CONF.task_path + "/" + self.task_id
        root = self.zk.get_node(path)
        lock = root.get_lock()
        lock.acquire(timeout=0.002)
        resource_node = root.get_child("resource")
        host_node = resource_node.get_child(self.host)
        agent_node = host_node.get_child(self.agent_id)
        agent_node.delete()
        lock.release()

    def is_alive(self):
        if 0 == self.pid:
            return False
        if self.pid in psutil.pids():
            return True
        else:
            return False

    def heartbeat(self, alive):
        path = CONF.task_path + "/" + self.task_id
        root = self.zk.get_node(path)
        resource_node = root.get_child("resource")
        host_node = resource_node.get_child(self.host)
        agent_node = host_node.get_child(self.agent_id)
        if agent_node.has_child("heartbeat"):
            if not alive:
                heartbeat_node = agent_node.get_child("heartbeat")
                heartbeat_node.delete()
        else:
            if alive:
                agent_node.add_child("heartbeat")

    def record_error_to_zk(self, err_msg):
        path = CONF.task_path + "/" + self.task_id
        root = self.zk.get_node(path)
        resource_node = root.get_child("resource")
        host_node = resource_node.get_child(self.host)
        agent_node = host_node.get_child(self.agent_id)
        agent_node.set_value(err_msg)

    def start(self):
        pass

    def stop(self):
        if not self.is_alive():
            return False
        p = psutil.Process(self.pid)
        children = p.children(True)
        for child in reversed(children):
            child.kill()
        p.kill()
        return True

    def output(self):
        return ""

    def change_qps(self, qps):
        pass

    def monitor_zk(self):
        info = self.get_info_from_zk()
        if info.has_key("qps"):
            current_qps = 0
            if self.info.has_key("qps"):
                current_qps = self.info["qps"]
            if current_qps != info["qps"]:
                self.change_qps(info["qps"])
                self.info["qps"] = info["qps"]

    def output_to_zk(self):
        output = self.output()
        if 0 == len(output):
            return
        path = CONF.task_path + "/" + self.task_id
        root = self.zk.get_node(path)
        resource_node = root.get_child("resource")
        host_node = resource_node.get_child(self.host)
        agent_node = host_node.get_child(self.agent_id)
        output_node = agent_node.get_child("output")
        output_node.set_value(output)

    def check(self):
        return True
        ### you can activate below code if you have uncomment data() function
        query_path = self.info["query_path"]
        if os.path.exists(query_path):
            if os.path.isdir(query_path):
                for key in CONF.data_number:
                    dir_path = "./data/" + CONF.data_number[key]
                    if os.path.samefile(dir_path, query_path):
                        for file in os.listdir(data_dir):
                            path = query_path + "/" + file
                            pattern = "^" + CONF.data_number[key] + "-\d{8}"
                            if os.path.isfile(path) and len(re.findall(pattern, dir)) > 0:
                                data_list.append(path)
                        if len(data_list) > 0:
                            self.info["query_path"] = data_list[-1]
                            self.record_error_to_zk(data_list[-1])
                            return True
                        else:
                            self.record_error_to_zk("%s has no data" % query_path)
                            CONF.log.error("%s has no data" % query_path)
                            return False
                self.record_error_to_zk("%s is not data dir" % query_path)
                CONF.log.error("%s is not data dir" % query_path)
            else:
                return True
        else:
            self.record_error_to_zk("%s not exist" % query_path)
            CONF.log.error("%s not exist" % query_path)
            return False

class AbenchAgent(Agent):

    def start(self):
        CONF.log.debug("entry AbenchAgent start")
        target = self.info["target"]
        qps = self.info["qps"]
        ip = target.split(":")[0]
        port = target.split(":")[1]
        path = self.info["query_path"]
        agent_id = int(self.agent_id.split("_")[1])

        # 处理cmd_options
        cmd_options = ""
        try:
            option = json.loads(self.info["option"])
            if option.has_key("cmdOptions"):
                cmd_options = option["cmdOptions"]
        except:
            CONF.log.exception("parse cmd_options fail")

        cmd = "./tools/piemon/piemon -d %s -r %s -s 100000000 --http -k %s %s %s %s" % (agent_id, qps, ip, port, path, cmd_options)

        cmd_list = cmd.split(" ")
        CONF.log.debug("AbenchAgent: [%s] [%s]" % (qps, self.info))
        CONF.log.error("cmd_list: [%s]" % cmd)
        null_file = open(os.devnull, "r+")
        child = subprocess.Popen(cmd_list, stdout=null_file, stderr=null_file, stdin=null_file)
        self.pid = child.pid
        CONF.log.debug("end start [%d]" % self.pid)

    def change_qps(self, qps):
        agent_id = int(self.agent_id.split("_")[1])
        cmd = "./tools/piemon/new %s %s > /dev/null 2>&1" % (qps, agent_id)
        child = subprocess.Popen(cmd, shell=True)
        child.wait()

class otherAgent(Agent):

    def start(self):
        CONF.log.debug("entry otherAgent start")
        target = self.info["target"]
        qps = self.info["qps"]
        ip = target.split(":")[0]
        port = target.split(":")[1]
        path = self.info["query_path"]
        agent_id = int(self.agent_id.split("_")[1])

        # 处理cmd_options
        cmd_options = ""
        try:
            option = json.loads(self.info["option"])
            if option.has_key("cmdOptions"):
                cmd_options = option["cmdOptions"]
        except:
            CONF.log.exception("parse cmd_options fail")

        cmd = "./tools/piemon/piemon -d %s -r %s -s 100000000 --post -k %s %s %s %s" % (agent_id, qps, ip, port, path, cmd_options)
        cmd_list = cmd.split(" ")
        CONF.log.debug("cmd_list: [%s]" % cmd_list)
        null_file = open(os.devnull, "r+")
        child = subprocess.Popen(cmd_list, stdout=null_file, stderr=null_file, stdin=null_file)
        self.pid = child.pid
        CONF.log.debug("end start [%d]" % self.pid)

    def change_qps(self, qps):
        agent_id = int(self.agent_id.split("_")[1])
        cmd = "./tools/piemon/new %s %s > /dev/null 2>&1" % (qps, agent_id)
        child = subprocess.Popen(cmd, shell=True)
        child.wait()

