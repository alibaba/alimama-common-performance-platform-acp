#coding:utf-8
import commands
import subprocess
from util import *
from datetime import *
import time
import re
import os

def exe_cmd(cmd):
    child = subprocess.Popen(cmd.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (out, err) = child.communicate() 
    if len(err) > 0:
        CONF.log.error(cmd)
        CONF.log.error(err)
    return out.strip()

class Data:

    def __init__(self):
        self.hdfs_path = CONF.hdfs
        self.keep_number = CONF.keep_number
        self.ignore_number = CONF.ignore_number
        self.data_dir = ""
        self.type = ""

    def list(self):
        pass

    # 检查当前机器上是否存在data文件
    def check(self, path):
        if os.path.exists(path):
            return True
        else:
            return False

    def download(self):
        pass

    # 汇报当前机器上已有的data文件
    def report(self):
        data_list = {}
        if "" == self.data_dir or "" == self.type:
            return data_list
        data_list[self.type] = []
        for dir in os.listdir(self.data_dir):
            path = os.path.abspath(self.data_dir + dir)
            if os.path.isfile(path) and not dir.startswith(".") and not dir.endswith("_COPYING_"):
                data_list[self.type].append(path)
        return data_list

    # 删除超过保留个数的data文件
    def delete(self):
        pass

class TempData(Data):

    def __init__(self):
        Data.__init__(self)
        self.data_dir = "./data/temp/"
        self.type = "temp"

    def list(self):
        temp_data = []
        # use your own hadoop path
        cmd = "/home/admin/hadoop/bin/hadoop fs -ls %s" % (self.hdfs_path + "/tmp")
        output = exe_cmd(cmd)
        if len(output) > 0:
            head_flag = True
            for line in output.split("\n"):
                if head_flag:
                    head_flag = False
                    continue
                if line.endswith("_COPYING_"):
                    continue
                fields = line.split()
                if len(fields) < 8:
                    CONF.log.error("hadoop return error")
                    continue
                type = fields[0][0]
                path = fields[7]
                if "-" != type:
                    CONF.log.error("%s is not a file" % path)
                    continue
                index = path.rfind("/")
                name = path[index+1:]
                temp_data.append((path, name))
        return temp_data

    def download(self):
        data_list = self.list()
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        for (path, name) in data_list:
            if self.check(self.data_dir + name):
                continue
            else:
                cmd = "/home/admin/hadoop/bin/hadoop fs -get %s %s" % (path, self.data_dir + name)
                #exe_cmd(cmd)

class UserDefineData(Data):

    def __init__(self, id):
        Data.__init__(self)
        self.data_dir = "./data/userdefine/"
        self.type = "userdefine"
        self.id = id

    def list(self):
        userdefine_data = []
        cmd = "/home/admin/hadoop/bin/hadoop fs -ls %s" % self.hdfs_path
        output = exe_cmd(cmd)
        if len(output) > 0:
            head_flag = True
            for line in output.split("\n"):
                if head_flag:
                    head_flag = False
                    continue
                if line.endswith("_COPYING_"):
                    continue
                fields = line.split()
                if len(fields) < 8:
                    CONF.log.error("hadoop return error")
                    continue
                type = fields[0][0]
                path = fields[7]
                index = path.rfind("/")
                full_name = path[index+1:]
                pattern = "^\d{8}-\d{1,3}-userdefine-\d{10}$"
                results = re.findall(pattern, full_name)
                if 0 == len(results):
                    continue
                if "d" != type:
                    CONF.log.error("%s is not a directory" % path)
                    continue
                name_fields = full_name.split("-")
                name_number = name_fields[1]
                if name_number in CONF.ignore_number:
                    continue
                if not CONF.data_number.has_key(name_number):
                    CONF.log.error("未定义的编号%s: %s" % (name_number, full_name))
                else:
                    name = CONF.data_number[name_number] + "-" + name_fields[-1]
                userdefine_data.append((path, name))
        return userdefine_data

    def download(self):
        data_list = self.list()
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        for (path, name) in data_list:
            if self.check(self.data_dir + name):
                continue
            else:
                # 获得需要下载的part文件名
                cmd = "/home/admin/hadoop/bin/hadoop fs -ls %s" % path
                output = exe_cmd(cmd)
                if 0 == len(output):
                    continue
                part_list = []
                head_flag = True
                for line in output.split("\n"):
                    if head_flag:
                        head_flag = False
                        continue
                    fields = line.split()
                    if len(fields) < 8:
                        CONF.log.error("hadoop return error")
                        continue
                    part_path = fields[7]
                    index = part_path.rfind("/")
                    part_name = part_path[index+1:]
                    if part_name.startswith("part-"):
                        part_list.append(part_path)
                if 0 == len(part_list):
                    CONF.log.error("未发现part文件: %s" % path)
                    continue
                number = self.id % len(part_list)
                download_path = path + "/part-" + str(number)
                if download_path not in part_list:
                    CONF.log.error("%s不存在" % download_path)
                    continue
                # 下载part文件
                download_cmd = "/home/admin/hadoop/bin/hadoop fs -get %s %s" % (download_path, self.data_dir + name)
                exe_cmd(download_cmd)

class DailyData(Data):

    def __init__(self, id):
        Data.__init__(self)
        self.data_dir = "./data/"
        self.id = id

    def list(self):
        daily_data = {}
        today_date = datetime.today()
        cmd = "/home/admin/hadoop/bin/hadoop fs -ls %s" % self.hdfs_path
        output = exe_cmd(cmd)
        if len(output) > 0:
            head_flag = True
            for line in output.split("\n"):
                if head_flag:
                    head_flag = False
                    continue
                if line.endswith("_COPYING_"):
                    continue
                fields = line.split()
                type = fields[0][0]
                if len(fields) < 8:
                    CONF.log.error("hadoop return error")
                    continue
                path = fields[7]
                index = path.rfind("/")
                full_name = path[index+1:]
                pattern = "^\d{8}-\d{1,3}$"
                results = re.findall(pattern, full_name)
                if 0 == len(results):
                    continue
                if "d" != type:
                    CONF.log.error("%s is not a directory" % path)
                    continue
                name_fields = full_name.split("-")
                name_date = name_fields[0]
                name_number = name_fields[1]
                if name_number in CONF.ignore_number:
                    continue
                if not CONF.data_number.has_key(name_number):
                    CONF.log.error("未定义的编号%s: %s" % (name_number, full_name))
                    continue
                data_type = CONF.data_number[name_number]
                name = data_type + "-" + name_date
                if daily_data.has_key(data_type):
                    daily_data[data_type].append((name_date, path, name))
                else:
                    daily_data[data_type] = [(name_date, path, name)]
            for key in daily_data:
                if len(daily_data[key]) > int(self.keep_number):
                    daily_data[key].sort(key=lambda e:e[0], reverse=True)
                    daily_data[key] = daily_data[key][0:int(self.keep_number)]
        return daily_data

    def download(self):
        data_dict = self.list()
        for key in data_dict:
            data_dir = self.data_dir + key + "/"
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
            for (name_date, path, name) in data_dict[key]:
                if self.check(data_dir + name):
                    continue
                else:
                    # 获得需要下载的part文件名
                    cmd = "/home/admin/hadoop/bin/hadoop fs -ls %s" % path
                    output = exe_cmd(cmd)
                    if 0 == len(output):
                        continue
                    part_list = []
                    head_flag = True
                    for line in output.split("\n"):
                        if head_flag:
                            head_flag = False
                            continue
                        fields = line.split()
                        if len(fields) < 8:
                            CONF.log.error("hadoop return error")
                            continue
                        part_path = fields[7]
                        index = part_path.rfind("/")
                        part_name = part_path[index+1:]
                        if part_name.startswith("part-"):
                            part_list.append(part_path)
                    if 0 == len(part_list):
                        CONF.log.error("未发现part文件: %s" % path)
                        continue
                    number = self.id % len(part_list)
                    dataId = int(path.split("-")[1])
                    CONF.log.error("current name_data: %s      path: %s     name: %s   id: %s" %(name_date,path,name,path.split("-")[1]))
                    CONF.log.error("current PART_LIST:: %s" % str(len(part_list)))
                    checkList = [1,2,3,4,5]  # define your own checkList
                    part_num = 15
                    if dataId in checkList and len(part_list) !=part_num:
                        CONF.log.error("强校验数据part数未达到预期数目: %s" %(str(len(part_list)))) 
                        continue
                    else:
                        CONF.log.error("强校验通过或不需要校验,开始下载数据,id: %s" %(str(dataId)))
                    download_path = path + "/part-" + str(number)
                    if download_path not in part_list:
                        CONF.log.error("%s不存在" % download_path)
                        continue
                    # 下载part文件
                    download_cmd = "/home/admin/hadoop/bin/hadoop fs -get %s %s" % (download_path, data_dir + name)
                    exe_cmd(download_cmd)

    def report(self):
        data_list = {}
        for key in CONF.data_number:
            data_dir = self.data_dir + CONF.data_number[key] + "/"
            if not os.path.exists(data_dir):
                continue
            for dir in os.listdir(data_dir):
                path = os.path.abspath(data_dir + dir)
                pattern = "^" + CONF.data_number[key] + "-\d{8}"
                if os.path.isfile(path) and len(re.findall(pattern, dir)) > 0:
                    if data_list.has_key(CONF.data_number[key]):
                        data_list[CONF.data_number[key]].append(path)
                    else:
                        data_list[CONF.data_number[key]] = [path]
        return data_list

    def delete(self):
        for key in CONF.data_number:
            data_list = []
            data_dir = self.data_dir + CONF.data_number[key] + "/"
            if not os.path.exists(data_dir):
                continue
            for dir in os.listdir(data_dir):
                path = os.path.abspath(data_dir + dir)
                pattern = "^" + CONF.data_number[key] + "-\d{8}"
                if os.path.isfile(path) and len(re.findall(pattern, dir)) > 0:
                    data_list.append(path)
            diff_count = len(data_list) - int(self.keep_number)
            if diff_count > 0:
                data_list.sort()
                for file in data_list[0:diff_count]:
                    try:
                        os.remove(file)
                    except e:
                        CONF.log.error("delete失败: %s" % e)
        
if __name__ == "__main__":
    pass
