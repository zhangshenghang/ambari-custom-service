#!/usr/bin/env python
# -*- coding: utf-8 -*--
"""
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""
import json
import os

from resource_management.libraries.script.script import Script
from resource_management.core.logger import Logger
from resource_management.core.resources import Directory
from resource_management import *
import pwd
import grp
from resource_management.core.logger import Logger
from time import sleep
import subprocess
import hashlib
class Master(Script):

    def install(self, env):
        import params
        env.set_params(params)

        # 删除历史安装包
        self.remove_rpm('clickhouse-client')
        self.remove_rpm('clickhouse-server')
        self.remove_rpm('clickhouse-common-static-dbg')
        self.remove_rpm('clickhouse-common-static')


        # 下载Clickhouse安装包
        Execute('wget {0} -O clickhouse-server.rpm'.format(params.clickhouse_server_download))
        Execute('wget {0} -O clickhouse-common-static.rpm'.format(params.clickhouse_common_static_download))
        Execute('wget {0} -O clickhouse-common-static-dbg.rpm'.format(params.clickhouse_common_static_dbg_download))
        Execute('wget {0} -O clickhouse-client.rpm'.format(params.clickhouse_client_download))

        # 安装Clickhouse安装包
        Execute('rpm -ivh clickhouse-common-static.rpm')
        Execute('rpm -ivh clickhouse-common-static-dbg.rpm')
        Execute('rpm -ivh clickhouse-server.rpm')
        Execute('rpm -ivh clickhouse-client.rpm')

        # 删除安装包
        Execute('rm -rf clickhouse-server.rpm')
        Execute('rm -rf clickhouse-common-static.rpm')
        Execute('rm -rf clickhouse-common-static-dbg.rpm')
        Execute('rm -rf clickhouse-client.rpm')

        Logger.info("Install complete")



    # configure() 方法没有被 Ambari 默认触发（亲测），
    # 这个方法一般被 install()、start()、restart() 方法调用执行。
    # configure() 方法主要是执行服务配置、设置目录用户组等相关逻辑。
    def configure(self, env):
        # Import properties defined in -config.xml file from the params class
        import params
        if params.enable_authentication:
            remote_servers_string = '\t<{0}>'.format(params.cluster_name)
            sha256_password = hashlib.sha256(params.password.encode()).hexdigest()
            for host in params.clickhouse_service_host:
                shard = '\t\t<shard>\n' \
                        '\t\t\t<weight>1</weight>\n' \
                        '\t\t\t<internal_replication>true</internal_replication>\n' \
                        '\t\t\t<replica>\n' \
                        '\t\t\t\t<host>' + host + '</host>\n' \
                                                  '\t\t\t\t<port>' + params.tcp_port + '</port>\n' \
                                                                                       '\t\t\t\t<user>' + params.username + '</user>\n' \
                                                                                                                            '\t\t\t\t<password_sha256_hex>' + sha256_password + '</password_sha256_hex>\n' \
                                                                                                                                                                                '\t\t\t</replica>\n' \
                                                                                                                                                                                '\t\t</shard>\n'
                remote_servers_string = remote_servers_string + '\n' + shard
            remote_servers_string = remote_servers_string + '\t</{0}>'.format(params.cluster_name)
            params.remote_servers = remote_servers_string
        else:
            remote_servers_string = '\t<{0}>'.format(params.cluster_name)
            for host in params.clickhouse_service_host:
                shard = '\t\t<shard>\n' \
                        '\t\t\t<weight>1</weight>\n' \
                        '\t\t\t<internal_replication>true</internal_replication>\n' \
                        '\t\t\t<replica>\n' \
                        '\t\t\t\t<host>' + host + '</host>\n' \
                                                  '\t\t\t\t<port>' + params.tcp_port + '</port>\n' \
                                                                                       '\t\t\t</replica>\n' \
                                                                                       '\t\t</shard>\n'
                remote_servers_string = remote_servers_string + '\n' + shard
            remote_servers_string = remote_servers_string + '\t</{0}>'.format(params.cluster_name)
            params.remote_servers = remote_servers_string
        env.set_params(params)

        # 初始化配置文件 ， 配置文件中参数取值读取的是params.py里的变量，不是直接读取的fe.xml变量名
        print params.remote_servers
        clickhouse_config = InlineTemplate(params.clickhouse_config)
        File(format("/etc/clickhouse-server/config.xml"),
             owner=params.clickhouse_user,
             group=params.user_group,
             content=clickhouse_config)

        users_config = InlineTemplate(params.users_config)
        File(format("/etc/clickhouse-server/users.xml"),
             owner=params.clickhouse_user,
             group=params.user_group,
             content=users_config)

        Logger.info("Configuration complete")

    def start(self, env):
        import params
        env.set_params(params)
        # Configure Elasticsearch
        self.configure(env)
        Execute('clickhouse restart',user = params.clickhouse_user)



    def stop(self, env):
        import params
        env.set_params(params)
        # Stop Elasticsearch

        Logger.info("Stop complete!")
        # sleep(5)

        # kill elasticsearch-head
        # cmd = format("pm2 delete elasticsearch-head")
        # Execute(cmd, user='root', ignore_failures=True)

    def status(self, env):
        # Import properties defined in -env.xml file from the status_params class
        import status_params

        # This allows us to access the params.elastic_pid_file property as
        #  format('{elastic_pid_file}')
        env.set_params(status_params)

        # Use built-in method to check status using pidfile
        check_process_status(status_params.elastic_pid_file)

    def restart(self, env):
        self.stop(env)
        self.start(env)

    def test_master_check(self, env):
        Logger.info("******** custom process ********")
        import params
        if params.enable_authentication:
            remote_servers_string = '\t<{0}>'.format(params.cluster_name)
            sha256_password = hashlib.sha256(params.password.encode()).hexdigest()
            for host in params.clickhouse_service_host:
                shard = '\t\t<shard>\n' \
                        '\t\t\t<weight>1</weight>\n' \
                        '\t\t\t<internal_replication>true</internal_replication>\n' \
                        '\t\t\t<replica>\n' \
                        '\t\t\t\t<host>' + host + '</host>\n' \
                        '\t\t\t\t<port>' + params.tcp_port + '</port>\n' \
                        '\t\t\t\t<user>' + params.username + '</user>\n' \
                        '\t\t\t\t<password_sha256_hex>' + sha256_password + '</password_sha256_hex>\n' \
                        '\t\t\t</replica>\n' \
                        '\t\t</shard>\n'
                remote_servers_string = remote_servers_string + '\n' + shard
            remote_servers_string = remote_servers_string + '\t</{0}>'.format(params.cluster_name)
            params.remote_servers = remote_servers_string
        else:
            remote_servers_string = '\t<{0}>'.format(params.cluster_name)
            for host in params.clickhouse_service_host:
                shard = '\t\t<shard>\n' \
                        '\t\t\t<weight>1</weight>\n' \
                        '\t\t\t<internal_replication>true</internal_replication>\n' \
                        '\t\t\t<replica>\n' \
                        '\t\t\t\t<host>' + host + '</host>\n' \
                                                  '\t\t\t\t<port>' + params.tcp_port + '</port>\n' \
                                                                                       '\t\t\t</replica>\n' \
                                                                                       '\t\t</shard>\n'
                remote_servers_string = remote_servers_string + '\n' + shard
            remote_servers_string = remote_servers_string + '\t</{0}>'.format(params.cluster_name)
            params.remote_servers = remote_servers_string
        env.set_params(params)

        # 初始化配置文件 ， 配置文件中参数取值读取的是params.py里的变量，不是直接读取的fe.xml变量名
        print params.remote_servers
        clickhouse_config = InlineTemplate(params.clickhouse_config)
        File(format("/etc/clickhouse-server/c.xml"),
             owner=params.clickhouse_user,
             group=params.user_group,
             content=clickhouse_config)

        users_config = InlineTemplate(params.users_config)
        File(format("/etc/clickhouse-server/u.xml"),
             owner=params.clickhouse_user,
             group=params.user_group,
             content=users_config)

        Logger.info("Configuration complete")



    # 如果rpm存在则卸载
    def remove_rpm(self,rpm_name):
        if self.rpm_install_status(rpm_name):
            cmd = 'rpm -qa | grep "{0}" | xargs rpm -e'.format(rpm_name)
            Execute(cmd)

    # 判断某个rpm是否安装
    def rpm_install_status(self, rpm_name):
        cmd = 'rpm  -qa  |  grep  -q  "{0}"  &&  echo  "True"  ||  echo  "False"'.format(rpm_name)
        result = subprocess.check_output(cmd ,
                                         stderr=subprocess.STDOUT,
                                         shell=True,
                                         universal_newlines=True).strip()
        if result == 'True':
            return True
        else:
            return False

if __name__ == "__main__":
    Master().execute()
