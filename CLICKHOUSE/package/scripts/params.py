#!/usr/bin/env python

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

from resource_management import *
from resource_management.core.resources import Directory
from resource_management.libraries.functions.default import default
import os
from resource_management.core.logger import Logger
# https://articles.zsxq.com/id_5ondul375fvf.html
# config object that holds the configurations declared in the -config.xml file
config = Script.get_config()
stack_root = Script.get_stack_root()
tmp_dir = Script.get_tmp_dir()
Logger.info(stack_root)

hostname = config['agentLevelParams']['hostname']
ambari_server_host = config['ambariLevelParams']['ambari_server_host']
clickhouse_service_host = config['clusterHostInfo']['clickhouse_service_hosts']
clickhouse_version = '24.3.2.23'
clickhouse_client_download = os.path.join('http://', ambari_server_host, 'ambari-extend/centos7/clickhouse/clickhouse-client-{0}.x86_64.rpm'.format(clickhouse_version))
clickhouse_common_static_download = os.path.join('http://', ambari_server_host, 'ambari-extend/centos7/clickhouse/clickhouse-common-static-{0}.x86_64.rpm'.format(clickhouse_version))
clickhouse_common_static_dbg_download = os.path.join('http://', ambari_server_host, 'ambari-extend/centos7/clickhouse/clickhouse-common-static-dbg-{0}.x86_64.rpm'.format(clickhouse_version))
clickhouse_server_download = os.path.join('http://', ambari_server_host, 'ambari-extend/centos7/clickhouse/clickhouse-server-{0}.x86_64.rpm'.format(clickhouse_version))

clickhouse_config = config['configurations']['config']['content']
users_config = config['configurations']['authentication']['content']
clickhouse_user = config['configurations']['clickhouse-env']['clickhouse_user']
user_group = config['configurations']['cluster-env']['user_group']

listen_host = config['configurations']['config']['listen_host']
http_port = config['configurations']['config']['http_port']
tcp_port = config['configurations']['config']['tcp_port']
mysql_port = config['configurations']['config']['mysql_port']
postgresql_port = config['configurations']['config']['postgresql_port']
interserver_http_port = config['configurations']['config']['interserver_http_port']
max_connections = config['configurations']['config']['max_connections']
auto_remote_servers = config['configurations']['config']['auto_remote_servers']
cluster_name = config['configurations']['config']['cluster_name']
if auto_remote_servers:
    remote_servers = ''
else:
    remote_servers = config['configurations']['config']['remote_servers']

enable_authentication = config['configurations']['authentication']['enable_authentication']
username = config['configurations']['authentication']['username']
password = config['configurations']['authentication']['password']
import hashlib
sha256_password = hashlib.sha256(password.encode()).hexdigest()
path = config['configurations']['config']['clickhouse.path']
clickhouse_error_log = config['configurations']['config']['clickhouse.error.log']
clickhouse_log = config['configurations']['config']['clickhouse.log']
