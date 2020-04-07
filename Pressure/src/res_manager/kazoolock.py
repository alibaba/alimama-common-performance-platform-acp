import os, time
from kazoo.client import KazooClient
from kazoo.client import KazooState
from kazoo.recipe.lock import Lock
from common.util import *

class ZooKeeperLock():
    def __init__(self, hosts, lock_name, lock_path):
        self.hosts = hosts
        self.zk_client = None
        self.name = lock_name
        self.lock_path = lock_path
        self.lock_handle = None
        self.create_lock()

    def create_lock(self):
        try:
            self.zk_client = KazooClient(hosts=self.hosts)
            self.zk_client.start()
        except Exception, ex:
            self.init_ret = False
            self.err_str = "Create KazooClient failed! Exception: %s" % str(ex)
            print self.err_str
            return
        try:
            self.lock_handle = Lock(self.zk_client, self.lock_path)
        except Exception, ex:
            self.init_ret = False
            self.err_str = "Create lock failed! Exception: %s" % str(ex)
            CONF.log.exception(self.err_str)
            return

    def destroy_lock(self):
        #self.release()
        if self.zk_client != None:
            self.zk_client.stop()
            self.zk_client = None

    def acquire(self, blocking=True, timeout=None):
        if self.lock_handle == None:
            raise Exception("lock_handle is None")
        try:
            return self.lock_handle.acquire(blocking=blocking, timeout=timeout)
        except Exception, ex:
            self.err_str = "Acquire lock failed! Exception: %s" % str(ex)
            CONF.log.exception(self.err_str)
            return None

    def release(self):
        if self.lock_handle == None:
            return None
        return self.lock_handle.release()

    def __del__(self):
#        print "Enter ZooKeeperLock.__del__()"
#        self.destroy_lock()
#        print "Exit ZooKeeperLock.__del__()"
        pass

#################################
# Test
def main():
    zookeeper_hosts = "10.103.84.140:2181"
#    lock_name = "kazoo_test_lock"
#    lock_path = "/acp/test_lock"
    lock_name = "luofan"
    lock_path = "/acp/host/lock"
    lock = ZooKeeperLock(zookeeper_hosts, lock_name, lock_path)
    ret = lock.acquire()

    if not ret:
        print "Can't get lock! Ret: %s", ret
        return
    print "Get lock! Do something! Sleep 10 secs!"
    for i in range(1, 11):
        time.sleep(1)
        print str(i)

    lock.release()

if __name__ == "__main__":
    try:
        main()
    except Exception, ex:
        print "Ocurred Exception: %s" % str(ex)
        quit()
