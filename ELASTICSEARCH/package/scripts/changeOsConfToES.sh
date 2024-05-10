#!/bin/sh
function change_etc_sysctl_conf()
{
    if [ `grep -c "vm.max_map_count" /etc/sysctl.conf` -ne '0' ]; then
        echo "vm.max_map_count has been defined!"
    else
        echo "vm.max_map_count = 262144" >> /etc/sysctl.conf
        sysctl -p
        echo "/etc/sysctl.conf 's vm.max_map_count is defined successfully!"
    fi
}

function change_etc_security_conf()
{
    if [ `grep -c "elasticsearch" /etc/security/limits.conf` -ne '0' ]; then
        echo "elasticsearch has been defined!"
    else
        echo "es soft nofile 65535" >> /etc/security/limits.conf
        echo "es hard nofile 65537" >> /etc/security/limits.conf
        echo "es soft nproc 4096" >> /etc/security/limits.conf
        echo "es hard nproc 4096" >> /etc/security/limits.conf
        echo "es soft memlock unlimited" >> /etc/security/limits.conf
        echo "es hard memlock unlimited" >> /etc/security/limits.conf
        echo "/etc/security/limits.conf 's elasticsearch is defined successfully!"
    fi
}
#
# main start
#
change_etc_sysctl_conf
change_etc_security_conf
