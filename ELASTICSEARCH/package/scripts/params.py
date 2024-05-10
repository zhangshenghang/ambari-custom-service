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

elastic_user = config['configurations']['elastic-env']['elastic_user']
user_group = config['configurations']['cluster-env']['user_group']

version = default("/commandParams/version", "3.1.5.0-152")
Logger.info(version)

elastic_version = "7.14.2"
elastic_base_dir = os.path.join(stack_root, version, 'elasticsearch')
# Initialize tag file
elastic_password_init_file = elastic_base_dir + '/password_init'

elastic_head_base_dir = os.path.join(stack_root, version, 'elasticsearch-head')
elastic_conf_base_dir = elastic_base_dir + '/config'
elastic_head_site = elastic_head_base_dir + '/_site'

elastic_log_dir = config['configurations']['elastic-env']['elastic_log_dir'].rstrip("/")
elastic_pid_dir = config['configurations']['elastic-env']['elastic_pid_dir'].rstrip("/")
elastic_pid_file = format("{elastic_pid_dir}/elasticsearch.pid")
elastic_jvm_conf = config['configurations']['elastic-jvm']['content']


service_packagedir = os.path.realpath(__file__).split('/scripts')[0]
elastic_scripts_dir = os.path.join(service_packagedir, "scripts")

es_log_file = os.path.join(elastic_log_dir, 'elasticsearch-start.log')

# ambari_server_hostname = config['ambariLevelParams']['ambari_server_host']
# download_path = '`cat /etc/yum.repos.d/xxx.repo | grep "baseurl" | awk -F \'=\' \'{print $2}\'`'
# metrics_collector_host = default("/clusterHostInfo/metrics_collector_hosts", ['localhost'])[0]
metrics_collector_host = default("/clusterHostInfo/metrics_collector_hosts", ['localhost'])[0]
elasticsearch_service_host = default("/clusterHostInfo/elasticsearch_service_hosts", ['localhost'])[0]
elastic_download = os.path.join('http://', ambari_server_host, 'es/elasticsearch-{0}-linux-x86_64.tar.gz'.format(elastic_version) )
elastic_metrics_jar_name = 'ambari-elastic-metrics.jar'
elastic_metrics_download = os.path.join('http://', ambari_server_host, 'es/{0}'.format(elastic_metrics_jar_name))
elastic_cert_download = os.path.join('http://', ambari_server_host, 'es/elastic-certificates.p12')
elastic_password = config['configurations']['elastic-config']['elastic_password']
# Tool File Dir
elastic_tool_dir = elastic_base_dir+'/tool'

# ==================== cerebro file content ====================
cerebro_download = os.path.join('http://', ambari_server_host, 'es/cerebro-0.9.4.tgz')
cerebro_base_dir = os.path.join(stack_root, version, 'cerebro')
cerebro_pid_dir = config['configurations']['cerebro']['pidfile_dir']
cerebro_pid_file = format("{cerebro_pid_dir}/cerebro.pid")
cerebro_log_dir = config['configurations']['cerebro']['cerebro_log_dir'].rstrip("/")
cerebro_conf = config['configurations']['cerebro']['content']
cerebro_port = config['configurations']['cerebro']['cerebro_port']
# ============================================================

# ==================== elastic-config file content ====================
elasticsearch_service_hosts = config['clusterHostInfo']['elasticsearch_service_hosts']
elasticsearch_service_host = elasticsearch_service_hosts[0]
cluster_name = config['configurations']['elastic-config']['cluster_name']
node_attr_rack = config['configurations']['elastic-config']['node_attr_rack']
node_master = config['configurations']['elastic-config']['node_master']
node_data = config['configurations']['elastic-config']['node_data']
node_ingest = config['configurations']['elastic-config']['node_ingest']
path_data = config['configurations']['elastic-config']['path_data'].strip(",")
transport_tcp_compress = config['configurations']['elastic-config']['transport_tcp_compress']
cluster_initial_master_nodes = '[' + ','.join('"' + x + '"' for x in elasticsearch_service_hosts) + ']'
cluster_routing_allocation_same_shard_host = config['configurations']['elastic-config']['cluster_routing_allocation_same_shard_host']
discovery_zen_fd_ping_timeout = config['configurations']['elastic-config']['discovery_zen_fd_ping_timeout']
action_auto_create_index = config['configurations']['elastic-config']['action_auto_create_index']
gateway_recover_after_time = config['configurations']['elastic-config']['gateway_recover_after_time']
gateway_expected_nodes = config['configurations']['elastic-config']['gateway_expected_nodes']
thread_pool_search_size = config['configurations']['elastic-config']['thread_pool_search_size']
thread_pool_search_queue_size = config['configurations']['elastic-config']['thread_pool_search_queue_size']
elasticsearch_tcp_port = config['configurations']['elastic-config']['elasticsearch_tcp_port']
xpack_license_self_generated_type = config['configurations']['elastic-config']['xpack_license_self_generated_type']
xpack_security_transport_ssl_enabled = config['configurations']['elastic-config']['xpack_security_transport_ssl_enabled']
xpack_security_transport_ssl_verification_mode = config['configurations']['elastic-config']['xpack_security_transport_ssl_verification_mode']
xpack_security_transport_ssl_keystore_path = config['configurations']['elastic-config']['xpack_security_transport_ssl_keystore_path']
xpack_security_transport_ssl_truststore_path = config['configurations']['elastic-config']['xpack_security_transport_ssl_truststore_path']
Xmx=config['configurations']['elastic-jvm']['Xmx']
Xms=config['configurations']['elastic-jvm']['Xms']
elasticsearch_yml = config['configurations']['elastic-config']['content']
http_cors_enabled = config['configurations']['elastic-config']['http_cors_enabled']

bootstrap_memory_lock = config['configurations']['elastic-config']['bootstrap_memory_lock']
bootstrap_system_call_filter = config['configurations']['elastic-config']['bootstrap_system_call_filter']

# Elasticsearch expetcs that boolean values to be true or false and will generate an error if you use True or False.
if bootstrap_system_call_filter:
    bootstrap_system_call_filter = 'true'
else:
    bootstrap_system_call_filter = 'false'

if bootstrap_memory_lock:
    bootstrap_memory_lock = 'true'
else:
    bootstrap_memory_lock = 'false'

if node_master:
    node_master = 'true'
else:
    node_master = 'false'

if node_data:
    node_data = 'true'
else:
    node_data = 'false'


if node_ingest:
    node_ingest = 'true'
else:
    node_ingest = 'false'


if transport_tcp_compress:
    transport_tcp_compress = 'true'
else:
    transport_tcp_compress = 'false'

if cluster_routing_allocation_same_shard_host:
    cluster_routing_allocation_same_shard_host = 'true'
else:
    cluster_routing_allocation_same_shard_host = 'false'


if action_auto_create_index:
    action_auto_create_index = 'true'
else:
    action_auto_create_index = 'false'

if http_cors_enabled:
    http_cors_enabled = 'true'
else:
    http_cors_enabled = 'false'

action_destructive_requires_name = str(config['configurations']['elastic-config']['action_destructive_requires_name'])

# Elasticsearch expecgts boolean values to be true or false and will generate an error if you use True or False.
if action_destructive_requires_name:
    action_destructive_requires_name = 'true'
else:
    action_destructive_requires_name = 'false'

xpack_security_enabled = config['configurations']['elastic-config']['xpack_security_enabled']
if xpack_security_enabled:
    xpack_security_enabled = 'true'
else:
    xpack_security_enabled = 'false'

if xpack_security_transport_ssl_enabled:
    xpack_security_transport_ssl_enabled = 'true'
else:
    xpack_security_transport_ssl_enabled = 'false'

network_host = config['configurations']['elastic-config']['network_host']
elasticsearch_port = config['configurations']['elastic-config']['elasticsearch_port']
elasticsearch_head_port = config['configurations']['elastic-config']['elasticsearch_head_port']
# metrics_collector_port = config['configurations']['ams-site']['timeline.metrics.service.webapp.address'].split(":")[1]
metrics_collector_port = default("configurations/ams-site/timeline.metrics.service.webapp.address", "0.0.0.0:6188").split(":")[1]
# metrics_collector_pid_path = config['configurations']['ams-env']['metrics_collector_pid_dir']
# metrics_collector_pid_file = os.path.join(metrics_collector_pid_path, "ambari-metrics-collector.pid")

# discovery_zen_ping_unicast_hosts = config['clusterHostInfo']['all_hosts']


# Need to parse the comma separated hostnames to create the proper string format within the configuration file
# Elasticsearch expects the format ["host1","host2"]
discovery_zen_ping_unicast_hosts = '[' + ','.join('"' + x + '"' for x in elasticsearch_service_hosts) + ']'

discovery_zen_minimum_master_nodes = len(elasticsearch_service_hosts) / 2 + 1

gateway_recover_after_nodes = config['configurations']['elastic-config']['gateway_recover_after_nodes']
node_max_local_storage_nodes = config['configurations']['elastic-config']['node_max_local_storage_nodes']



# head requires
# http_cors_enabled = config['configurations']['elastic-config']['http_cors_enabled']
http_cors_allow_origin = config['configurations']['elastic-config']['http_cors_allow_origin']





# Elasticsearch expects boolean values to be true or false and will generate an error if you use True or False.
# if xpack_security_enabled == 'True':
#     xpack_security_enabled = 'true'
# else:
#     xpack_security_enabled = 'false'

discovery_zen_ping_timeout = config['configurations']['elastic-config']['discovery_zen_ping_timeout']
zookeeper_session_timeout = config['configurations']['elastic-config']['zookeeper.session.timeout']

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


# ==================== kibana ====================
kibana_base_dir = os.path.join(stack_root, version, 'kibana')
kibana_conf_base_dir = kibana_base_dir + '/config'
kibana_download = os.path.join('http://', ambari_server_host, 'es/kibana-{0}-linux-x86_64.tar.gz'.format(elastic_version) )
kibana_log_dir = config['configurations']['kibana']['kibana_log_dir'].rstrip("/")
kibana_pid_dir = config['configurations']['kibana']['kibana_pid_dir'].rstrip("/")
kibana_pid_file = format("{kibana_pid_dir}/kibana.pid")
kibana_conf = config['configurations']['kibana']['content']
elastic_url_list = '[' + ','.join('"http://' + x + ':{0}"'.format(elasticsearch_port) for x in elasticsearch_service_hosts) + ']'
kibana_web_ui_port = config['configurations']['kibana']['kibana_web_ui_port']

# ============================================================