# coding:utf-8
from agentManager import *
import psutil
import signal

def get_pid(pid_file):
    if not os.path.exists(pid_file):
        return None
    file = open(pid_file, "r")
    pid = file.read().strip()
    file.close()
    if not pid or pid == "":
        return None
    if int(pid) in psutil.pids():
        return pid
    else:
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

def kill_all(pid):
    p = psutil.Process(int(pid))
    children = p.children(True)
    for child in reversed(children):
        child.kill()
    p.kill()

if __name__ == "__main__":
    pid_file = "./agent_manager.pid"
    if len(sys.argv) != 2:
        print sys.argv[0] + " [start|stop]"
        sys.exit(1)
    op = sys.argv[1]
    pid = get_pid(pid_file)
    if op == "start":
        if pid:
            print "agentManager already exists"
        else:
            daemonize()
            # ignore SIGCHLD to avoid defunct child process
            signal.signal(signal.SIGCHLD, signal.SIG_IGN)
            start_manager(pid_file)
    elif op == "stop":
        if not pid:
            print "agentManager does not exist"
        else:
            kill_all(pid)
    else:
        print sys.argv[0] + " [start|stop]"
