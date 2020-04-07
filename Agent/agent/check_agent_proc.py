#coding:utf-8
import psutil
from util import *
import time
import subprocess

def check():
    target_proc = "agent_ctrl.py"
    count = 0
    for proc in psutil.process_iter():
        cmd = " ".join(proc.cmdline())
        if cmd.find(target_proc) != -1:
            count += 1
    # 一个主进程+work进程+data进程
    if count < 3:
        return False
    else:
        return True

def stop():
    cmd = "../python2.7.6/bin/python ./agent_ctrl.py stop"
    CONF.log.error("try to stop abnormal agent")
    subprocess.Popen(cmd.split(), shell=False)

def start():
    cmd = "../python2.7.6/bin/python ./agent_ctrl.py start"
    CONF.log.error("try to start agent")
    subprocess.Popen(cmd.split(), shell=False)

if __name__ == "__main__":
    if not check():
        stop()
        time.sleep(5)
        start()
