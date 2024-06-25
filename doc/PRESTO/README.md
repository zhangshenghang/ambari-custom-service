# 开发联调
## 本地源码上传到Ambari Server服务器

执行机器：本机

```shell
cd /Users/mac/PycharmProjects/ambari-custom-service/PRESTO && tar -czvf PRESTO.tar.gz ../PRESTO && scp  PRESTO.tar.gz root@172.16.25.213:/var/lib/ambari-server/resources/stacks/HDP/3.1/services/ &&  rm PRESTO.tar.gz
```

## Ambari Server服务器更新服务

执行机器：Ambari Server

```shell

cd /var/lib/ambari-server/resources/stacks/HDP/3.1/services/ && rm -rf PRESTO && tar -zxvf PRESTO.tar.gz && rm -rf PRESTO/._.DS_Store PRESTO/.DS_Store PRESTO/venv PRESTO/.git PRESTO/.idea/ PRESTO/.gitignore PRESTO/README.md && rm -f PRESTO.tar.gz && ambari-server restart 

```

## 只更新script脚本

执行机器：本机

```shell

cd /Users/mac/PycharmProjects/ambari-custom-service/PRESTO && scp package/scripts/* root@172.16.25.213:/var/lib/ambari-agent/cache/stacks/HDP/3.1/services/PRESTO/package/scripts/

```

## 服务安装的目录

机器：服务器
```shell
cd /usr/hdp/3.1.5.0-152/presto/
```