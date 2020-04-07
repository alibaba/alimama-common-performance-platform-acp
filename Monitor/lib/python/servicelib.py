import os
import sys
import json
import urllib2

def getValue(keyname):
    jsonStr = os.environ['JSONINPUT']
    decodeJson = json.loads(jsonStr)  
    if decodeJson.has_key(keyname):
        return decodeJson[keyname]
    return ""

def getJsonInput():
    return os.environ['JSONINPUT']

def getDictInput():
    jsonStr = os.environ['JSONINPUT']
    return json.loads(jsonStr)

def callService(hosts, plugin, params):
    httpCmd = "http://127.0.0.1:9090/"+plugin+"?"+params+"&hosts="+hosts
    try:
        page=urllib2.urlopen(httpCmd)
        line = page.read()
        page.close()
        return line
    except Exception,ex:
        return str(ex)

def getServiceValue(host, key, serviceRes):
    decodeJson = json.loads(serviceRes)
    try:
        return decodeJson[host][key]
    except Exception,ex:
        return ""
    

def checkAuthority(users, groups):
    user = os.environ['USERINPUT']
    group = os.environ['USERGROUP']
    if users != "":
        usersArr = users.split(",")
        if user!="" and user in usersArr:
            return True
        print '{"status":"failed", "msg":"user auth failed"}'
        sys.exit(10)

    if groups=="":
       return True 
    
    groupArr = group.split(",")
    groupsArr = groups.split(",")
    for agroup in groupArr:
        if agroup in groupsArr:
            return True
    print '{"status":"failed", "msg":"user auth failed"}'
    sys.exit(10)
