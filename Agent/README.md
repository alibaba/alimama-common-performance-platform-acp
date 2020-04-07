一:简介
===
* 大规模分布式调度的执行器agent,在acp中主要负责获取压测任务,启动真正的压测进程,同时支持自定义任务,拉取数据等功能,此外,agent会向zookeeper主动汇报当前agent状态,如当前机器上资源数,任务心跳,任务管理等.

二:依赖
===
* 1. python >= 2.7.6
* 2. 安装kazoo到自己的python 目录,https://github.com/python-zk/kazoo
* 3. hadoop >= 2.2,0 ,并安装到指定目录,如/home/admin/hadoop/bin/hadoop (如有数据持久化需要)

三:部署
===
* cd Agent/agent && sudo ../python2.7.6/bin/python ./agent_ctrl.py start (python替换为自己的路径)
* ps -ef|grep agent_ctrl 查看进程是否存在

四:FAQ
===
* 1. agent log打印在log/run.log中.
* 2.Agent/agent/agent.conf中对压测协议和拉去数据进行配置
