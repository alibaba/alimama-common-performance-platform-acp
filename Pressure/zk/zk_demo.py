from kazoo.client import KazooClient
import sys
import getopt
import json
import six
import time
import urllib2

def usage():
    print "add machine into machine pool:"
    print "\tpress_res_mgr.py -a [ip1:resourceCount1,ip2:resourceCount2,...]"
    print "delete machine from machine pool:"
    print "\tpress_res_mgr.py -d [ip1,ip2]"
    print "allocate press agent resource from machine pool:"
    print "\tpress_res_mgr.py -n pressjobid:resourceCount"
    print "release press agent resource into machine pool:"
    print "\tpress_res_mgr.py -r pressjobid"
    print "help info:"
    print "\tpress_res_mgr.py -h"

zkAddress = "127.0.0.1:2181"
zk = KazooClient(hosts=zkAddress)
zk.start()
hostPath = "/press_res/hosts"
jobPath = "/press_res/jobs"
lockPath = "/press_res/lock"
createAgentUrl = "/press_agent?token=aaa123456&cmd=create&jobId="
deleteAgentUrl = "/press_agent?token=aaa123456&cmd=delete&jobId="

def addHost(hostList):
    ret = 0
    retDict = {}
    retDict['errorInfo'] = ""
    if not zk.exists(hostPath):
        zk.create(hostPath,makepath=True)
    if not zk.exists(jobPath):
        zk.create(jobPath,makepath=True)
    for host in hostList:
        ip,resCount = host.split(":")
        if(zk.exists(hostPath+"/"+ip)):
            ret += 1
            retDict['errorInfo'] += ip+" is in pool already;"
        else:
           zk.create(hostPath+"/"+ip,resCount) 
    print json.dumps(retDict)
    return ret

def delHost(hostList):
    ret = 0
    retDict = {}
    retDict['errorInfo'] = ""
    for ip in hostList:
        if(zk.exists(hostPath+"/"+ip)):
            zk.delete(hostPath+"/"+ip)
        else:
            retDict['errorInfo'] += ip+" is not in pool;"
            ret += 1
    print json.dumps(retDict)
    return ret

def allocateRes(jobIdRes):
    ret = 0
    retDict = {}
    retDict['errorInfo'] = ""
    resources = {} 
    jobId,jobResCount = jobIdRes.split(":")
    zk.create(lockPath, ephemeral=True)
    if zk.exists(jobPath+"/"+jobId):
        retDict['errorInfo'] = "job:%s exists, can not allocate resource again!"%jobId
        ret = 1
        print retDict
        zk.delete(lockPath)
        return ret
    jobResCount = int(jobResCount)
    resourceNodes = zk.get_children(hostPath)
    totalResCount = 0
    #allcate machine list for this job
    allocateIpList = []
    for ip in resourceNodes:
        resCount = zk.get(hostPath+"/"+ip) 
        resources[ip] = resCount[0]
        totalResCount += int(resCount[0])
    sortDict = sorted(resources.items(), key=lambda d: d[1]) 
    if jobResCount>totalResCount:
        ret = 1
        retDict['errorInfo'] += "resource count is %d, not sufficient!"%totalResCount 
    else:
        allocateResCount = 0
        resourceStr = ""
        while allocateResCount<jobResCount:
            for res in sortDict:
                # minus a resource
                ip = res[0]
                count = int(res[1])
                if count==0:
                    continue
                count = count - 1
                zk.set(hostPath+"/"+res[0], str(count))
                allocateIpList.append(ip)
                # add to task
                allocateResCount += 1
                if allocateResCount == jobResCount:
                    resourceStr += ip
                    break
                resourceStr += ip + ","
        #print jobPath+"/"+jobId, six.binary_type(resourceStr)
        zk.create(jobPath+"/"+jobId, six.binary_type(resourceStr))
    zk.delete(lockPath)
    # start press agent for these machines
    for ip in allocateIpList:
        url = "http://"+ip+":9090"+createAgentUrl+jobId
        try:
            result = urllib2.urlopen(url).read()
        except:
            retDict['errorInfo'] += "agent:%s start failed! Allocate resource failed!"%(ip)
            ret += 1
            releaseRes(jobId)
        
    print json.dumps(retDict)
    return ret

def releaseRes(jobId):
    ret = 0
    retDict = {}
    retDict['errorInfo'] = ""
    zk.create(lockPath, ephemeral=True)
    if not zk.exists(jobPath+"/"+jobId):
        retDict['errorInfo'] = "job:%s not exists!"%jobId
        ret = 1
        zk.delete(lockPath)
        return ret
    #print jobPath+"/"+jobId
    resources = zk.get(jobPath+"/"+jobId)
    #print resources
    ipList = resources[0].split(",")
    for ip in ipList:
        url = "http://"+ip+":9090"+deleteAgentUrl+jobId
        try:
            result = urllib2.urlopen(url).read()
            #print hostPath+"/"+ip
        except:
            retDict['errorInfo'] += "agent:%s release failed!"%(ip) 
            ret+=1
        count = zk.get(hostPath+"/"+ip)
        #print count
        count = int(count[0])
        count += 1
        zk.set(hostPath+"/"+ip, str(count))
    zk.delete(jobPath+"/"+jobId, recursive=True)
    zk.delete(lockPath)
    print retDict
    return ret

def readHost(jobId):
    ret = 0
    retDict = {}
    retDict['errorInfo'] = ""
    if not zk.exists(jobPath+"/"+jobId):
        retDict['errorInfo'] = "job:%s not exists!"%jobId
        ret = 1
        return ret
    resources = zk.get(jobPath+"/"+jobId)
    ipList = resources[0].split(",")
    print len(ipList)
    return ret

if __name__ == '__main__':
    opts, args = getopt.getopt(sys.argv[1:], "ha:d:n:r:x:")
    for op, value in opts:
        if op == "-x":
            # add machine into machines pool
            lineid = value
            ret = readHost(lineid)
            zk.stop()
            sys.exit(ret)
        if op == "-a":
            # add machine into machines pool
            hostList = value.split(",")
            ret = addHost(hostList)
            zk.stop()
            sys.exit(ret)
        elif op == "-d":
            # delete machine from machines pool
            hostList = value.split(",")
            ret=delHost(hostList)
            zk.stop()
            sys.exit(ret)
        elif op == "-n":
            jobIdRes = value
            ret = allocateRes(jobIdRes)
            zk.stop()
            sys.exit(ret)
        elif op == "-r":
            jobId = value
            print jobId
            ret = releaseRes(jobId)
            zk.stop()
            sys.exit(ret)
        elif op == "-h":
            usage()
            zk.stop()
            sys.exit(0)
        else:
            usage()
            zk.stop()
            sys.exit(1)
 
