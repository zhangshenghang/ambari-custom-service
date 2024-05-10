# 便捷命令

## HUGEGRAPH

### 本地源码上传到Ambari Server服务器
```shell
cd /Users/mac/PycharmProjects/ambari-custom-service/HUGEGRAPH && tar -czvf HUGEGRAPH.tar.gz ../HUGEGRAPH && scp  HUGEGRAPH.tar.gz root@172.16.25.213:/var/lib/ambari-server/resources/stacks/HDP/3.1/services/ &&  rm HUGEGRAPH.tar.gz
```

### Ambari Server服务器更新服务

```shell

cd /var/lib/ambari-server/resources/stacks/HDP/3.1/services/ && rm -rf HUGEGRAPH && tar -zxvf HUGEGRAPH.tar.gz && rm -rf HUGEGRAPH/._.DS_Store HUGEGRAPH/.DS_Store HUGEGRAPH/venv HUGEGRAPH/.git HUGEGRAPH/.idea/ HUGEGRAPH/.gitignore HUGEGRAPH/README.md && rm -f HUGEGRAPH.tar.gz && ambari-server restart 

```

### 只更新script脚本

```shell

scp package/scripts/* root@172.16.25.213:/var/lib/ambari-agent/cache/stacks/HDP/3.1/services/HUGEGRAPH/package/scripts/

```

## ELASTICSEARCH

### 本地源码上传到Ambari Server服务器
```shell
cd /Users/mac/PycharmProjects/ambari-custom-service/ELASTICSEARCH && tar -czvf ELASTICSEARCH.tar.gz ../ELASTICSEARCH && scp  ELASTICSEARCH.tar.gz root@172.16.25.213:/var/lib/ambari-server/resources/stacks/HDP/3.1/services/ &&  rm ELASTICSEARCH.tar.gz
```

### Ambari Server服务器更新服务

```shell

cd /var/lib/ambari-server/resources/stacks/HDP/3.1/services/ && rm -rf ELASTICSEARCH && tar -zxvf ELASTICSEARCH.tar.gz && rm -rf ELASTICSEARCH/._.DS_Store ELASTICSEARCH/.DS_Store ELASTICSEARCH/venv ELASTICSEARCH/.git ELASTICSEARCH/.idea/ ELASTICSEARCH/.gitignore ELASTICSEARCH/README.md && rm -f ELASTICSEARCH.tar.gz && ambari-server restart 

```

### 只更新script脚本

```shell

scp package/scripts/* root@172.16.25.213:/var/lib/ambari-agent/cache/stacks/HDP/3.1/services/ELASTICSEARCH/package/scripts/

```