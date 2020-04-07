#coding=utf-8
import sys
import os
import signal
path = os.path.split(os.path.realpath(__file__))[0]
sys.path.append(path+"/../src")
from schedule.schedule import *

def get_pid(pid_file):
    if not os.path.exists(pid_file):
        return None

def daemonize():
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError, e:
        print "daemonize fork#1 failed: (%d) %s\n" % (e.errno, e.strerror)
        sys.exit(1)
    os.umask(0)
    os.setsid()
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError, e:
        print "daemonize fork#2 failed: (%d) %s\n" % (e.errno, e.strerror)
        sys.exit(1)

if __name__ == "__main__":
    pid_file = "./schedule.pid"
    if len(sys.argv) != 2:
        print sys.argv[0] + " [start|stop]"
        sys.exit(1)
    op = sys.argv[1]
    pid = get_pid(pid_file)
    if op == "start":
        if pid:
            print "schedule already exists"
        else:
            daemonize()
            schedule(pid_file)
    elif op == "stop":
        if not pid:
            print "schedule does not exist"
        else:
            os.kill(int(pid), signal.SIGTERM)
    else:
        print sys.argv[0] + " [start|stop]"
