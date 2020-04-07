import logging
import os
import ConfigParser

class Conf:

    def __init__(self):
        # [log]
        config = ConfigParser.ConfigParser()
        path = os.path.split(os.path.realpath(__file__))[0]
        config.read(path+"/agent.conf")
        log_path = path + "/log/" + config.get("log", "name")
        self.log_file = log_path
        log_level_dict = {"NOTSET": logging.NOTSET, "DEBUG": logging.DEBUG, "INFO": logging.INFO, "WARNING": logging.WARNING, "ERROR": logging.ERROR, "CRITICAL": logging.CRITICAL}
        log_level = log_level_dict[config.get("log", "level")]
        handler = logging.FileHandler(log_path)
        handler.setLevel(log_level)
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] [%(filename)s] [%(funcName)s:%(lineno)d] -- %(message)s")
        handler.setFormatter(formatter)
        self.log = logging.getLogger("agent")
        self.log.addHandler(handler)
        self.log.setLevel(log_level)
        # [zk]
        self.zk_address = config.get("zk", "address")
        self.task_path = config.get("zk", "task")
        self.host_path = config.get("zk", "host")
        # [agent_type]
        self.agent_type = {}
        for option in config.options("agent_type"):
            self.agent_type[option] = config.get("agent_type", option)
        # [data_number]
        self.data_number = {}
        for option in config.options("data_number"):
            self.data_number[option] = config.get("data_number", option)
        # [data]
        self.hdfs = config.get("data", "hdfs")
        self.keep_number = config.get("data", "keep_number")
        self.ignore_number = []
        for num in config.get("data", "ignore_number").split(","):
            self.ignore_number.append(num)

CONF = Conf() 
