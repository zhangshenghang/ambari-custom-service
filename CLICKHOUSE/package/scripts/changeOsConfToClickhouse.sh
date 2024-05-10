#!/bin/sh

function change_etc_security_conf()
{
    if [ `grep -c "clickhouse" /etc/security/limits.conf` -ne '0' ]; then
        echo "clickhouse has been defined!"
    else
        echo "clickhouse soft nofile 65536" >> /etc/security/limits.conf
        echo "clickhouse hard nofile 65536" >> /etc/security/limits.conf
        echo "clickhouse soft nproc 131072" >> /etc/security/limits.conf
        echo "clickhouse hard nproc 131072" >> /etc/security/limits.conf
        echo "/etc/security/limits.conf 's clickhouse is defined successfully!"
    fi


    if [ `grep -c "clickhouse" /etc/security/limits.d/20-nproc.conf` -ne '0' ]; then
        echo "clickhouse has been defined!"
    else
        echo "clickhouse soft nofile 65536" >> /etc/security/limits.conf
        echo "clickhouse hard nofile 65536" >> /etc/security/limits.conf
        echo "clickhouse soft nproc 131072" >> /etc/security/limits.conf
        echo "clickhouse hard nproc 131072" >> /etc/security/limits.conf
        echo "/etc/security/limits.d/20-nproc.conf 's clickhouse is defined successfully!"
    fi
}



function close_selinux()
{
  sudo  sed  -i  's/SELINUX=enforcing/SELINUX=permissive/'  /etc/selinux/config  &&  sudo  setenforce  0
}
#
# main start
#
change_etc_security_conf
close_selinux