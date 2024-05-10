# Ambari 2.7.5 版本自定义服务开发

## 安装
服务安装有两种方法：
 - 1. Ambari已经安装其他服务
   - 这种方法无法重新安装我们编译好的包，直接将自定义服务代码上传到服务器指定目录
 - 2. Ambari尚未安装
   - 直接安装编译好的安装包

### Ambari已经安装其他服务
这里使用ElasticSearch举例
1. 将我们需要用到服务上传到目录
```shell
/var/lib/ambari-server/resources/stacks/HDP/3.1/services
```


## 安装包位置
所有自定义服务安装依赖包统一放在:`ambari-extend/centos7`目录下，即`/var/www/html/ambari-extend/centos7`
|服务|安装包位置|
|---|---|
|ELASTICSEARCH|/var/www/html/ambari-extend/centos7/es/|
|DORIS|/var/www/html/ambari-extend/centos7/doris/|
|HUGEGRAPH|/var/www/html/ambari-extend/centos7/hugegraph/|
|CLICKHOUSE|/var/www/html/ambari-extend/centos7/clickhouse/|
