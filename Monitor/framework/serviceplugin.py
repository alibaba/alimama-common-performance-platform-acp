import subprocess
import os
import ConfigParser
import traceback
from lib.util.shellcommand import Shell

def loadOnePluginConfig(pluginDir):
    pluginConfig = {}
    if not os.path.isdir(pluginDir):
        return None
    config = ConfigParser.ConfigParser() 
    try:
        config.read(pluginDir+"/plugin.conf") 
        pluginConfig['name'] = config.get("service","name")
        pluginConfig['language'] = config.get("service","language")
        pluginConfig['file'] = config.get("service","file")
        pluginConfig['remote'] = False
        pluginConfig['dir'] = pluginDir
        return pluginConfig
    except Exception,e:
        print "error, load conf failed!"+traceback.format_exc()
        return None
    
def loadAllPluginsConfig(pluginsDir):
    pluginsConfig = []
    if not os.path.isdir(pluginsDir):
        return None
    dirs = os.listdir(pluginsDir)
    for aDir in dirs:
        if not os.path.isdir(pluginsDir+"/"+aDir):
            continue
        pluginsConfig.append(loadOnePluginConfig(pluginsDir+"/"+aDir))
    return pluginsConfig

class ServicePlugin(object):
    __slots__ = ['__conf','__name','__ip','__port']
    def __init__(self, confDict):
        self.__conf = confDict
        self.__name = confDict['name']
        if confDict['remote']:
            self.__ip = confDict['ip']
            self.__port = confDict['port']
            self.__startCmd = confDict['startCmd']
            cmd = Shell(self.__startCmd)
            cmd.run()
            cmd.print_result()

class ShellPlugin(ServicePlugin):
    def __init__(self,confDict):
        super(ShellPlugin,self).__init__(confDict)
        self.__scriptFile = confDict['file']
        self.__dir = confDict['dir']
 
    def run(self, jsonInput, paramsDict):
        os.environ['JSONINPUT'] = jsonInput
        cmd = Shell("cd "+self.__dir+" && sh "+self.__scriptFile)
        cmd.run()
        return cmd.ret_code,cmd.ret_info,cmd.err_info

class PythonPlugin(ServicePlugin):
    def __init__(self,confDict):
        super(PythonPlugin,self).__init__(confDict)
        self.__scriptFile = confDict['file']
        self.__dir = confDict['dir']
 
    def run(self, jsonInput, paramsDict):
        os.environ['JSONINPUT'] = jsonInput
        cmd = Shell("cd "+self.__dir+" && python "+self.__scriptFile)
        cmd.run()
        return cmd.ret_code,cmd.ret_info,cmd.err_info

class PhpPlugin(ServicePlugin):
    def __init__(self,confDict):
        super(PhpPlugin,self).__init__(confDict)
        self.__scriptFile = confDict['file']
        self.__dir = confDict['dir']
 
    def run(self, jsonInput, paramsDict):
        os.environ['JSONINPUT'] = jsonInput
        cmd = Shell("cd "+self.__dir+" && php "+self.__scriptFile)
        cmd.run()
        return cmd.ret_code,cmd.ret_info,cmd.err_info

class JavaPlugin(ServicePlugin):
    def __init__(self,confDict):
        super(JavaPlugin,self).__init__(confDict)
        self.__scriptFile = confDict['file']
        self.__dir = confDict['dir']
 
    def run(self, jsonInput, paramsDict):
        os.environ['JSONINPUT'] = jsonInput
        cmd = Shell("cd "+self.__dir+" && java "+self.__scriptFile)
        cmd.run()
        return cmd.ret_code,cmd.ret_info,cmd.err_info
         

class ServiceFactory(object):
    def __init__(self, confDict):
        pass

    def __new__(cls, confDict):
        if confDict['language'] == "shell":
            obj = object.__new__(ShellPlugin, confDict)
            obj.__init__(confDict)
            return obj
        if confDict['language'] == "python":
            obj = object.__new__(PythonPlugin, confDict)
            obj.__init__(confDict)
            return obj
        if confDict['language'] == "php":
            obj = object.__new__(PhpPlugin, confDict)
            obj.__init__(confDict)
            return obj
        if confDict['language'] == "java":
            obj = object.__new__(JavaPlugin, confDict)
            obj.__init__(confDict)
            return obj
            
if __name__=="__main__":
    print loadOnePlugin("../plugins/phpsample/");
    print loadAllPlugins("../plugins");
