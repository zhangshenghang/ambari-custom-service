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

# config object that holds the configurations declared in the -config.xml file
config = Script.get_config()
stack_root = Script.get_stack_root()
tmp_dir = Script.get_tmp_dir()
Logger.info(stack_root)

hostname = config['agentLevelParams']['hostname']
ambari_server_host = config['ambariLevelParams']['ambari_server_host']

hugegraph_user = config['configurations']['hugegraph-env']['hugegraph_user']
user_group = config['configurations']['cluster-env']['user_group']

version = default("/commandParams/version", "3.1.5.0-152")
Logger.info(version)

hugegraph_version = "1.2.0"
hugegraph_base_dir = os.path.join(stack_root, version, 'hugegraph')
zookeeper_host = config['clusterHostInfo']['zookeeper_server_hosts'][0]
zookeeper_port = config['configurations']['zoo.cfg']['clientPort']
hbase_znode_parent = config['configurations']['hbase-site']['zookeeper.znode.parent']
# Initialize tag file

hugegraph_service_host = config['clusterHostInfo']['hugegraph_service_hosts'][0]
hugegraph_log_dir = config['configurations']['hugegraph-env']['hugegraph_log_dir'].rstrip("/")
hugegraph_pid_dir = config['configurations']['hugegraph-env']['hugegraph_pid_dir'].rstrip("/")
hugegraph_pid_file = format("{hugegraph_pid_dir}/hugegraph.pid")
hugegraph_properties = config['configurations']['hugegraph-config']['content']
gremlin_serer_yaml = config['configurations']['gremlin-server']['content']
rest_server_properties = config['configurations']['rest-server']['content']
gremlin_port = config['configurations']['gremlin-server']['gremlin_port']
restserver_port = config['configurations']['rest-server']['restserver_port']

hugegraph_configs = config['configurations']['hugegraph-config']

# ==================== hubble file content ====================
hubble_base_dir = os.path.join(stack_root, version, 'hugegraph-toolchain/apache-hugegraph-hubble-incubating-1.2.0')
hubble_log_dir = config['configurations']['hugegraph-env']['hubble_log_dir'].rstrip("/")
hubble_pid_dir = config['configurations']['hugegraph-env']['hubble_pid_dir'].rstrip("/")
hubble_pid_file = format("{hubble_pid_dir}/hubble.pid")
hubble_properties = config['configurations']['hugegraph-hubble']['content']
hubble_process_tag = 'org.apache.hugegraph.HugeGraphHubble'
hubble_port = config['configurations']['hugegraph-hubble']['hubble_port']
# =============================================================
service_packagedir = os.path.realpath(__file__).split('/scripts')[0]
elastic_scripts_dir = os.path.join(service_packagedir, "scripts")


# ambari_server_hostname = config['ambariLevelParams']['ambari_server_host']
# download_path = '`cat /etc/yum.repos.d/xxx.repo | grep "baseurl" | awk -F \'=\' \'{print $2}\'`'
# metrics_collector_host = default("/clusterHostInfo/metrics_collector_hosts", ['localhost'])[0]
metrics_collector_host = default("/clusterHostInfo/metrics_collector_hosts", ['localhost'])[0]
elasticsearch_service_host = default("/clusterHostInfo/elasticsearch_service_hosts", ['localhost'])[0]
hugegraph_server_download = os.path.join('http://', ambari_server_host, 'ambari-extend/centos7/hugegraph/apache-hugegraph-incubating-{0}.tar.gz'.format(hugegraph_version) )
hubble_download = os.path.join('http://', ambari_server_host, 'ambari-extend/centos7/hugegraph/apache-hugegraph-toolchain-incubating-{0}.tar.gz'.format(hugegraph_version) )
hugegraph_jdk11_download = os.path.join('http://', ambari_server_host, 'ambari-extend/centos7/hugegraph/jdk-11.0.22_linux-x64_bin.tar.gz' )
keystore_download = os.path.join('http://', ambari_server_host, 'ambari-extend/centos7/hugegraph/hugegraph-server.keystore' )

hugegraph_process_tag = 'org.apache.hugegraph.dist.HugeGraphServer'

# Tool File Dir




