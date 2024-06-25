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
Logger.info("sync info : ")
Logger.info(stack_root)

if 'fe' in config['configurations']:
    doris_properties_map = config['configurations']['fe']
else:
    doris_properties_map = {}

if 'fe' in config['configurations']:
    doris_be_properties_map = config['configurations']['be']
else:
    doris_be_properties_map = {}

enable_test=True
# current node hostname
hostname = config['agentLevelParams']['hostname']
ambari_server_host = config['ambariLevelParams']['ambari_server_host']
# all fe node
fe_hosts = config['clusterHostInfo']['frontend_hosts']
# all be node
be_hosts = config['clusterHostInfo']['backend_hosts']
# All FE Observer
frontend_observer_hosts = default('/clusterHostInfo/frontend_observer_hosts',[])
frontend_follower_hosts = default('/clusterHostInfo/frontend_follower_hosts',[])
# Coordinator First Host
coordinator_host = config['clusterHostInfo']['coordinator_hosts'][0]


elasticsearch_service_host = default("/clusterHostInfo/elasticsearch_service_hosts", ['localhost'])[0]
presto_user = config['configurations']['presto-env']['presto_user']
user_group = config['configurations']['cluster-env']['user_group']
# --------------------------------------------------------
all_hosts = config['clusterHostInfo']['all_hosts']
all_ipv4 = config['clusterHostInfo']['all_ipv4_ips']
if len(all_hosts) != len(all_ipv4):
    print("The number of hosts and IPv4 addresses must be the same.")
hostname_to_ipv4 = dict(zip(all_hosts, all_ipv4))
# --------------------------------------------------------

version = default("/commandParams/version", "3.1.5.0-152")
Logger.info(version)


# doris service root directory
presto_dir_name = 'presto'
presto_base_dir = os.path.join(stack_root, version, presto_dir_name)
node_environment = config['configurations']['common']['node.environment']
node_data_dir = config['configurations']['common']['node.data-dir']
log_data_dir = node_data_dir + '/log'
log_config = config['configurations']['common']['log_config']
hive_connector = config['configurations']['common']['hive_connector']
elastic_head_base_dir = os.path.join(stack_root, version, 'elasticsearch-head')


elastic_head_site = elastic_head_base_dir + '/_site'

# configuration
CUR_DATE=config['configurations']['fe']['CUR_DATE']
meta_dir=config['configurations']['fe']['meta_dir']
LOG_DIR=config['configurations']['fe']['LOG_DIR']
JAVA_OPTS=config['configurations']['fe']['JAVA_OPTS']
JAVA_OPTS_FOR_JDK_9=config['configurations']['fe']['JAVA_OPTS_FOR_JDK_9']
sys_log_level=config['configurations']['fe']['sys_log_level']
sys_log_mode=config['configurations']['fe']['sys_log_mode']
http_port=config['configurations']['fe']['http_port']
rpc_port=config['configurations']['fe']['rpc_port']
query_port=config['configurations']['fe']['query_port']
edit_log_port=config['configurations']['fe']['edit_log_port']
be_heartbeat_service_port=config['configurations']['be']['heartbeat_service_port']
fe_user=config['configurations']['doris-env']['fe_user']
fe_password = default('/configurations/doris-env/fe_password', '')
sys_log_dir=config['configurations']['be']['sys_log_dir']
be_priority_networks=config['configurations']['be']['priority_networks']
fe_priority_networks=config['configurations']['fe']['priority_networks']
PPROF_TMPDIR=config['configurations']['be']['PPROF_TMPDIR']

config_properties = config['configurations']['coordinator']['config']
#elastic_log_dir = config['configurations']['elastic-env']['elastic_log_dir'].rstrip("/")
presto_pid_dir = config['configurations']['presto-env']['presto_pid_dir'].rstrip("/")
#elastic_head_pid_dir = config['configurations']['elastic-env']['elastic_head_pid_dir'].rstrip("/")
presto_pid_file = format("{presto_pid_dir}/presto.pid")

#elastic_head_pid_file = format("{elastic_head_pid_dir}/elasticsearch-head.pid")

service_packagedir = os.path.realpath(__file__).split('/scripts')[0]
# execute scripts directory
doris_scripts_dir = os.path.join(service_packagedir, "scripts")

#es_log_file = os.path.join(elastic_log_dir, 'elasticsearch-start.log')

# ambari_server_hostname = config['ambariLevelParams']['ambari_server_host']
# download_path = '`cat /etc/yum.repos.d/xxx.repo | grep "baseurl" | awk -F \'=\' \'{print $2}\'`'
# metrics_collector_host = default("/clusterHostInfo/metrics_collector_hosts", ['localhost'])[0]
metrics_collector_host = default("/clusterHostInfo/metrics_collector_hosts", ['localhost'])[0]

presto_version = "0.287"
presto_download = os.path.join('http://', ambari_server_host, 'ambari-extend/centos7/presto/presto-server-{0}.tar.gz'.format(presto_version))
#elastic_head_download = os.path.join('http://', ambari_server_host, 'es/elasticsearch-head.tar.gz')
# nodejs_download = os.path.join('http://', ambari_server_host, 'es/node-v10.13.0-linux-x64.tar.gz')

jvm_config = config['configurations']['common']['jvm_config']

#cluster_name = config['configurations']['elastic-config']['cluster_name']
#node_attr_rack = config['configurations']['elastic-config']['node_attr_rack']
#path_data = config['configurations']['elastic-config']['path_data'].strip(",")
doris_fe_conf = config['configurations']['fe']['content']

#bootstrap_memory_lock = str(config['configurations']['elastic-config']['bootstrap_memory_lock'])
#bootstrap_system_call_filter = str(config['configurations']['elastic-config']['bootstrap_system_call_filter'])

# Elasticsearch expetcs that boolean values to be true or false and will generate an error if you use True or False.
#if bootstrap_memory_lock == 'True':
#    bootstrap_memory_lock = 'true'
#else:
#    bootstrap_memory_lock = 'false'

#if bootstrap_system_call_filter == 'True':
#    bootstrap_system_call_filter = 'true'
#else:
#    bootstrap_system_call_filter = 'false'

# network_host = config['configurations']['elastic-config']['network_host']
# elasticsearch_port = config['configurations']['elastic-config']['elasticsearch_port']
# elasticsearch_head_port = config['configurations']['elastic-config']['elasticsearch_head_port']
# metrics_collector_port = config['configurations']['ams-site']['timeline.metrics.service.webapp.address'].split(":")[1]
metrics_collector_port = default("configurations/ams-site/timeline.metrics.service.webapp.address", "0.0.0.0:6188").split(":")[1]
# metrics_collector_pid_path = config['configurations']['ams-env']['metrics_collector_pid_dir']
# metrics_collector_pid_file = os.path.join(metrics_collector_pid_path, "ambari-metrics-collector.pid")
# http_cors_enabled = config['configurations']['elastic-config']['http_cors_enabled']

# discovery_zen_ping_unicast_hosts = config['clusterHostInfo']['all_hosts']
frontend_hosts = config['clusterHostInfo']['frontend_hosts']
coordinator_hosts = config['clusterHostInfo']['coordinator_hosts']
worker_hosts = config['clusterHostInfo']['worker_hosts']
# Need to parse the comma separated hostnames to create the proper string format within the configuration file
# Elasticsearch expects the format ["host1","host2"]
discovery_zen_ping_unicast_hosts = '[' + ','.join('"' + x + '"' for x in frontend_hosts) + ']'

discovery_zen_minimum_master_nodes = len(frontend_hosts) / 2 + 1

# gateway_recover_after_nodes = config['configurations']['elastic-config']['gateway_recover_after_nodes']
# node_max_local_storage_nodes = config['configurations']['elastic-config']['node_max_local_storage_nodes']

# action_destructive_requires_name = str(config['configurations']['elastic-config']['action_destructive_requires_name'])

# Elasticsearch expecgts boolean values to be true or false and will generate an error if you use True or False.
# if action_destructive_requires_name == 'True':
#     action_destructive_requires_name = 'true'
# else:
#     action_destructive_requires_name = 'false'

# head requires
# http_cors_enabled = config['configurations']['elastic-config']['http_cors_enabled']
# http_cors_allow_origin = config['configurations']['elastic-config']['http_cors_allow_origin']
#
# if http_cors_enabled:
#     http_cors_enabled = 'true'
# else:
#     http_cors_enabled = 'false'

# xpack_security_enabled = str(config['configurations']['elastic-config']['xpack_security_enabled'])

# Elasticsearch expects boolean values to be true or false and will generate an error if you use True or False.
# if xpack_security_enabled == 'True':
#     xpack_security_enabled = 'true'
# else:
#     xpack_security_enabled = 'false'

# ping_timeout_default = config['configurations']['elastic-config']['ping_timeout_default']
# discovery_zen_ping_timeout = config['configurations']['elastic-config']['discovery_zen_ping_timeout']
# zookeeper_session_timeout = config['configurations']['elastic-config']['zookeeper.session.timeout']

# list >>> str
# config_str = ",".join(config)
# Logger.info(config_str)
# clusterHostInfo_str = str(config['clusterHostInfo'])
# Logger.info(clusterHostInfo_str)
# configurations_str = str(config['configurations'])
# roleCommand_str = str(config['roleCommand'])
# commandParams_str = str(config['commandParams'])
# Logger.info(configurations_str)
# Logger.info("----")
# Logger.info(roleCommand_str)
# Logger.info("----")
# Logger.info(commandParams_str)
# Logger.info("zookeeper_session_timeout:")
# Logger.info(zookeeper_session_timeout)

if 'hive-connector' in config['configurations']:
    hive_connector_properties_map = config['configurations']['hive-connector']
else:
    hive_connector_properties_map = {}

