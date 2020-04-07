一: 简介
===
### 提供基于zookeeper实现的大规模分布式调度服务,可同时调度上万个agent,资源分配粒度达到内核级别,如一个机器上可以启动多个agent,一个agent可以分为多个资源,如96核机器可分配96个资源粒度,同时提供了运维页面,一键式部署脚本/命令.

二:依赖
===
### 1:jdk > 1.6
### 2:安装zookeeper:https://github.com/apache/zookeeper  默认安装到 /opt/install/zookeeper-3.4.5 目录

三、如何在本地搭建zk服务？
===

### 1. 进入zk目录，执行sudo bash ./zk_init.sh，完成zk部署工作,如有zk部署经验可跳过此步骤
### 2. 执行sudo bash ./start.sh，启动zk服务进程
### 3. 执行sudo bash ./stop.sh，停止zk服务进程

四、如何在本地搭建zk web页面，便于调试
===
### 1.获取zk web代码:https://github.com/killme2008/node-zk-browser
### 2. 进入zk_web目录，执行sudo bash ./start.sh，启动zk web进程
### 3. 在浏览器输入[ip:3000]（如本开发机ip为127.0.0.1，在浏览器输入127.0.0.1:3000），即可看到zk的web页面
### 4. 执行sudo bash ./stop.sh，停止zk web进程

五、部署&运维
===
### 1. 发压系统域名: ***
### 2. Debug页面: ***
### 3. ZK地址: ***
### 4. ZK Web页面: ***
### 5. 起停命令
* web interface: cd scripts/ && sudo  bash ./webservice_ctrl.sh [start|stop]; 
* schedule cd scripts/ && sudo  ../python2.7.6/bin/python schedule_ctrl.py [start|stop]   (python 路径可自己指定)
*  发压机器增减 新增机器: cd scripts/ && ../python2.7.6/bin/python resource_add.py 1.1.1.1,2.2.2.2,3.3.3.3, 然后在新机器上部署agent代码和服务
* 下线机器: cd scripts/ && ../python2.7.6/bin/python resource_delete.py 1.1.1.1,2.2.2.2,3.3.3.3
8. 停止所有发压任务(慎用): cd scripts/ && ../python2.7.6/bin/python all_task_stop.py
9. 注意点:  如果发压工具打开文件数较多，需要调整open files大小(建议调整到165535)
