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
# from elastic_common import kill_process
import pwd
import grp
from resource_management.core.logger import Logger
from time import sleep
import subprocess


class Coordinator(Script):

    def install(self, env):
        import params
        env.set_params(params)

        # 删除历史安装目录
        Execute('rm -rf /usr/hdp/3.1.5.0-152/{0}'.format(params.presto_dir_name))
        Execute('rm -f {0}'.format(params.presto_pid_file))
        Execute('rm -rf {0}'.format(params.presto_pid_dir))
        Execute('rm -rf {0}'.format(params.node_data_dir))

        Logger.info("downloading installation package.")
        # 目录不存在，下载安装包
        install_package_name = "presto.tar.gz"
        # Download
        Execute('wget {0} -O {1}'.format(params.presto_download,install_package_name))
        # 将安装包解压到指定目录
        Execute('tar -zxvf {0} -C /usr/hdp/3.1.5.0-152/'.format(install_package_name))

        # 安装包重命名
        Execute('mv /usr/hdp/3.1.5.0-152/presto-server-{0} /usr/hdp/3.1.5.0-152/{1}'.format(
                params.presto_version,params.presto_dir_name))
        # 删除下载的安装包
        Execute('rm -rf {0}'.format(install_package_name))
        # 创建etc目录
        Directory(format('{presto_base_dir}/etc/catalog'),
                  mode=0755,
                  cd_access='a',
                  owner=params.presto_user,
                  group=params.user_group,
                  create_parents=True
                  )

        # 服务目录权限设置
        Execute(format('chown -R {presto_user}:{user_group} {presto_base_dir}'))


        # 设置 pid 目录权限
        Execute(format('mkdir -p {presto_pid_dir} && chown -R {presto_user}:{user_group} {presto_pid_dir}'))

        # 设置 数据 目录权限
        Execute(format('mkdir -p {node_data_dir} && chown -R {presto_user}:{user_group} {node_data_dir}'))

        Logger.info("Install complete")



    def configure(self, env):
        # Import properties defined in -config.xml file from the params class
        import params
        env.set_params(params)

        # 生成 config.properties 配置文件
        config_properties = InlineTemplate(params.config_properties)
        File(format("{presto_base_dir}/etc/config.properties"),
             owner=params.presto_user,
             group=params.user_group,
             content=config_properties)

        node_content = 'node.environment=' +params.node_environment + '\nnode.data-dir=' +params.node_data_dir + '\nnode.id=' + params.hostname

        # 初始化配置文件 ， 配置文件中参数取值读取的是params.py里的变量，不是直接读取的fe.xml变量名
        File(format("{presto_base_dir}/etc/node.properties"),
             owner=params.presto_user,
             group=params.user_group,
             content=node_content
             )

        # 生成 config.properties 配置文件
        jvm_config_content = InlineTemplate(params.jvm_config)
        # 初始化配置文件
        File(format("{presto_base_dir}/etc/jvm.config"),
             owner=params.presto_user,
             group=params.user_group,
             content=jvm_config_content
             )

        # 生成日志配置文件
        log_config_content = InlineTemplate(params.log_config)
        File(format("{presto_base_dir}/etc/log.properties"),
             owner=params.presto_user,
             group=params.user_group,
             content=log_config_content
             )

        # 生成连接器
        File(format("{presto_base_dir}/etc/catalog/hive.properties"),
             content=Template('hive.conf.j2'),
             owner=params.presto_user,
             group=params.user_group,
             mode=0755
             )

        Logger.info("Configuration complete")

    def start(self, env):
        import params
        env.set_params(params)
        self.configure(env)

        # Start Presto
        cmd = format("{presto_base_dir}/bin/launcher start")
        Execute(cmd, user=params.presto_user)

        sleep(5)

        # 获取 Presto 进程ID写入到文件
        Execute(
            'ps -ef | grep  com.facebook.presto.server.PrestoServer | grep -v grep | awk \'NR==1{print $2}\' > ' + params.presto_pid_file,
            user=params.presto_user)



    def stop(self, env):
        import params
        env.set_params(params)
        # Kill掉 FE进程
        Execute('ps -ef | grep com.facebook.presto.server.PrestoServer | grep -v grep | awk \'{print $2}\' | xargs kill -9',
                user=params.presto_user,
                ignore_failures=True)

        # 删除pid文件
        File([params.presto_pid_file],
             action="delete")

        Logger.info("Stop complete!")

    def status(self, env):
        # Import properties defined in -env.xml file from the status_params class
        import status_params

        # This allows us to access the params.elastic_pid_file property as
        #  format('{elastic_pid_file}')
        env.set_params(status_params)
        check_process_status(status_params.presto_pid_file)
        # Use built-in method to check status using pidfile
        # 检查进程ID在不在
        Logger.info("Check BE process status complete!")

    def restart(self, env):
        self.stop(env)
        self.start(env)

    def test_master_check(self, env):
        import params
        Logger.info("******** custom process ********")
        Logger.info("custom presto service successfully!")


if __name__ == "__main__":
    Coordinator().execute()
