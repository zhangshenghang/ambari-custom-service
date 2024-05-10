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
        Execute('rm -rf /usr/hdp/3.1.5.0-152/hugegraph*')

        # 安装包名称
        package_name = 'apache-hugegraph-incubating.tar.gz'

        # Download apache-hugegraph-incubating.tar.gz
        Execute('wget {0} -O {1}'.format(params.hugegraph_server_download,package_name))

        # Install hugegraph
        Execute('tar -zxvf {0} -C /usr/hdp/3.1.5.0-152/'.format(package_name))

        # 安装包重命名
        Execute('mv /usr/hdp/3.1.5.0-152/apache-hugegraph-incubating* /usr/hdp/3.1.5.0-152/hugegraph')

        # Remove Elasticsearch installation file
        Execute('rm -rf {0}'.format(package_name))

        # 安装JDK11,HugeGraph单独使用
        jdk_package_name = 'jdk11.tar.gz'
        Execute('wget {0} -O {1}'.format(params.hugegraph_jdk11_download, jdk_package_name))
        Execute('tar -zxvf {0} -C /usr/hdp/3.1.5.0-152/hugegraph'.format(jdk_package_name))
        Execute('wget {0} -P /usr/hdp/3.1.5.0-152/hugegraph/conf'.format(params.keystore_download))
        # set JDK
        Execute("grep -qxF 'export JAVA_HOME=/usr/hdp/3.1.5.0-152/hugegraph/jdk-11.0.22' ~/.bashrc || echo 'export JAVA_HOME=/usr/hdp/3.1.5.0-152/hugegraph/jdk-11.0.22' >> ~/.bashrc ",user=params.hugegraph_user)
        Execute("grep -qxF 'export PATH=$JAVA_HOME/bin:$PATH' ~/.bashrc ||  echo 'export PATH=$JAVA_HOME/bin:$PATH' >> ~/.bashrc",user=params.hugegraph_user)

        # 删除pid目录
        Directory([params.hugegraph_pid_dir],
                  action="delete")

        # 创建pid目录
        Directory([params.hugegraph_log_dir, params.hugegraph_pid_dir],
                  mode=0755,
                  cd_access='a',
                  owner=params.hugegraph_user,
                  group=params.user_group,
                  create_parents=True
                  )

        # Ensure all files owned by elasticsearch user
        cmd = format("chown -R {hugegraph_user}:{user_group} {hugegraph_base_dir} {hugegraph_log_dir} {hugegraph_pid_dir}")
        Execute(cmd)



        Logger.info("Install complete")

    def configure(self, env):
        # Import properties defined in -config.xml file from the params class
        import params
        env.set_params(params)
        Execute('source ~/.bashrc')


        # 生成hugegraph_properties配置文件
        gremlin_serer_yaml = InlineTemplate(params.gremlin_serer_yaml)
        File(format("{hugegraph_base_dir}/conf/gremlin-server.yaml"),
             owner=params.hugegraph_user,
             group=params.user_group,
             content=gremlin_serer_yaml)



        # 生成hugegraph_properties配置文件
        hugegraph_properties = InlineTemplate(params.hugegraph_properties)
        File(format("{hugegraph_base_dir}/conf/graphs/hugegraph.properties"),
             owner=params.hugegraph_user,
             group=params.user_group,
             content=hugegraph_properties)

        # 多图的配置，在Custom中添加
        for hugegraph_config in params.hugegraph_configs:
            if hugegraph_config.startswith("hugegraph."):
                print hugegraph_config
                content = format(params.hugegraph_configs[hugegraph_config])
                content_list = content.split('\n')
                if len(content_list) > 1:
                    for content_line in content_list:
                        if content_line.startswith("store"):
                            store = content_line.split("=")[-1]
                            File(format("{hugegraph_base_dir}/conf/graphs/" + store + ".properties"),
                                 owner=params.hugegraph_user,
                                 group=params.user_group,
                                 content=format(content))
                else:
                    print("多图配置每次修改配置需要重新添加，因为修改后换行失效，这是一个小问题，之后版本会修复")

        result = subprocess.check_output(format('sudo -i -u '+params.hugegraph_user+' {hugegraph_base_dir}/bin/init-store.sh'),
                                         stderr=subprocess.STDOUT,
                                         shell=True,
                                         universal_newlines=True)

        print result

        if 'Initialization finished.' in result:
            print "HugeGraph Initialization finished."
        else:
            raise Exception("HugeGraph Initialization failed.")

        hugegraph_properties = InlineTemplate(params.rest_server_properties)
        File(format("{hugegraph_base_dir}/conf/rest-server.properties"),
             owner=params.hugegraph_user,
             group=params.user_group,
             content=hugegraph_properties)

        try:
            # 启动HugeGraph服务，并打印启动输出内容
            print subprocess.check_output(format('sudo -i -u '+params.hugegraph_user+' {hugegraph_base_dir}/bin/start-hugegraph.sh'),
                                         stderr=subprocess.STDOUT,
                                         shell=True,
                                         universal_newlines=True)
        except subprocess.CalledProcessError as e:
            error_output = e.output
            print(error_output)

        # 3分钟内进程如果未拉起，则跳出循环
        import time
        start_time = time.time()
        while True:
            current_time = time.time()
            elapsed_time = current_time - start_time
            # 如果经过的时间超过三分钟，退出循环
            if elapsed_time >= 180:
                break
            time.sleep(5)
            Logger.info("waiting for hugegraph to complete startup")
            if self.find_hugegraph_pid(env) != -1:
                break

        if self.find_hugegraph_pid(env) == -1:
            raise Exception("HugeGraph start failed.")
        else:
            print "HugeGraph process ."

        Execute(
            'ps -ef | grep org.apache.hugegraph.dist.HugeGraphServer | grep -v grep | awk \'{print $2}\' > ' + params.hugegraph_pid_file,
            user=params.hugegraph_user)

        check_running_status_cmd = 'echo `curl -o /dev/null -s -w %{http_code} "http://'+params.hostname+':'+params.restserver_port+'/graphs/hugegraph/graph/vertices"`'
        print check_running_status_cmd
        check_running_status = subprocess.check_output(check_running_status_cmd,
                                      stderr=subprocess.STDOUT,
                                      shell=True,
                                      universal_newlines=True)
        Logger.info("status:{0}".format(check_running_status))
        if check_running_status.strip() == '200':
            print "HugeGraph start success."
        else:
            raise Exception("HugeGraph start failed.")
        # This allows us to access the params.elastic_pid_file property as
        # format('{elastic_pid_file}')


        Logger.info("Configuration complete")


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



    def stop(self, env):
        import params
        env.set_params(params)
        Execute('ps -ef | grep '+params.hugegraph_process_tag+' | grep -v grep | awk \'{print $2}\' | xargs kill -9',
                user=params.hugegraph_user,
                ignore_failures=True)
        # 删除pid文件
        File([params.hugegraph_pid_file],
             action="delete")

        Logger.info("Stop complete!")
        # sleep(5)

        # kill elasticsearch-head
        # cmd = format("pm2 delete elasticsearch-head")
        # Execute(cmd, user='root', ignore_failures=True)



    def status(self, env):
        import status_params
        env.set_params(status_params)
        check_process_status(status_params.hugegraph_pid_file)

    def restart(self, env):
        self.stop(env)
        self.start(env)

    def test(self, env):
        import params
        env.set_params(params)
        Logger.info("******** 设置集群密码 ********")





if __name__ == "__main__":
    Master().execute()
