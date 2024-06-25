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

class Fe(Script):

    # 查看所有节点状态，
    def node_check(self, env):
        import params
        env.set_params(params)

        Logger.info("检查BE添加状态")
        frontend_host = params.frontend_hosts[0]
        # 查看BE添加状态
        Execute(format("rm -f {mysql_tool_file_name}* && wget {mysql_tool_download}"))
        add_be_sql_all = 'java -jar ambari-mysql-tool.jar --type=query --uri={0} --sql={1} --user={2} --password={3}'.format(
            frontend_host + ":" + params.query_port, "\"SHOW PROC '/backends';\"", params.fe_user, params.fe_password)
        result = subprocess.check_output([add_be_sql_all], stderr=subprocess.STDOUT, shell=True,
                                         universal_newlines=True)
        if 'Caused by: java.net.ConnectException: Connection refused (Connection refused)' in result :
            Logger.info('查询节点超时,切换节点,超时节点:{0}'.format(frontend_host+":"+params.query_port))
            # 当前连接接口连接失败
            for host in params.frontend_follower_hosts:
                Logger.info('查询节点:{0}'.format(host+":"+params.query_port))
                add_be_sql_all = 'java -jar ambari-mysql-tool.jar --type=query --uri={0} --sql={1} --user={2} --password={3}'.format(
                    host + ":" + params.query_port, "\"SHOW PROC '/backends';\"", params.fe_user,
                    params.fe_password)
                result = subprocess.check_output([add_be_sql_all], stderr=subprocess.STDOUT, shell=True,
                                                 universal_newlines=True)
                if 'Caused by: java.net.ConnectException: Connection refused (Connection refused)' not in result:
                    Logger.info('执行成功,跳出循环')
                    break

        formatted_data = json.dumps(json.loads(result), indent=4, ensure_ascii=False)
        Logger.info('BackEnd list:')
        print(formatted_data)

        add_fe_observer_sql_all = 'java -jar ambari-mysql-tool.jar --type=query --uri={0} --sql={1} --user={2} --password={3}'.format(
            frontend_host + ":" + params.query_port, "\"SHOW PROC '/frontends';\"", params.fe_user, params.fe_password)
        result = subprocess.check_output([add_fe_observer_sql_all], stderr=subprocess.STDOUT, shell=True,
                                         universal_newlines=True)

        if 'Caused by: java.net.ConnectException: Connection refused (Connection refused)' in result :
            Logger.info('查询节点超时,切换节点,超时节点:{0}'.format(frontend_host+":"+params.query_port))
            # 当前连接接口连接失败
            for host in params.frontend_follower_hosts:
                Logger.info('查询节点:{0}'.format(host+":"+params.query_port))
                add_fe_observer_sql_all = 'java -jar ambari-mysql-tool.jar --type=query --uri={0} --sql={1} --user={2} --password={3}'.format(
                    host + ":" + params.query_port, "\"SHOW PROC '/frontends';\"", params.fe_user,
                    params.fe_password)
                result = subprocess.check_output([add_fe_observer_sql_all], stderr=subprocess.STDOUT, shell=True,
                                                 universal_newlines=True)
                if 'Caused by: java.net.ConnectException: Connection refused (Connection refused)' not in result:
                    Logger.info('执行成功,跳出循环')
                    break

        formatted_data = json.dumps(json.loads(result), indent=4, ensure_ascii=False)
        Logger.info('Frontend list:')
        print(formatted_data)
        Logger.info("检查执行完成")

    def add_backends(self,env):
        import params
        env.set_params(params)
        Execute(params.download_mysql_tool_link)
        for be_host in params.be_hosts:
            # 将安装包解压到指定目录
            frontend_host = params.frontend_hosts[0]
            add_be_sql = "\"ALTER SYSTEM ADD BACKEND \\\"{0}:{1}\\\";\"".format(be_host,
                                                                                params.be_heartbeat_service_port)
            add_be_sql_all = 'java -jar ambari-mysql-tool.jar --type=execute --uri={0} --sql={1} --user={2} --password={3}'.format(
                frontend_host + ":" + params.query_port, add_be_sql, params.fe_user, params.fe_password)
            Logger.info("Run add BE :" + add_be_sql_all)
            result = subprocess.check_output([add_be_sql_all], stderr=subprocess.STDOUT, shell=True,
                                             universal_newlines=True)
            Logger.info("Run result:" + result.replace('\n', '').strip())

            if 'Caused by: java.net.ConnectException: Connection refused (Connection refused)' in result:
                Logger.info('节点超时,切换节点,超时节点:{0}'.format(frontend_host + ":" + params.query_port))
                # 当前连接接口连接失败
                for host in params.frontend_follower_hosts:
                    Logger.info('节点:{0}'.format(host + ":" + params.query_port))
                    add_be_sql_all = 'java -jar ambari-mysql-tool.jar --type=execute --uri={0} --sql={1} --user={2} --password={3}'.format(
                        host + ":" + params.query_port, add_be_sql, params.fe_user, params.fe_password)
                    Logger.info("Run add BE :" + add_be_sql_all)
                    result = subprocess.check_output([add_be_sql_all], stderr=subprocess.STDOUT, shell=True,
                                                     universal_newlines=True)
                    if 'Caused by: java.net.ConnectException: Connection refused (Connection refused)' not in result:
                        Logger.info('执行成功,跳出循环')
                        break

            if result.replace('\n', '').strip() == '0':
                # 执行成功
                Logger.info("添加BE成功")
            else:
                Logger.info("BE已经添加,无需重复添加")
        self.node_check(env)

    def install(self, env):
        import params
        env.set_params(params)

        # 安装前清空配置元数据
        Execute(format('rm -rf {meta_dir}'))
        Execute(format('rm -rf /usr/hdp/3.1.5.0-152/doris'))

        install_package_name = "apache-doris.tar.gz"

        # 下载Doris安装包
        download_cmd = 'grep -q "avx2" /proc/cpuinfo && wget {0} -O {2} || wget {1} -O {2}'.format(params.doris_download, params.doris_noavx2_download, install_package_name)
        Logger.info("Download cmd is : "+download_cmd)
        Execute(download_cmd)

        # 将安装包解压到指定目录
        Execute('tar -zxvf {0} -C /usr/hdp/3.1.5.0-152/'.format(install_package_name))
        # 安装包重命名
        Execute('mv /usr/hdp/3.1.5.0-152/apache-doris-{0}-bin-x64* /usr/hdp/3.1.5.0-152/doris'.format(params.doris_version))

        # 删除下载的安装包
        Execute('rm -rf {0}'.format(install_package_name))

        # 初始化环境变量
        cmd = format("cd {doris_scripts_dir}; chmod +x ./changeOsConf.sh && sh ./changeOsConf.sh")
        Execute(cmd)

        # 创建日志目录
        Execute(format('mkdir -p {LOG_DIR} && chown -R {doris_user}:{user_group} {LOG_DIR}'))

        # 将服务目录权限设置为doris
        Execute(format('chown -R {doris_user}:{user_group} {doris_base_dir}'))

        # 设置 pid 目录权限
        Execute(format('mkdir -p {doris_pid_dir} && chown -R {doris_user}:{user_group} {doris_pid_dir}'))


        Logger.info("Install complete")

    def configure(self, env):
        # Import properties defined in -config.xml file from the params class
        import params

        # This allows us to access the params.elastic_pid_file property as
        # format('{elastic_pid_file}')
        env.set_params(params)

        # 初始化配置文件 ， 配置文件中参数取值读取的是params.py里的变量，不是直接读取的fe.xml变量名
        File(format("{doris_fe_conf_base_dir}/fe.conf"),
             owner=params.doris_user,
             group=params.user_group,
             content=Template('fe.conf.j2')
             )


        # mkdir {meta_dir}
        meta_dir = format("{meta_dir}")
        Directory(meta_dir,
                      mode=0755,
                      cd_access='a',
                      owner=params.doris_user,
                      group=params.user_group,
                      create_parents=True
                      )
        cmd = "chown -R {0}:{1} {2}".format(params.doris_user, params.user_group, meta_dir)
        Execute(cmd)

        Logger.info("Configuration complete")

    def start(self, env):
        import params
        env.set_params(params)
        # Configure Elasticsearch
        self.configure(env)
        # 创建日志目录
        Execute(format('mkdir -p {LOG_DIR} && chown -R {doris_user}:{user_group} {LOG_DIR}'))

        # Start Elasticsearch
        cmd = format("{doris_base_dir}/fe/bin/start_fe.sh --daemon")
        Execute(cmd, user=params.doris_user)

        # 获取Doris进程ID写入到文件
        Execute(
            'ps -ef | grep org.apache.doris.DorisFE | grep -v grep | awk \'{print $2}\' > ' + params.doris_fe_pid_file,
            user=params.doris_user)

        # 等待十秒，fe完全启动成功后，再返回成功
        sleep(30)

    def stop(self, env):
        import params
        env.set_params(params)
        # Kill掉 FE进程
        Execute('ps -ef | grep org.apache.doris.DorisFE | grep -v grep | awk \'{print $2}\' | xargs kill -9',
                user=params.doris_user,
                ignore_failures=True)

        # 删除pid文件
        File([params.doris_fe_pid_file],
             action="delete")

        Logger.info("Stop complete!")

    def status(self, env):
        # Import properties defined in -env.xml file from the status_params class
        import status_params

        # This allows us to access the params.elastic_pid_file property as
        #  format('{elastic_pid_file}')
        env.set_params(status_params)

        # Use built-in method to check status using pidfile
        # 检查进程ID在不在
        check_process_status(status_params.doris_fe_pid_file)
        Logger.info("Check FE process status complete!")

    def restart(self, env):
        self.stop(env)
        self.start(env)


if __name__ == "__main__":
    Fe().execute()
