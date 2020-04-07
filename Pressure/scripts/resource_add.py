#coding=utf-8
import sys
import os
path = os.path.split(os.path.realpath(__file__))[0]
sys.path.append(path+"/../src")
from host.host import *

ip_list = sys.argv[1]
for ip in ip_list.split(","):
    Host.add_host(ip)
