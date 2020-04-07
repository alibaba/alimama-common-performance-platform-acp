import web
import time
import imp
import json
import sys
import os
import re
import socket
import traceback
import threading
import urllib2
import subprocess
from lib.util.shellcommand import Shell
from framework.serviceplugin import ServiceFactory,loadOnePluginConfig,loadAllPluginsConfig
from conf.ServiceConfig import ServiceConfig
from lib.util.getuserauth import getUserAuth

urls = (
    '/(.*)', 'WebService'
)

def callRemoteService(host, url, global_info):
    try:
        page=urllib2.urlopen(url)
        line = page.read()
        page.close()
        print line
        global_info[host]=json.loads(line)
    except Exception,ex:
        global_info[host] =  str(ex)

gHeartbeatServices = {} # heatbeat servicefor monitor
class WebService:  
    __plugins = {}
    __services = {}

    def getPlugins(self):
        return self.__plugins

    def loadAllPlugins(self, pluginsDir):
        configArrs = loadAllPluginsConfig(pluginsDir);
        for compConfig in configArrs:
            self.__plugins[compConfig['name']] = ServiceFactory(compConfig)

    def GET(self, name):
        global gHeartbeatServices

        data = web.input()
      
        #if specified hosts, then will call remote hosts service
        if data.has_key("hosts"):

            web_hosts = data['hosts'].split(',');

            params = ""
            for key,value in data.items():
                if key=="hosts":
                    continue
                params += key + "=" + urllib2.quote(value.encode('utf-8')) + "&"
            params = params.rstrip("&")

            urllib2.socket.setdefaulttimeout(600)
            global_info = {}
            thread_pool = []
            for web_host in web_hosts:
                temp_arr = web_host.split(":")
                host = temp_arr[0]
                port = "9090"
                if len(temp_arr)==2:
                    port = temp_arr[1]

                url = "http://"+host+":"+port+"/"+name+"?"+params
                
                t = threading.Thread(target=callRemoteService,args=(host, url, global_info)) 
                thread_pool.append(t)
                t.start()

            for t in thread_pool:
                threading.Thread.join(t)

            return json.dumps(global_info)

        # if specified user and password, get the authority infomation for the plugins

        os.environ['USERINPUT'] = "";
        os.environ['USERGROUP'] = "";
        if data.has_key("user") and data.has_key("password"):
            (user,group,msg) = getUserAuth(data['user'],data['password'])
            if user==None:
                return msg
            del data['user']
            del data['password']
            os.environ['USERINPUT'] = user
            os.environ['USERGROUP'] = group

        if name=="query": # query service
            self.__services[ServiceConfig['name']] = ServiceConfig 
            self.loadAllPlugins("plugins/")
            ServiceConfig['plugins'] = loadAllPluginsConfig("plugins/")
            jsonStr = json.dumps(self.__services)
            if data.has_key("callback"):
                jsonStr = data['callback'] + "(" + jsonStr +")"
            return jsonStr

        if name=="system":
            if not data.has_key("cmd"):
                return '{"status":"failed","ret_info":"need parameter cmd!!!"}'
            cmd = Shell(data["cmd"])
            cmd.run()
            ret_info = urllib2.quote(cmd.ret_info.encode('utf-8'))
            err_info = urllib2.quote(cmd.err_info.encode('utf-8'))
            return '{"status":"ok","ret_code":%d,"ret_info":"%s","err_info":"%s"}'%(cmd.ret_code,ret_info,err_info)


        if name=="heartbeat": #heartbeat service
            if not data.has_key("info"):
                return '{"status":"fail", "msg":"no info pramaters!"}'
            try:
                serviceDict = json.loads(data['info'])
            except Exception,e:
                return '{"status":"fail", "msg":"info is not a json string:%s"}'%data['info']
            if not serviceDict.has_key('name'):
                return '{"status":"fail", "msg":"info must has a name key:%s"}'%data['info']
            serviceDict['updatetime'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
            self.__services[serviceDict['name']] = serviceDict
            # record global service of heart beat. for monitor
            gHeartbeatServices[serviceDict['name']]  = serviceDict
            print gHeartbeatServices
            return '{"status":"ok", "msg":"the service is updated"}'


        if not self.__plugins.has_key(name):
            try:
                self.loadAllPlugins("plugins/")
            except Exception,e:
                return "updated plugins failed!"+traceback.format_exc()

        # local services
        if self.__plugins.has_key(name):
            ret_code1,ret_info1,err_info1 = self.__plugins[name].run(json.dumps(data),data)
            #return  err_info1
            if name == 'getdetail' or name =='createtask' or name =='updatetask' or name =='getalltask' or name =='stoptask' or name =='getquota':
                return ret_info1
            ret_info = urllib2.quote(ret_info1.encode('utf-8'))
            err_info = urllib2.quote(err_info1.encode('utf-8'))
            if name == 'getCurrentStatus' or name == 'getlist' or name == 'getdetail' or name == 'swift' or name == 'gamma' or name=='gammadiff' or name == 'gammadiff2' or name == 'gammatasklist' or name == 'gammatasklist2' or name == 'gammadifftwins' or name == 'gammatasklist3' or name == 'writezkforadf' or name == 'readzkforadf' or name == 'runErpc':
                return ret_info1
            else:
                jsonStr = '{"qps":200}'
                return '{"msg":"","code":200,"fields":%s,"errorMsg":"","errorCode":200,"success": true,"status":"ok", "ret_code":%d, "ret_info":"", "err_info":"%s"}'%(jsonStr,ret_code1,err_info)
        return "%s do not exist or other error happend!"

    def POST(self, name):
        if not self.__plugins.has_key(name):
            self.__plugins[name] = self.loadOnePlugin("plugins/"+name)

        data = web.input()
        if self.__plugins.has_key(name):
             return self.__plugins[name].run(json.dumps(data),data)

def heartBeat():
    while 1:
        ServiceConfig['plugins'] = loadAllPluginsConfig("plugins/")
        jsonStr = urllib2.quote(json.dumps(ServiceConfig))
        url = "http://"+ServiceConfig['heartbeatserver']+"/heartbeat?info="+jsonStr
        #page=urllib2.urlopen("http://"+ServiceConfig['heartbeatserver']+"/heartbeat?info="+jsonStr)
        page=urllib2.urlopen(url)
        line = page.read()
        page.close()
        print line
        time.sleep(30)
def monitor():
    global gHeartbeatServices
    
    while 1:
       #print "monitor"
       #print gHeartbeatServices
       time.sleep(10)

if __name__ == "__main__":
    try:
        port = sys.argv[1]
    except:
        port = "8080"
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    ServiceConfig['address'] = "http://"+ip+":"+port+"/"
    # start heart beat thread
    if ServiceConfig['heartbeatserver'] != "":
        t = threading.Thread(target=heartBeat, args=())
        t.start()
    gHeartbeatServices = {"global":{"name":"gobal", "newsn":"yes"}}
    t = threading.Thread(target=monitor, args=())
    t.start()

    # start monitor thread
    app = web.application(urls, globals())
    app.run()
