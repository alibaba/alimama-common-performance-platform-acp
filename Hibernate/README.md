一.简介
===
* 1.Hibernate模块是acp数据持久化模块,acp使用python 实现数据持久化,通过http接口的形式对外提供服务.

二.编译及依赖:
===
* 1.依赖:python > 2.7.6
* 2.安装sqlalchemy:  https://github.com/sqlalchemy/sqlalchemy 放到python lib目录下面
* 3.安装到tools/python2.7.6/下,或者更改env_init.sh bin路径到指定路径

三.启动:
===
* 1.cd Hibernate  && sudo start_service.sh
* 2.停止: sudo sh stop_service.sh 
* 3.启动12345 端口服务,
* 4.start_service.sh 里面的 env_init.sh配置了python bin环境和lib环境,用户可自定义指定自己的环境
* 5.ps -ef|grep py|grep 12345

* 6. curl '127.0.0.1:12345'  查看服务是否正常运行

四:功能介绍:
* 1.用户自定义插件,通过简单配置,即可url路径名映射到用户具体的的目录,执行业务逻辑.
* 2.支持多种语言,如 python,php,shell等.

五.FAQ
===
*** 1.如何查看log? /tmp/webservice1.log log会打印到这里,可通过修改start_service.sh配置
*** 2.具体的业务逻辑都在plugin里面实现,通过 curl '127.0.0.1:12345/xxx?param1=111' 格式访问
*** 3.mysql表设计:  model/MYSQL_TABLE
