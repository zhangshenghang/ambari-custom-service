#!/bin/bash
# 目前该脚本暂未用到
cat /etc/group | grep ^$1: >> /dev/null 2>&1
if [ $? -ne 0 ];then
	# group 不含 elasticsearch
	id $1 >> /dev/null 2>&1;[ $? -ne 0 ] && adduser $1 || echo "user: $1 existed"
else
	# group 含有 elasticsearch
	id $1 >> /dev/null 2>&1;[ $? -ne 0 ] && adduser $1 -g $1 || echo "user:$1 existed"
fi
chown -R $1:$1 /home/$1

