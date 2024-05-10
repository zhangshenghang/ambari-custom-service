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

class Cerebro(Script):
    def install(self, env):
        import params
        env.set_params(params)

        Execute('rm -rf /usr/hdp/3.1.5.0-152/cerebro')

        # Download cerebro.tar.gz
        Execute('wget {0} -O cerebro.tar.gz'.format(params.cerebro_download))

        # Install Cerebro
        Execute('tar -zxvf cerebro.tar.gz -C /usr/hdp/3.1.5.0-152/')
        Execute('mv /usr/hdp/3.1.5.0-152/cerebro-0.9.4 /usr/hdp/3.1.5.0-152/cerebro')

        # Remove Cerebro installation file
        Execute('rm -rf cerebro.tar.gz')

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
        Directory([params.cerebro_pid_dir],
                  action="delete")

        # 创建目录
        Directory([params.cerebro_log_dir, params.cerebro_pid_dir],
                  mode=0755,
                  cd_access='a',
                  owner=params.elastic_user,
                  group=params.user_group,
                  create_parents=True
                  )

        # Ensure all files owned by elasticsearch user
        cmd = format("chown -R {elastic_user}:{user_group} {cerebro_base_dir} {cerebro_log_dir} {cerebro_pid_dir}")
        Execute(cmd)

        cerebro_conf = InlineTemplate(params.cerebro_conf)
        File(format("{cerebro_base_dir}/conf/application.conf"),
             owner=params.elastic_user,
             group=params.user_group,
             content=cerebro_conf)

        Logger.info("Configuration complete")

    def start(self, env):
        import params
        env.set_params(params)
        # Configure Elasticsearch
        self.configure(env)

        # Start Cerebro
        cmd = format("nohup {cerebro_base_dir}/bin/cerebro > {cerebro_log_dir}/nohup.log &")
        Execute(cmd, user=params.elastic_user)

        # get cerebro pid and write filex
        Execute(
            'ps -ef | grep cerebro.cerebro-0.9.4-launcher.jar | grep -v grep | awk \'{print $2}\' > ' + params.cerebro_pid_file,
            user=params.elastic_user)


    def stop(self, env):
        import params
        env.set_params(params)
        # Stop Elasticsearch
        Execute('ps -ef | grep cerebro.cerebro-0.9.4-launcher.jar | grep -v grep | awk \'{print $2}\' | xargs kill -9',
                user=params.elastic_user,
                ignore_failures=True)
        # 删除pid文件
        File([params.cerebro_pid_file],
             action="delete")

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
        check_process_status(status_params.cerebro_pid_file)

    def restart(self, env):
        self.stop(env)
        self.start(env)


if __name__ == "__main__":
    Cerebro().execute()
