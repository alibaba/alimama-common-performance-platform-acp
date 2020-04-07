from kazoo.client import KazooClient
from kazoo.recipe.lock import Lock
import time

class ZK:

    client = None

    def __init__(self, zk_host):
        self.client = KazooClient(zk_host)
        self.client.start()

    def __del__(self):
        self.client.stop()

    def get_node(self, path):
        if not self.client.exists(path):
            return None
        node = ZKNode(path, self)
        return node

    def create_node(self, path):
        self.client.ensure_path(path)
        return self.get_node(path)

    def get_transaction(self):
        return self.client.transaction()

    def get_lock(self, path, id=None):
        return self.client.Lock(path+"/lock", id)

    def has_lock(self, path):
        lock_path = path + "/lock"
        if not self.client.exists(lock_path):
            return False
        if len(self.client.get_children(lock_path)) > 0:
            return True
        else:
            return False

class ZKNode:

    path = ""
    zk = None

    def __init__(self, path, zk):
        self.path = path
        self.zk = zk

    def get_name(self):
        return self.path.split("/")[-1]

    def get_value(self):
        return self.zk.client.get(self.path)[0]

    def get_stat(self):
        return self.zk.client.get(self.path)[1]

    def get_lock(self, id=None):
        return self.zk.get_lock(self.path, id)

    def has_lock(self):
        return self.zk.has_lock(self.path)

    def get_child(self, name):
        child_path = self.path + "/" + name
        if self.zk.client.exists(child_path):
            node = ZKNode(child_path, self.zk)
            return node
        else:
            return None

    def has_child(self, name):
        child_path = self.path + "/" + name
        if self.zk.client.exists(child_path):
            return True
        else:
            return False

    def list_children(self):
        if self.has_lock():
            return None
        node_list = []
        for name in self.zk.client.get_children(self.path):
            child_path = self.path + "/" + name
            node = ZKNode(child_path, self.zk)
            if not node.has_lock():
                node_list.append(node)
        return node_list

    def set_value(self, value):
        self.zk.client.set(self.path, str(value))

    def add_child(self, name, value="", transaction=None):
        path = self.path + "/" + name
        if transaction:
            transaction.create(path, value)
        else:
            self.zk.client.create(path, value)
        node = ZKNode(path, self.zk)
        return node

    def delete(self):
        self.zk.client.delete(self.path, recursive=True)

