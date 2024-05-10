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


class Be(Script):

    def install(self, env):
        import params
        env.set_params(params)
        # 安装BE的hostname节点
        if params.hostname not in params.frontend_hosts:
            # 如果be节点未安装FE
            if params.hostname not in params.frontend_observer_hosts:
                if params.hostname not in params.frontend_follower_hosts:
                    # 如果be节点未安装Observer，则清空历史安装
                    # 安装前清空配置元数据
                    Execute(format('rm -rf {meta_dir}'))
                    Execute(format('rm -rf /usr/hdp/3.1.5.0-152/doris'))

        result = subprocess.check_output('[ -d "/usr/hdp/3.1.5.0-152/doris" ] && echo 0 || echo 1', stderr=subprocess.STDOUT,
                                         shell=True,
                                         universal_newlines=True)
        if int(result.strip()) == 1:
            Logger.info("downloading installation package.")
            # 目录不存在，下载安装包
            install_package_name = "apache-doris.tar.gz"

            # 下载Doris安装包
            download_cmd = 'grep -q "avx2" /proc/cpuinfo && wget {0} -O {2} || wget {1} -O {2}'.format(
                params.doris_download, params.doris_noavx2_download, install_package_name)
            Logger.info("Download cmd is : " + download_cmd)
            Execute(download_cmd)
            # 将安装包解压到指定目录
            Execute('tar -zxvf {0} -C /usr/hdp/3.1.5.0-152/'.format(install_package_name))
            # 安装包重命名
            Execute('mv /usr/hdp/3.1.5.0-152/apache-doris-{0}-bin-x64* /usr/hdp/3.1.5.0-152/doris'.format(
                params.doris_version))

            # 删除下载的安装包
            Execute('rm -rf {0}'.format(install_package_name))
        else:
            Logger.info("Doris FE installed, skipping downloading installation package.")

        # 初始化环境变量
        cmd = format("cd {doris_scripts_dir}; chmod +x ./changeBEOsConf.sh && sh ./changeBEOsConf.sh")
        Execute(cmd)

        # 删除可能存在的历史缓存
        Execute('rm -rf /usr/hdp/3.1.5.0-152/doris/be/storage/*')

        # 创建日志目录
        Execute(format('mkdir -p {sys_log_dir} && chown -R {doris_user}:{user_group} {sys_log_dir}'))
        Execute(format('mkdir -p {PPROF_TMPDIR} && chown -R {doris_user}:{user_group} {PPROF_TMPDIR}'))

        # 将服务目录权限设置为doris
        Execute(format('chown -R {doris_user}:{user_group} {doris_base_dir}'))

        # 设置 pid 目录权限
        Execute(format('mkdir -p {doris_pid_dir} && chown -R {doris_user}:{user_group} {doris_pid_dir}'))


        Logger.info("Install complete")



    def configure(self, env):
        # Import properties defined in -config.xml file from the params class
        import params
        env.set_params(params)

        # 初始化配置文件 ， 配置文件中参数取值读取的是params.py里的变量，不是直接读取的fe.xml变量名
        File(format("{doris_be_conf_base_dir}/be.conf"),
             owner=params.doris_user,
             group=params.user_group,
             content=Template('be.conf.j2')
             )

        Logger.info("Configuration complete")

    def start(self, env):
        import params
        env.set_params(params)
        self.configure(env)
        # 创建日志目录
        Execute(format('mkdir -p {sys_log_dir} && chown -R {doris_user}:{user_group} {sys_log_dir}'))
        Execute(format('mkdir -p {PPROF_TMPDIR} && chown -R {doris_user}:{user_group} {PPROF_TMPDIR}'))
        # 添加be节点到fe中，当前目录为/var/lib/ambari-agent
        Execute(params.download_mysql_tool_link)
        # 将安装包解压到指定目录
        frontend_host = params.frontend_hosts[0]
        add_be_sql = "\"ALTER SYSTEM ADD BACKEND \\\"{0}:{1}\\\";\"".format(params.hostname,
                                                                            params.be_heartbeat_service_port)
        add_be_sql_all = 'java -jar ambari-mysql-tool.jar --type=execute --uri={0} --sql={1} --user={2} --password={3}'.format(
            frontend_host + ":" + params.query_port, add_be_sql, params.fe_user, params.fe_password)
        Logger.info("Run add BE :"+add_be_sql_all)
        result = subprocess.check_output([add_be_sql_all], stderr=subprocess.STDOUT, shell=True,
                                         universal_newlines=True)
        Logger.info("Run result:" + result.replace('\n', '').strip())
        if result.replace('\n', '').strip() == '0':
            # 执行失败
            Logger.info("添加BE成功")
        else:
            Logger.info("BE已经添加,无需重复添加")


        # Start Elasticsearch
        cmd = format("{doris_base_dir}/be/bin/start_be.sh --daemon")
        Execute(cmd, user=params.doris_user)

        # 获取Doris进程ID写入到文件
        Execute(
            'ps -ef | grep doris_be | grep -v grep | awk \'{print $2}\' > ' + params.doris_be_pid_file,
            user=params.doris_user)



    def stop(self, env):
        import params
        env.set_params(params)
        # Kill掉 FE进程
        Execute('ps -ef | grep doris_be | grep -v grep | awk \'{print $2}\' | xargs kill -9',
                user=params.doris_user,
                ignore_failures=True)

        # 删除pid文件
        File([params.doris_be_pid_file],
             action="delete")

        Logger.info("Stop complete!")

    def status(self, env):
        # Import properties defined in -env.xml file from the status_params class
        import status_params

        # This allows us to access the params.elastic_pid_file property as
        #  format('{elastic_pid_file}')
        env.set_params(status_params)
        check_process_status(status_params.doris_be_pid_file)
        # Use built-in method to check status using pidfile
        # 检查进程ID在不在
        Logger.info("Check BE process status complete!")

    def restart(self, env):
        self.stop(env)
        self.start(env)

    def test_master_check(self, env):
        import params
        Logger.info("******** custom process ********")
        Logger.info("custom doris service successfully!")


if __name__ == "__main__":
    Be().execute()
