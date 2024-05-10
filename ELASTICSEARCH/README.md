## AMBARI - ELASTICSEARCH

ambari 的 elasticsearch 自定义服务集成，自动化安装部署脚本

### 调试开发
#### 本地：整个安装包同步到服务器安装目录
```shell
cd /Users/mac/PycharmProjects/ELASTICSEARCH && tar -czvf ELASTICSEARCH.tar.gz ../ELASTICSEARCH && scp  ELASTICSEARCH.tar.gz root@192.168.235.128:/var/lib/ambari-server/resources/stacks/HDP/3.1/services/ &&  rm ELASTICSEARCH.tar.gz 
```

#### 服务器：解压删除无用文件
```shell
cd /var/lib/ambari-server/resources/stacks/HDP/3.1/services/ && rm -rf ELASTICSEARCH && tar -zxvf ELASTICSEARCH.tar.gz && rm -rf ELASTICSEARCH/venv ELASTICSEARCH/.git ELASTICSEARCH/.idea/ ELASTICSEARCH/.gitignore ELASTICSEARCH/README.md && rm -f ELASTICSEARCH.tar.gz && ambari-server restart
```

---

工具 elastic_metrics_jar_name.jar 项目为：`ambari-elastic-metrics`