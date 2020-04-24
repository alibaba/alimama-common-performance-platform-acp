
## 目录结构
解压后生成以下两个子目录

* acp-test-service,为空白module;，
* acp-test-start，包含web配置和示例代码，web配置和vm模板在src/main/webapp目录中。日志配置文件为src/main/webapp/WEB-INF下的logback.xml。

## 使用方式
在根目录下执行

```sh
mvn package
```

在acp-test-start的target目录下生成war。将war重命名acp.war并部署到tomcat 下deploy目录即可。

