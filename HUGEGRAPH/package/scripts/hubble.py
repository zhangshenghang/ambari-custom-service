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
import base64

from resource_management.libraries.script.script import Script
from resource_management.core.logger import Logger
from resource_management.core.resources import Directory
from resource_management import *
import pwd
import grp
from resource_management.core.logger import Logger
from time import sleep
from datetime import datetime
import subprocess

class Master(Script):
    def install(self, env):
        import params
        env.set_params(params)

        self.stop(env)

        # 删除历史安装目录
        Execute('rm -rf /usr/hdp/3.1.5.0-152/hugegraph-toolchain*')

        # 安装包名称
        package_name = 'apache-hugegraph-toolchain-incubating.tar.gz'

        # Download Hubble package
        Execute('wget {0} -O {1}'.format(params.hubble_download,package_name))

        # Install hugegraph
        Execute('tar -zxvf {0} -C /usr/hdp/3.1.5.0-152/'.format(package_name))

        # 安装包重命名
        Execute('mv /usr/hdp/3.1.5.0-152/apache-hugegraph-toolchain-incubating* /usr/hdp/3.1.5.0-152/hugegraph-toolchain')

        # Remove Elasticsearch installation file
        Execute('rm -rf {0}'.format(package_name))

        check_dir_exists_flag = self.check_dir_exist('/usr/hdp/3.1.5.0-152/jdk-11.0.22')
        # JDK11目录不存在安装JDK11
        if not check_dir_exists_flag:
            # 安装JDK11,HugeGraph单独使用
            jdk_package_name = 'jdk11.tar.gz'
            Execute('wget {0} -O {1}'.format(params.hugegraph_jdk11_download, jdk_package_name))
            Execute('tar -zxvf {0} -C /usr/hdp/3.1.5.0-152'.format(jdk_package_name))
            # set JDK
            Execute("grep -qxF 'export JAVA_HOME=/usr/hdp/3.1.5.0-152/jdk-11.0.22' ~/.bashrc || echo 'export JAVA_HOME=/usr/hdp/3.1.5.0-152/jdk-11.0.22' >> ~/.bashrc ",user=params.hugegraph_user)
            Execute("grep -qxF 'export PATH=$JAVA_HOME/bin:$PATH' ~/.bashrc ||  echo 'export PATH=$JAVA_HOME/bin:$PATH' >> ~/.bashrc",user=params.hugegraph_user)

        # 删除pid目录
        Directory([params.hubble_pid_dir],
                  action="delete")

        # 创建pid目录
        Directory([params.hubble_log_dir, params.hubble_pid_dir],
                  mode=0755,
                  cd_access='a',
                  owner=params.hugegraph_user,
                  group=params.user_group,
                  create_parents=True
                  )

        # Ensure all files owned by elasticsearch user
        cmd = format("chown -R {hugegraph_user}:{user_group} {hubble_base_dir} {hubble_log_dir} {hubble_pid_dir}")
        Execute(cmd)



        Logger.info("Install complete")

    def configure(self, env):
        # Import properties defined in -config.xml file from the params class
        import params
        env.set_params(params)
        Execute('source ~/.bashrc')

        # 生成hugegraph_properties配置文件
        hubble_properties = InlineTemplate(params.hubble_properties)
        File(format("{hubble_base_dir}/conf/hugegraph-hubble.properties"),
             owner=params.hugegraph_user,
             group=params.user_group,
             content=hubble_properties)


        Logger.info("Configuration complete")

    # 判断目录是否存在，存在返回True，不存在返回False
    def check_dir_exist(self, dir):
        cmd = "if [ ! -d {0} ]; then echo 'false'; else echo 'true'; fi".format(dir)
        result = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True, universal_newlines=True).strip()
        if result == 'false':
            return False
        else:
            return True

    # 获取进程PID，如果不存在返回-1
    def find_hugegraph_pid(self, env):
        import params
        env.set_params(params)
        cmd = "ps -ef | grep \'{0}\' | grep -v grep | awk \'{{print $2}}\'".format(params.hugegraph_process_tag)
        result = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True, universal_newlines=True).strip()
        if result.isdigit():
            return result
        else:
            return -1

    def start(self, env):
        import params
        env.set_params(params)
        # Configure Elasticsearch
        self.configure(env)

        Execute(format("{hubble_base_dir}/bin/start-hubble.sh"),
            user=params.hugegraph_user)

        Execute(
            'ps -ef | grep '+params.hubble_process_tag+' | grep -v grep | awk \'{print $2}\' > ' + params.hubble_pid_file,
            user=params.hugegraph_user)





    def stop(self, env):
        import params
        env.set_params(params)
        Execute('ps -ef | grep '+params.hubble_process_tag+' | grep -v grep | awk \'{print $2}\' | xargs kill -9',
                user=params.hugegraph_user,
                ignore_failures=True)
        # 删除pid文件
        File([params.hubble_pid_file],
             action="delete")

        Logger.info("Stop complete!")


    def status(self, env):
        import status_params
        env.set_params(status_params)
        check_process_status(status_params.hubble_pid_file)

    def restart(self, env):
        self.stop(env)
        self.start(env)

    def test(self, env):
        import params
        env.set_params(params)
        Logger.info("******** Test ********")




if __name__ == "__main__":
    Master().execute()
