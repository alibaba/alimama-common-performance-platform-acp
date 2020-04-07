#coding:utf-8
import sys
import time
import traceback
import threading
import traceback
import signal

#######################################
# Class Monitor
class Monitor:
    '''
    Monitor类, 独立线程, 绑定多个Rule实例

    rules:  Rule实例的列表
    '''
    
    def __init__(self,name,rules,interval=5):
        self.name = name
        self.interval = interval

        # ensure rules is a tuple or list
        if not (type(rules) in (tuple, list)):
            rules = tuple([rules]) 
        self.rules = rules
        self.isRunning = False

    def run(self):
        self.isRunning = True
        signal.signal(signal.SIGTERM, self.term_signal_handler)
        while self.isRunning:
            for rule in self.rules:
                runner = self.getRunnerForRule(rule)
                runner.run()

                # sleep 
                time.sleep(self.interval)

    def term_signal_handler(self, signum, frame):
        print "%s stopped."%(self.name)
        self.isRunning = False

    # 实例化一个Runner包装Rule实例
    def getRunnerForRule(self, rule):
        return self._createRunner(rule, self.onRuleEnded)

    # 实例化一个Runner包装Action实例
    def getRunnerForAction(self, rule, action):
        return self._createRunner(action, self.onActionEnded)

    # Action执行结束后的Callback
    def onActionEnded(self,runner):
        pass

    # Rule执行结束后的Callback
    def onRuleEnded(self, runner):
        rule = runner.runable

        # succes
        if runner.result.isSuccess():
            if rule.success:
                for action_object in rule.success:
                    action_runner = self.getRunnerForAction(rule, action_object)
                    action_runner.run(rule,runner)
        # failure
        else:
            if rule.failure:
                for action_object in rule.failure:
                    action_runner = self.getRunnerForAction(rule, action_object)
                    action_runner.run(rule,runner)

    def _createRunner(self, runable, callback):
        runable_id = str(runable)
        runner = Runner.Create(runable,id=runable_id)
        runner.onRunEnded(callback)
        return runner

#######################################
# Class Runner
class Runner:
    '''
    Wrapper for Rules and Actions

    Rule或Action通过包装在Runner实例中来单独开启线程执行
    '''
    
    @classmethod
    def Create(cls, runable, id=None):
        runner = Runner(runable, id)
        return runner

    def __init__(self,runable,id=None):
        self._onRunEnded = None
        self.runable     = runable
        self.result      = None
        self.id          = id
        self._thread     = threading.Thread(target=self._run)
        self._thread.setDaemon(True)

    def onRunEnded(self, callback):
        self._onRunEnded = callback
        return self

    def run(self, *args):
        self.args = args
        self._thread.start()
        return self

    def _run(self):
        try:
            self.result = self.runable.run(*self.args)
            if self._onRunEnded:
                self._onRunEnded(self)
        except Exception,e:
            traceback.print_exc()

#######################################
# Class Result
class Result:
    '''
    描述一次监控结果（success 或failure)

    注：此为基类，实际使用具体实现类Success和Failure

    message:    保存传递描述信息
    info:       字典形式保存传递更复杂的数据信息 
    '''
    def __init__(self, message=None, info=None):
        self.message = message
        self.info = info

    def getMessage(self):
        return self.message

    def isSuccess(self):
        pass

    def isFailure(self):
        pass


class Success(Result):
    
    def __init__ (self, message=None):
        Result.__init__(self,message)

    def isSuccess(self):
        return True

    def isFailure(self):
        return False

class Failure(Result):
    
    def __init__ (self, message=None):
        Result.__init__(self,message)

    def isSuccess(self):
        return False

    def isFailure(self):
        return True

