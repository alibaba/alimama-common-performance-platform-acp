# -*- coding: gbk -*-
# copy from cnblogs
import os
import subprocess
import signal
import pwd
import sys
 
class MockLogger(object):
    '''模拟日志类。方便单元测试。'''
    def __init__(self):
        self.info = self.error = self.critical = self.debug
 
    def debug(self, msg):
        print "LOGGER:"+msg
 
class Shell(object):
    '''完成Shell脚本的包装。
    执行结果存放在Shell.ret_code, Shell.ret_info, Shell.err_info中
    run()为普通调用，会等待shell命令返回。
    run_background()为异步调用，会立刻返回，不等待shell命令完成
    异步调用时，可以使用get_status()查询状态，或使用wait()进入阻塞状态，
    等待shell执行完成。
    异步调用时，使用kill()强行停止脚本后，仍然需要使用wait()等待真正退出。
    TODO 未验证Shell命令含有超大结果输出时的情况。
    '''
    def __init__(self, cmd):
        self.cmd = cmd  # cmd包括命令和参数
        self.ret_code = None
        self.ret_info = None
        self.err_info = None
        #使用时可替换为具体的logger
        self.logger = MockLogger()
         
    def run_background(self):
        '''以非阻塞方式执行shell命令（Popen的默认方式）。
        '''
        self.logger.debug("run %s"%self.cmd)
        # Popen在要执行的命令不存在时会抛出OSError异常，但shell=True后，
        # shell会处理命令不存在的错误，因此没有了OSError异常，故不用处理
        self._process = subprocess.Popen(self.cmd, shell=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE) #非阻塞
         
    def run(self):
        '''以阻塞方式执行shell命令。
        '''
        self.run_background()
        self.wait()
         
    def run_cmd(self, cmd):
        '''直接执行某条命令。方便一个实例重复使用执行多条命令。
        '''
        self.cmd = cmd
        self.run()
 
    def wait(self):
        '''等待shell执行完成。
        '''
        self.logger.debug("waiting %s"%self.cmd)
        self.ret_info, self.err_info = self._process.communicate() #阻塞
        # returncode: A negative value -N indicates that the child was
        # terminated by signal N
        self.ret_code = self._process.returncode
        self.logger.debug("waiting %s done. return code is %d"%(self.cmd,
                            self.ret_code))
 
    def get_status(self):
        '''获取脚本运行状态(RUNNING|FINISHED)
        '''
        retcode = self._process.poll()
        if retcode == None:
            status = "RUNNING"
        else:
            status = "FINISHED"
        self.logger.debug("%s status is %s"%(self.cmd, status))
        return status
 
    # Python2.4的subprocess还没有send_signal,terminate,kill
    # 所以这里要山寨一把，2.7可直接用self._process的kill()
    def send_signal(self, sig):
        self.logger.debug("send signal %s to %s"%(sig, self.cmd))
        os.kill(self._process.pid, sig)
 
    def terminate(self):
        self.send_signal(signal.SIGTERM)
 
    def kill(self):
        self.send_signal(signal.SIGKILL)
     
    def print_result(self):
        print "return code:", self.ret_code
        print "return info:", self.ret_info
        print " error info:", self.err_info
 
class RemoteShell(Shell):
    '''远程执行命令（ssh方式）。
    XXX 含特殊字符的命令可能导致调用失效，如双引号，美元号$
    NOTE 若cmd含有双引号，可使用RemoteShell2
    '''
    def __init__(self, cmd, ip):
        ssh = ("ssh -o PreferredAuthentications=publickey -o "
                "StrictHostKeyChecking=no -o ConnectTimeout=10")
        # 不必检查IP有效性，也不必检查信任关系，有问题shell会报错
        cmd = '%s %s "%s"'%(ssh, ip, cmd)
        Shell.__init__(self, cmd)
         
class RemoteShell2(RemoteShell):
    '''与RemoteShell相同，只是变换了引号。
    '''
    def __init__(self, cmd, ip):
        RemoteShell.__init__(self, cmd, ip)
        self.cmd = "%s %s '%s'"%(ssh, ip, cmd)
 
class SuShell(Shell):
    '''切换用户执行命令（su方式）。
    XXX 只适合使用root切换至其它用户。
        因为其它切换用户后需要输入密码，这样程序会挂住。
    XXX 含特殊字符的命令可能导致调用失效，如双引号，美元号$
    NOTE 若cmd含有双引号，可使用SuShell2
    '''
    def __init__(self, cmd, user):
        if os.getuid() != 0: # 非root用户直接报错
            raise Exception('SuShell must be called by root user!')
        cmd = 'su - %s -c "%s"'%(user, cmd)
        Shell.__init__(self, cmd)
 
class SuShell2(SuShell):
    '''与SuShell相同，只是变换了引号。
    '''
    def __init__(self, cmd, user):
        SuShell.__init__(self, cmd, user)
        self.cmd = "su - %s -c '%s'"%(user, cmd)
 
class SuShellDeprecated(Shell):
    '''切换用户执行命令（setuid方式）。
    执行的函数为run2，而不是run
    XXX 以“不干净”的方式运行：仅切换用户和组，环境变量信息不变。
    XXX 无法获取命令的ret_code, ret_info, err_info
    XXX 只适合使用root切换至其它用户。
    '''
    def __init__(self, cmd, user):
        self.user = user
        Shell.__init__(self, cmd)
 
    def run2(self):
        if os.getuid() != 0: # 非root用户直接报错
            raise Exception('SuShell2 must be called by root user!')
        child_pid = os.fork()
        if child_pid == 0: # 子进程干活
            uid, gid = pwd.getpwnam(self.user)[2:4]
            os.setgid(gid) # 必须先设置组
            os.setuid(uid)
            self.run()
            sys.exit(0) # 子进程退出，防止继续执行其它代码
        else: # 父进程等待子进程退出
            os.waitpid(child_pid, 0)
         
if __name__ == "__main__":
    '''test code'''
    # 1. test normal
    sa = Shell('who')
    sa.run()
    sa.print_result()
     
    # 2. test stderr
    sb = Shell('ls /export/dir_should_not_exists')
    sb.run()
    sb.print_result()
     
    # 3. test background
    sc = Shell('sleep 1')
    sc.run_background()
    print 'hello from parent process'
    print "return code:", sc.ret_code
    print "status:", sc.get_status()
    sc.wait()
    sc.print_result()
     
    # 4. test kill
    import time
    sd = Shell('sleep 2')
    sd.run_background()
    time.sleep(1)
    sd.kill()
    sd.wait() # NOTE, still need to wait
    sd.print_result()
     
    # 5. test multiple command and uncompleted command output
    se = Shell('pwd;sleep 1;pwd;pwd')
    se.run_background()
    time.sleep(1)
    se.kill()
    se.wait() # NOTE, still need to wait
    se.print_result()
     
    # 6. test wrong command
    sf = Shell('aaaaa')
    sf.run()
    sf.print_result()
     
    # 7. test instance reuse to run other command
    sf.cmd = 'echo aaaaa'
    sf.run()
    sf.print_result()
     
    sg = RemoteShell('pwd', '127.0.0.1')
    sg.run()
    sg.print_result()
     
    # unreachable ip
    sg2 = RemoteShell('pwd', '17.0.0.1')
    sg2.run()
    sg2.print_result()
     
    # invalid ip
    sg3 = RemoteShell('pwd', '1711.0.0.1')
    sg3.run()
    sg3.print_result()
     
    # ip without trust relation
    sg3 = RemoteShell('pwd', '10.145.132.247')
    sg3.run()
    sg3.print_result()
     
     
    sh = SuShell('pwd', 'ossuser')
    sh.run()
    sh.print_result()
     
    # wrong user
    si = SuShell('pwd', 'ossuser123')
    si.run()
    si.print_result()
     
    # user need password
    si = SuShell('pwd', 'root')
    si.run()
    si.print_result()
