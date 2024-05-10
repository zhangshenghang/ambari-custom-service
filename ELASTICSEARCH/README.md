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

### Python Request模块安装
创建脚本 `install_requests.sh`
```shell
#!/bin/bash

# 检查 pip 是否已经安装
if ! command -v pip &> /dev/null
then
    echo "pip 未能找到，正在安装 pip..."
    # CentOS 7 使用以下命令安装 pip
    sudo yum install -y epel-release
    sudo yum install -y python-pip
    
    # 如果是 CentOS 8，你可能需要将上述命令中的 yum 替换为 dnf
    # sudo dnf install -y epel-release
    # sudo dnf install -y python3-pip    
    echo "pip 安装完成。"
fi

# 使用 pip 安装 requests 库
echo "正在安装 requests 库..."
pip install --trusted-host pypi.tuna.tsinghua.edu.cn requests==2.23.0

echo "requests 库安装完成。"
```
赋予权限
```shell
chmod +x install_requests.sh
```
运行安装
```shell
./install_requests.sh
```

---

工具 elastic_metrics_jar_name.jar 项目为：`ambari-elastic-metrics`