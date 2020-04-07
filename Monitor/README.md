一.简介
===
* 1.Monitor模块是监控收集模块,acp使用python 实现监控收集,通过http接口的形式对外提供服务.

二.编译及依赖:
===
* 1.依赖:python > 2.7.6

三.启动:
===
* 1.cd Monitor  && sudo start_service.sh
* 2.停止: sudo sh stop_service.sh 
* 3.启动12346 端口服务,
* 4.start_service.sh 里面的 env_init.sh配置了python bin环境和lib环境,用户可自定义指定自己的环境
* 5.ps -ef|grep py|grep 12346

* 6. curl '127.0.0.1:12346'  查看服务是否正常运行

四.FAQ
===
* 1.如何查看log? /tmp/webservice1.log log会打印到这里,可通过修改start_service.sh配置
* 2.具体的业务逻辑都在plugin里面实现,通过 curl '127.0.0.1:12346/xxx?param1=111' 格式访问
