概述
===
alimama-common-performance platform(简称acp)是基于zookeeper的大规模分布式的性能测试平台,服务于妈妈各个业务线性能测试,acp 1.0开源版本已经发布,主要特性如下:
------
* python实现,基于zookeeper的分布式智能调度服务/通用任务执行agent/http接口,可同时调度万级别agent执行任务,任务分配粒度细化到协议/压测数据类型级别,同时提供运维页面/部署脚本.
* python, based on zookeeper's distributed intelligent scheduling service / common task execution agent / http interface, can schedule ten thousand levels of agent execution tasks at the same time, the task distribution granularity is refined to the level of protocol / test-data type, and provides operation and maintenance page / Deployment script
* c++版本的http高性能测试工具及sdk,将发压线程抽象成链式管理,同时提供指标实时统计,压测报告产出,控制qps,批量读取query,支持同步等压测模式.
* C++  http high-performance testing tool and SDK, abstracts the pressure-generating threads into a chain management, while providing real-time statistics of indicators, perf report, qps controller, batch query reader, and support for pressure test modes such as synchronization.
* python实现数据持久化方案,支持mysql增删改查,负责压测任务及监控数据持久化.
* python,Data persistence solution, supports mysql curl , this module is responsible for pressure testing tasks and monitoring data persistence

* 基于python的通用http服务,可实现用户自定义增加plugin,自定义执行任务.
* python based common http Protocol service,support user-defined plugins and customize execution tasks

* 一站式web平台,触发任务,查看指标,停止任务,任务列表.

### 1.部署分布式调度服务和接口服务
[使用文档](https://github.com/alibaba/alimama-common-performance-platform-acp/tree/master/Pressure)  
### 1. zookeeper's distributed scheduling service deploy
[Documentation](https://github.com/alibaba/alimama-common-performance-platform-acp/tree/master/Pressure)  


### 2.部署分布式agent及运维页面.
[使用文档](https://github.com/alibaba/alimama-common-performance-platform-acp/tree/master/Agent)  

### 3.c++高性能压测工具的依赖及编译
[使用文档](https://github.com/alibaba/alimama-common-performance-platform-acp/tree/master/HttpBench)  

### 4.数据持久化层和监控层部署
[使用文档](https://github.com/alibaba/alimama-common-performance-platform-acp/tree/master/Monitor)  

### 5.web部署
[使用文档](https://github.com/alibaba/alimama-common-performance-platform-acp/tree/master/Web)  


后续开源计划
===
* acp除了提供了基础的性能测试组件外，还在智能化应用在性能测试领域做了很多探索,如acp架构图所示,acp做到了基于模型/算法的无人值守性能测试,引领业界方向,结合整体架构图后续开源计划如下:
* 1:开源无人值守的模型训练流.
* 2:开源无人值守的实时压测流.
* 3:开源亿万级别数据的数据构造系统.
* 4:开源基于算法/模型的智能数据抽取方案.
* 5:开源后端通用指收集系统.

联系我们
===
* 欢迎通过邮件组 acp-opensource@list.alibaba-inc.com和github issue联系和反馈.


FAQ
===
![](http://gitlab.alibaba-inc.com/engine-test-platform/acp-ops/tree/master/arch.png)  



License
===
* acp使用Apache-2.0许可证

致谢
===
acp由阿里妈妈事业部-技术质量-工具平台团队荣誉出品,感谢阿里妈妈测试团队,pe团队,主搜团队的帮助.

