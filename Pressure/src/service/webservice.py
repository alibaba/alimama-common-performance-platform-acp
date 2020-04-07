import web
import logging
import json
import sys
import traceback
sys.path.append('..')
import time,md5,re
from task.task import Task
from host.host import *

render = web.template.render('templates', base='layout')
 
urls = (
    '/favicon.ico$','Api',
    '/(.*).html', 'WebPage',
    '/(.*)', 'Api'
)

class WebPage:
    def GET(self, name=None):
        data = web.input()
        title = "no title"
        func = eval('render.'+name)
        return func()

def checkToken(func):
    def _func(*argv,**kwgs):
        data = argv[1]
        if data.has_key('token') == False or data.has_key('timestamp') == False:
            return json.dumps({'code':'false','res':'','desc':'Token Fail'})
        if( ( int(time.time()*1000) - int(data['timestamp']) ) < 6000 ):
            cT = md5.new()
            cT.update(str(data['timestamp']) + Api.key)
            if(data['token'] == cT.hexdigest()):
                return func(*argv,**kwgs)
        return json.dumps({'code':'false','res':'','desc':'Token Fail'})
    return _func
    
class Api:
    key = 'xilj438jg09hl1-340';
    res = {'code':'true','res':'','desc':''}

    def GET(self, name=None):
        try:
            data = web.input()
            logging.info("request: name=%s, param=%s"%(name,data))
            func = eval('self.'+name+'_action')
            return func(data)
        except Exception, e:
            logging.exception("get exception")
            return json.dumps({'code':'false','res':'','desc':e.message})

    def POST(self, name=None):
        try:
            data = web.data()
            func = eval('self.'+name+'_action')
            return func(json.loads(data))
        except Exception, e:
            logging.exception("post exception")
            return json.dumps({'code':'false','res':'','desc':e.message})

    def getToken(self, timestamp):
        token = md5.new()
        token.update(str(timestamp) + self.key)
        return token.hexdigest()

    #@checkToken
    def test_action(self, data):
        return json.dumps(data)

    def taskList_action(self, data):
        list = Task.get_all_task()
        result = []
        for task in list:
            task_dict = task.__dict__
            task_dict["agentList"] = []
            for agent in task.get_all_agent():
                agent_dict = agent.__dict__
                agent_dict["heartbeat"] = agent.heartbeat()
                task_dict["agentList"].append(agent_dict)
            result.append(task_dict)
        self.res['res'] = result
        return json.dumps(self.res)

    def resource_action(self, data):
        host_list = Host.get_all_host()
        result = []
        for host in host_list:
            host_dict = host.__dict__
            host_dict["query"] = ""
            host_dict["agentList"] = host.get_agent_in_zk()
            result.append(host_dict)
        self.res['res'] = result
        return json.dumps(self.res)

    def queryList_action(self, data):
        try:
            query_set = Host.get_query_list()
            return json.dumps(query_set)
        except Exception,e:
            return str(e)

    #@checkToken
    def create_action(self, data):
        if not data.has_key("target") or not data.has_key("qps") or not data.has_key("query_path") or not data.has_key("source") or not data.has_key("query_type") or not data.has_key("option"):
            return json.dumps({'code':'false','res':'','desc':'lark of parameters: target, qps, query_path, source, query_type or option'})
        query_path  = data['query_path']
        #query_path = Host.get_real_query(data['query_path'])
        #if "" == query_path:
        #    return json.dumps({'code':'false','res':'','desc':'query not exist: %s' % data['query_path']})
        logging.info("create a task")
        taskInfo = Task.create_task(data['target'].strip(),data['qps'],data['source'],query_path,data['query_type'],data['option'].strip())
        dict = {}
        dict.update(taskInfo.__dict__)
        dict['taskid'] = taskInfo.task_id
        self.res['res'] = dict
        return json.dumps(self.res)

    #@checkToken
    def stop_action(self, data):
        logging.info("stop a task")
        taskObj = Task.get_task(data['taskid'])
        taskObj.set_status('stop')
        return json.dumps({'code':'true','res':'','desc':''});

    #@checkToken
    def change_action(self, data):
        logging.info("change task")
        try:
            taskObj = Task.get_task(data['taskid'])
            if taskObj == None:
                self.res['code'] = 1
                return json.dumps(self.res)
            taskObj.set_qps(data['qps'])
            return json.dumps({'code':'true','res':'','desc':''})
        except:
            return sys.exc_info()

    def queryTask_action(self, data):
        logging.info("query task")
        try:
            taskObj = Task.get_task(data['taskid'])
            if taskObj == None:
                return json.dumps({'code':'false','res':'','desc':'taskid not found'})
            return json.dumps({'code':'true','res':taskObj.__dict__,'desc':''})
        except:
            return sys.exc_info()

    def queryTaskAgent_action(self, data):
        logging.info("query task agent")
        try:
            taskObj = Task.get_task(data['taskid'])
            if taskObj == None:
                return json.dumps({'code':'false','res':'','desc':'taskid not found'})
            res = taskObj.get_all_agent()
            hosts = []
            for agent in res:
                hosts.append(agent.__dict__)
            return json.dumps({'code':'true','res':hosts,'desc':''})
        except:
            return sys.exc_info()

class Index:  
    def GET(self, name=None):
        data = web.input()
        title = "no title"
        if data.has_key('title'):
            title = data['title']
        return render.index(name, title)

    def POST(self, name):
        data = web.input()
        return "todo"

if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='logs/press_service.log',
                    filemode='a')
    app = web.application(urls, globals())
    app.run()
