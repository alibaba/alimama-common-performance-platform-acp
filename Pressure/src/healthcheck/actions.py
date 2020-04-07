#coding:utf-8
import sys
import os
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from monitor import *
from task.agent import Agent
from common.util import *
from res_manager.res_manager import ResManager
import time
from kazoo.client import KazooClient

##############################
# global config
SMTP_SERVER = '...'
SMTP_PORT = 465
SMTP_USERNAME = 'qa@alibaba-inc.com'
SMTP_PASSWORD = '123456'
SMTP_ORIGIN = 'ACP压测平台<acp@alibaba-inc.com>'

ZK_HOST_ROOT_PATH = "/acp/host/list"
ZK_HOST_LOCK_PATH = "/acp/host/lock"

class AbstractAction:
    '''
    Action抽象类

    当一次检查出现success或failure是要采取的Action(会开启独立线程执行)

    注：此为抽象类，实际使用时要写具体实现类并将实际Action逻辑写在run()里面
    '''
    def run(self, *args):
        pass

class Log(AbstractAction):
    '''
    执行记log操作，可以选择输出到console和/或写进log文件

    path:       log文件的路径，为None则不写log文件
    stdout:     是否输出到console
    overwrite:  当写log文件是用overwirte模式还是append模式 
    '''

    def __init__(self, path=None, stdout=True, overwrite=False):
        self.path       = path
        self.stdout     = stdout
        self.overwrite  = overwrite

    def successMessage(self, msg):
        return "success message: %s"%(msg)

    def failureMessage(self,msg):
        return "failure message: %s"%(msg)

    def run(self, *args):
        runner = None
        for arg in args:
            if isinstance(arg,Runner):
                runner = arg
                break

        result = runner.result
        if result.isFailure():
            msg = self.failureMessage(result.getMessage()) + "\n"
        else:
            msg = self.successMessage(result.getMessage()) + "\n"

        self.log(msg)

    def log(self,msg):
        if self.stdout:
            sys.stdout.write(msg)
        if self.path:
            f = open(self.path, (self.overwrite and 'w') or 'a')
            f.write(msg)
            f.flush()
            f.close()
        return True

class Email(AbstractAction):
    '''
    执行发email操作

    recipient:      收件人(列表形式)
    subject:        邮件主题 
    min_interval:   两次email发送动作间最小时间间隔(发送频率抑制,单位为秒)
    '''
    
    def __init__(self, recipient, subject, min_interval=300):

        # ensure recipient is a tuple or list 
        if not (type(recipient) in (tuple,list)):
            recipient = tuple([recipient])

        self.recipient      = recipient
        self.subject        = subject
        self.min_interval  = min_interval
        self.last_trigger   = 0

    def run(self, runner, *args):
        runner = None
        for arg in args:
            if isinstance(arg,Runner):
                runner = arg
                break

        result = runner.result
        message = result.getMessage()

        # 发送频率抑制
        now = time.time()
        if (now - self.last_trigger) > self.min_interval:
            self.send(message)
            self.last_trigger = now
        else:
            print "Action \"%s\" is blocked because of min_interval control(now=%d, last_trigger=%d)"%(str(self),now,self.last_trigger)

    def send(self,message):
        try:
            server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
            server.login(SMTP_USERNAME,SMTP_PASSWORD)
            msg = MIMEText(message,'plain','utf-8')
            subject = "%s - %s"%(self.subject,self.getTimeStr())
            msg["Subject"] = Header(subject,"utf-8")

            server.sendmail(SMTP_ORIGIN, self.recipient, msg.as_string())
            print "send email to %s...done"%(self.recipient)
        finally:
            server.quit()

    def getTimeStr(self):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

class MarkACPErrorHosts(AbstractAction):
    def __init__(self,zkAddr):
        self.zk_client = KazooClient(zkAddr)
        self.zk_client.start()

    def run(self, *args):
        runner = None
        for arg in args:
            if isinstance(arg,Runner):
                runner = arg
                break

        result = runner.result

        # 取得error host
        error_hosts = result.info.get("error_hosts")
        if error_hosts:
            for hostIp in error_hosts:
                status_path = os.path.join(ZK_HOST_ROOT_PATH,hostIp,"status")
                self.zk_client.set(status_path,"error")

class ProcessACPDeadAgents(AbstractAction):
    def __init__(self):
        self.resMgr = ResManager()

    def run(self, *args):
        runner = None
        for arg in args:
            if isinstance(arg,Runner):
                runner = arg
                break

        result = runner.result

        # 取得dead agent
        dead_agents = result.info.get("dead_agents")
        if dead_agents:
            for agentObj in dead_agents:
                if not agentObj.heartbeat():
                    logging.error("Agent \"%s\" is dead, release it!!"%(agentObj.__dict__))
                    self.resMgr.release_agent(agentObj)

