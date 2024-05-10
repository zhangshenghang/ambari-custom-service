#!/bin/sh

# 设置 doris 用户配置
function change_etc_security_conf()
{
    if [ `grep -c "doris" /etc/security/limits.conf` -ne '0' ]; then
        echo "doris has been defined!"
    else
        echo "doris soft nofile 65535" >> /etc/security/limits.conf
        echo "doris hard nofile 65537" >> /etc/security/limits.conf
        echo "doris soft nproc 4096" >> /etc/security/limits.conf
        echo "doris hard nproc 4096" >> /etc/security/limits.conf
        echo "doris soft memlock unlimited" >> /etc/security/limits.conf
        echo "doris hard memlock unlimited" >> /etc/security/limits.conf
        echo "/etc/security/limits.conf 's doris is defined successfully!"
    fi
}

# 关闭交换分区
function change_swap_conf()
{
  swapoff -a
  sed -ri 's/.*swap.*/#&/' /etc/fstab
}

#
# main start
#
change_etc_security_conf
change_swap_conf
