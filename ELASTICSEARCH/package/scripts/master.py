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
from elastic_common import kill_process
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

        # 删除历史安装目录
        Execute('rm -rf /usr/hdp/3.1.5.0-152/elasticsearch*')

        # backups elasticsearch path_data
        path_data_es = params.path_data.split(',')
        for i in range(len(path_data_es)):
            result = subprocess.check_output('[ -d "{0}" ] && echo 0 || echo 1'.format(path_data_es[i]),
                                             stderr=subprocess.STDOUT,
                                             shell=True,
                                             universal_newlines=True)
            if int(result.strip()) == 1:
                Logger.info("First Install")
            else:
                # 历史数据目录存在，备份目录
                Logger.info("History installed services, backups it")
                cmd = "mv {0} {1}".format(path_data_es[i], path_data_es[i]+'_backup_'+datetime.now().strftime("%Y%m%d%H%M%S"))
                Execute(cmd)

        # Download elasticsearch.tar.gz
        Execute('wget {0} -O elasticsearch.tar.gz'.format(params.elastic_download))

        # Install Elasticsearch
        Execute('tar -zxvf elasticsearch.tar.gz -C /usr/hdp/3.1.5.0-152/')

        # 安装包重命名
        Execute('mv /usr/hdp/3.1.5.0-152/elasticsearch* /usr/hdp/3.1.5.0-152/elasticsearch')

        # Remove Elasticsearch installation file
        Execute('rm -rf elasticsearch.tar.gz')

        # sh config file in targethost
        cmd = format("cd {elastic_scripts_dir}; chmod +x ./changeOsConfToES.sh && sh ./changeOsConfToES.sh")
        Execute(cmd)

        Execute(format("mkdir {elastic_base_dir}/config/certs"))
        Execute('wget {0} -O elastic-certificates.p12'.format(params.elastic_cert_download))
        Execute(format('mv elastic-certificates.p12 {elastic_base_dir}/config/certs'))



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
        Directory([params.elastic_pid_dir],
                  action="delete")

        # 创建pid目录
        Directory([params.elastic_log_dir, params.elastic_pid_dir],
                  mode=0755,
                  cd_access='a',
                  owner=params.elastic_user,
                  group=params.user_group,
                  create_parents=True
                  )

        # Ensure all files owned by elasticsearch user
        cmd = format("chown -R {elastic_user}:{user_group} {elastic_base_dir} {elastic_log_dir} {elastic_pid_dir}")
        Execute(cmd)

        # 生成jvm配置文件
        elastic_jvm = InlineTemplate(params.elastic_jvm_conf)
        File(format("{elastic_conf_base_dir}/jvm.options"),
             owner=params.elastic_user,
             group=params.user_group,
             content=elastic_jvm)

        elasticsearch_yml = InlineTemplate(params.elasticsearch_yml)
        File(format("{elastic_conf_base_dir}/elasticsearch.yml"),
             owner=params.elastic_user,
             group=params.user_group,
             content=elasticsearch_yml)

        # mkdir elasticsearch path_data
        path_data_es = params.path_data.split(',')
        for i in range(len(path_data_es)):
            Directory([path_data_es[i]],
                      mode=0755,
                      cd_access='a',
                      owner=params.elastic_user,
                      group=params.user_group,
                      create_parents=True
                      )
            cmd = "chown -R {0}:{1} {2}".format(params.elastic_user, params.user_group, path_data_es[i])
            Execute(cmd)

        Logger.info("Configuration complete")

    def start(self, env):
        import params
        env.set_params(params)
        # Configure Elasticsearch
        self.configure(env)

        # Start Elasticsearch
        cmd = format("{elastic_base_dir}/bin/elasticsearch -d -p {elastic_pid_file}")
        Execute(cmd, user=params.elastic_user)

        Execute(
            'source /etc/profile',
            user=params.elastic_user)
        # get Elasticsearch pid and write filex
        Execute(
            'ps -ef | grep elasticsearch/config | grep -v grep | awk \'{print $2}\' > ' + params.elastic_pid_file,
            user=params.elastic_user)

        Directory([format("{elastic_tool_dir}")], mode=0755, cd_access='a', owner=params.elastic_user,
                  group=params.user_group, create_parents=True )
        metrics_jar_exist = self.fileExists(format('{elastic_tool_dir}/ambari-elastic-metrics.jar'))
        if metrics_jar_exist:
            print('Metrics监控jar包已存在，准备启动Metrics监控')
        else:
            print('Metrics监控jar包不存在，准备下载Metrics监控jar包')
            Execute(format('wget {elastic_metrics_download} -O {elastic_tool_dir}/ambari-elastic-metrics.jar'))

        metrics_pid = self.find_metric_pid(env)
        if metrics_pid != -1:
            # KILL进程，重新启动
            Execute('kill -9 {0}'.format(metrics_pid))

        params_data = {
            "es": {
                "ip": params.elasticsearch_service_host,
                "port": params.elasticsearch_port,
                "pid_file": params.elastic_pid_file,
                "log_dir": params.elastic_log_dir
            },
            "metrics_collector": {
                "ip": params.metrics_collector_host,
                "port": params.metrics_collector_port
            }
        }
        Logger.info("Metrics parameter: {0}".format(json.dumps(params_data)))
        if params.xpack_security_enabled == 'true':
            # 启动Metrics进程
            cmd = "nohup java -jar {0}/{1} {2} {3} > {0}/run.log &".format(params.elastic_tool_dir,
                                                                       params.elastic_metrics_jar_name,
                                                                       base64.b64encode(
                                                                           json.dumps(params_data).encode()),
                                                                           base64.b64encode('elastic:'+params.elastic_password.encode()))
        else:
            # 启动Metrics进程
            cmd = "nohup java -jar {0}/{1} {2} > {0}/run.log &".format(params.elastic_tool_dir,
                                                                           params.elastic_metrics_jar_name,
                                                                           base64.b64encode(json.dumps(params_data).encode()))

        Logger.info(cmd)
        Execute(cmd, user=params.elastic_user)

        sleep(30)

        if params.xpack_security_enabled == 'true':
            if params.elasticsearch_service_host == params.hostname:
                Logger.info("当前节点为首个节点，将在当前节点初始化密码")
                file_exist = self.fileExists(params.elastic_password_init_file)
                if file_exist:
                    Logger.info("密码已经初始化完成,无需再次初始化")
                else:
                    if params.elasticsearch_service_host == params.hostname:
                        print "当前为主机节点，初始化密码"
                        Logger.info("ElasticSearch password init")
                        self.password_init(env)
                        # 创建文件说明密码已经初始化过
                        File(params.elastic_password_init_file,
                             owner=params.elastic_user,
                             group=params.user_group,
                             content='true')
                    else:
                        print "当前非第一个节点不进行密码初始化"
            else:
                Logger.info("当前节点非密码管理节点")

    # 根据PID查询进程是否存在
    def process_exist(self, pid):
        try:
            os.kill(pid, 0)
            logger.info("process already exists! ")
            process_is_exist = True
        except OSError:
            logger.error("Process with pid {0} is not running.".format(pid))
            process_is_exist = False
        return process_is_exist

    # 查看Metrics程序是否已经在运行，如果运行返回True
    def find_metric_pid(self, env):
        import params
        env.set_params(params)
        cmd = "ps -ef | grep \'{0}\' | grep -v grep | awk \'{{print $2}}\'".format(params.elastic_metrics_jar_name)
        result = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True, universal_newlines=True).strip()
        if result.isdigit():
            return result
        else:
            return -1

    # 判断文件是否存在
    def fileExists(self,file_path):
        # 1代表不存在，0代表文件存在
        cmd = format('[ -f "{0}" ] && echo 0 || echo 1'.format(file_path))
        print cmd
        result = subprocess.check_output(cmd,
                                         stderr=subprocess.STDOUT,
                                         shell=True,
                                         universal_newlines=True)
        if int(result.strip()) == 1:
            return False
        else:
            return True

    def stop(self, env):
        import params
        env.set_params(params)
        # Stop Elasticsearch
        Execute('ps -ef | grep elasticsearch/config | grep -v grep | awk \'{print $2}\' | xargs kill -9',
                user=params.elastic_user,
                ignore_failures=True)
        # 删除pid文件
        File([params.elastic_pid_file],
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
        check_process_status(status_params.elastic_pid_file)

    def restart(self, env):
        self.stop(env)
        self.start(env)

    def password_init(self, env):
        import params
        env.set_params(params)
        Logger.info("******** 设置集群密码 ********")
        try:
            result = subprocess.check_output(
                format(
                    "echo -e 'y\\n{elastic_password}\\n{elastic_password}\\n{elastic_password}\\n{elastic_password}\\n{elastic_password}\\n{elastic_password}\\n{elastic_password}\\n{elastic_password}\\n{elastic_password}\\n{elastic_password}\\n{elastic_password}\\n{elastic_password}\\n' | {elastic_base_dir}/bin/elasticsearch-setup-passwords interactive 2>&1"),
                stderr=subprocess.STDOUT,
                shell=True,
                universal_newlines=True)
            print result
        except subprocess.CalledProcessError as e:
            # 捕获执行失败时返回的内容
            error_output = e.output
            if 'has already been changed on this cluster' in error_output:
                print('集群已经设置过密码')
            print(error_output)


if __name__ == "__main__":
    Master().execute()
