#coding=utf-8
import sys
import time
from kazoo.client import KazooClient
sys.path.append("..")
from task.task import *

print Task.delete_task("t1498135392228")
