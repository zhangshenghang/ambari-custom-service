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
from elastic_common import kill_process
import pwd
import grp
from resource_management.core.logger import Logger
from time import sleep
from datetime import datetime
import subprocess

class Kibana(Script):
    def install(self, env):
        import params
        env.set_params(params)

        # 删除历史安装目录
        Execute('rm -rf /usr/hdp/3.1.5.0-152/kibana*')

        # Download elasticsearch.tar.gz
        Execute('wget {0} -O kibana.tar.gz'.format(params.kibana_download))

        # Install Elasticsearch
        Execute('tar -zxvf kibana.tar.gz -C /usr/hdp/3.1.5.0-152/')

        # Remove Elasticsearch installation file
        Execute('rm -rf kibana.tar.gz')

        # 安装包重命名
        Execute('mv /usr/hdp/3.1.5.0-152/kibana* /usr/hdp/3.1.5.0-152/kibana')

        Logger.info("Install complete")

    def configure(self, env):
        # Import properties defined in -config.xml file from the params class
        import params

        # This allows us to access the params.elastic_pid_file property as
        # format('{elastic_pid_file}')
        env.set_params(params)

        # Update the port in the web UI that displays the connection to the Elasticsearch
        # cmd = format("cd {elastic_head_site}; sh ./changeHostName.sh {elasticsearch_port} {elasticsearch_head_port}")
        # Execute(cmd)

        # 删除pid目录
        Directory([params.kibana_pid_dir],
                  action="delete")

        # 创建pid目录
        Directory([params.kibana_log_dir, params.kibana_pid_dir],
                  mode=0755,
                  cd_access='a',
                  owner=params.elastic_user,
                  group=params.user_group,
                  create_parents=True
                  )

        # Ensure all files owned by elasticsearch user
        cmd = format("chown -R {elastic_user}:{user_group} {kibana_base_dir} {kibana_log_dir} {kibana_pid_dir}")
        Execute(cmd)

        # 生成Kibana配置文件
        kibana_conf = InlineTemplate(params.kibana_conf)
        File(format("{kibana_conf_base_dir}/kibana.yml"),
             owner=params.elastic_user,
             group=params.user_group,
             content=kibana_conf)

        Logger.info("Configuration complete")

    def start(self, env):
        import params
        env.set_params(params)
        # Configure Elasticsearch
        self.configure(env)

        # Start Elasticsearch
        cmd = format("nohup {kibana_base_dir}/bin/kibana > {kibana_log_dir}/kibana.log &")
        Execute(cmd, user=params.elastic_user)


        # get Kibana pid and write filex
        Execute(
            'ps -ef | grep kibana/src/cli/dist | grep -v grep | awk \'{print $2}\' > ' + params.kibana_pid_file,
            user=params.elastic_user)


    def stop(self, env):
        import params
        env.set_params(params)
        # Stop Elasticsearch
        Execute('ps -ef | grep kibana/src/cli/dist | grep -v grep | awk \'{print $2}\' | xargs kill -9',
                user=params.elastic_user,
                ignore_failures=True)
        # 删除pid文件
        File([params.kibana_pid_file], action="delete")

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
        check_process_status(status_params.kibana_pid_file)

    def restart(self, env):
        self.stop(env)
        self.start(env)


if __name__ == "__main__":
    Kibana().execute()
