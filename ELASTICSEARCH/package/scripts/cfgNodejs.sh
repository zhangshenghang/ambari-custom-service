#!/bin/bash
##############################
# @Description: Configure the node.js environment variable, add pm2 tool
# @Author: liuyzh
# @Date: 2018/7/30 18:15
##############################
targetPath="/usr/nodejs"
echo '****************判断/usr/nodejs目录是否存在****************'
pm2 -V
if [ $? -eq 0 ];then
  echo pm2 environment is setted~
else
  echo $targetPath"不存在,新建目录"
  mkdir -p /usr/nodejs
  echo '****************下载nodejs文件****************'
  cd /usr/nodejs
  wget -q $1
  tar zxf node-v10.13.0-linux-x64.tar.gz
  rm -rf node-v10.13.0-linux-x64.tar.gz
  echo '****************配置nodejs环境****************'
  # 配置环境变量
  if [ `grep -c "# set nodejs" /etc/profile` -ne '0' ]; then
    echo "node.js has been defined!"
  else
    echo '# set nodejs' >> /etc/profile
    echo "export NODE_HOME=/usr/nodejs/node-v10.13.0-linux-x64" >> /etc/profile
    echo "export PATH=\$PATH:\$NODE_HOME/bin" >> /etc/profile
    echo '****************使环境变量生效****************'
  fi
  # 延时3秒
  sleep 3s
  # 使环境变量生效
  source /etc/profile
  echo '****************替换/bin/bash****************'
  # 替换/bin/bash
  ln -sf /usr/nodejs/node-v10.13.0-linux-x64/bin/pm2 /usr/bin
  ln -sf /usr/nodejs/node-v10.13.0-linux-x64/bin/node /usr/bin
  ln -sf /usr/nodejs/node-v10.13.0-linux-x64/bin/npm /usr/bin
  echo '****************替换/bin/bash成功****************'
fi




