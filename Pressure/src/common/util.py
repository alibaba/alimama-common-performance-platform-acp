import logging
import os
import ConfigParser

class Conf:

    def __init__(self):
        # [log]
        path = os.path.split(os.path.realpath(__file__))[0] + "/../../"
        config = ConfigParser.ConfigParser()
        config.read(path+"/conf/acp-pressure.conf")

        log_path = path + "log/" + config.get("log", "name")
        log_level_dict = {"NOTSET": logging.NOTSET, "DEBUG": logging.DEBUG, "INFO": logging.INFO, "WARNING": logging.WARNING, "ERROR": logging.ERROR, "CRITICAL": logging.CRITICAL}
        log_level = log_level_dict[config.get("log", "level")]
        handler = logging.FileHandler(log_path)
        handler.setLevel(log_level)
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] [%(filename)s] [%(funcName)s:%(lineno)d] -- %(message)s")
        handler.setFormatter(formatter)

        self.log = logging.getLogger("acp-pressure")
        self.log.addHandler(handler)
        self.log.setLevel(log_level)

        # [zk]
        self.zk_address = config.get("zk", "address")
        self.root = config.get("zk", "root")
        self.task_path = config.get("zk", "task")
        self.host_path = config.get("zk", "host")

        # [resource]
        self.resource = {}
        for option in config.options("resource"):
            self.resource[option] = config.getint("resource", option)
        self.maxqps = {}
        for option in config.options("max qps"):
            self.maxqps[option] = config.getint("max qps", option)

        # [press host]
        self.press_hosts = []
        for hostname in config.get("press host","hosts").split(","):
            self.press_hosts.append(hostname.strip())

        # [health monitor]
        self.monitor_failure_log = os.path.join(path,"log",config.get("health monitor","failure_log"))

CONF = Conf()
