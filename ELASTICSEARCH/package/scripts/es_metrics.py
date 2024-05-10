#!/usr/bin/env python
# -*- coding: utf-8 -*--

import json
import logging
import os
import sys
import time
import socket
import requests

##############################
# 相关ES监控指标脚本逻辑如下：
# 1、判断ES是否启动，如果服务宕机，则停止向metrcis collector发送指标数据
# 2、通过requests模块，读取ES api接口，解析json，获取需要的指标数据。
# 3、组装请求参数，并向etrcis collector发送POST请求
# 4、过程中，将发送的指标数据打印到日志文件中，方便运维人员排查问题。
# 5、每隔10s向metrics collector发送一系列POST请求。
# 6、以上是一个while循环，循环条件就是判断ES进程是否存在，如果ES进程不存在，则终止循环。
# 7、把该脚本放在生命周期start()方法里面执行。
##############################

# '''
# 需要提供的参数有：
# {
#   "metrics_collector": {
#     "ip": "hdp1.com",
#     "port": "6188"
#   },
#   "es": {
#     "pid_file": "/var/run/elasticsearch/elasticsearch.pid",
#     "ip": "hdp1.com",
#     "port": "9200",
#     "log_dir": "/var/log/elasticsearch"
#   }
# }
# '''

params_data = sys.argv[1]
params_json = json.loads(params_data)
# 解析
# mc_pid_file = params_json['metrics_collector']['pid_file']
mc_ip = params_json['metrics_collector']['ip']
mc_port = params_json['metrics_collector']['port']
es_pid_file = params_json['es']['pid_file']
es_ip = params_json['es']['ip']
es_port = params_json['es']['port']
es_log_dir = params_json['es']['log_dir']

elastic_log_dir = "{0}".format(es_log_dir)
metrics_log_file = "es_metrics.log"
metrics_log = os.path.join(elastic_log_dir, metrics_log_file)
es_cluster_stats_api = "http://{0}:{1}/_cluster/stats".format(es_ip, es_port)
es_cluster_health_api = "http://{0}:{1}/_cluster/health".format(es_ip, es_port)
metrics_collector_api = "http://{0}:{1}/ws/v1/timeline/metrics".format(mc_ip, mc_port)

if not os.path.exists(elastic_log_dir):
    os.makedirs(elastic_log_dir, 0644)

# 输出到console
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)  # 指定被处理的信息级别为最低级DEBUG，低于level级别的信息将被忽略
# 输出到文件
logging.basicConfig(level=logging.INFO,  # 控制台打印的日志级别
                    filename=metrics_log,
                    filemode='a',  ##文件模式，有w和a，w就是写模式，每次都会重新写日志，覆盖之前的日志
                    # a是追加模式，默认如果不写的话，就是追加模式
                    format='%(asctime)s - %(filename)s [line:%(lineno)d] %(levelname)s: %(message)s',  # 日志格式
                    )
logger = logging.getLogger()
logger.addHandler(ch)

logger.info("data type: {0}, params_data: {1}".format(type(params_data), params_data))


# 获取pid进程号
def read_file(pid_file, encoding=None):
    with open(pid_file, "rb") as fp:
        content = fp.read()

    content = content.decode(encoding) if encoding else content
    return content


# 根据pid文件检查进程是否存在
def check_process(pid_file):
    if not pid_file or not os.path.isfile(pid_file):
        logging.error("Pid file {0} is empty or does not exist".format(str(pid_file)))
        return False
    else:
        pid = -1
        try:
            pid = int(read_file(pid_file))
        except RuntimeError:
            logging.error("Pid file {0} does not exist or does not contain a process id number".format(pid_file))

        try:
            # Kill will not actually kill the process
            # From the doc:
            # If sig is 0, then no signal is sent, but error checking is still
            # performed; this can be used to check for the existence of a
            # process ID or process group ID.
            os.kill(pid, 0)
            logging.info("process already exists! ")
            process_is_exist = True
        except OSError:
            logging.error("Process with pid {0} is not running. Stale pid file"
                          " at {1}".format(pid, pid_file))
            process_is_exist = False
        return process_is_exist


# get_api_data
def get_api_data():
    try:
        logging.info("elasticsearch cluster stats api: {0}".format(es_cluster_stats_api))
        stats_resp = requests.get(es_cluster_stats_api)
        stats_content = json.loads(stats_resp.content)
        indices_count = stats_content['indices']['count']
        heap_used_memory = stats_content['nodes']['jvm']['mem']['heap_used_in_bytes']
        heap_max_memory = stats_content['nodes']['jvm']['mem']['heap_max_in_bytes']
        nodes_number = stats_content['_nodes']['successful']
        total_nodes_number = stats_content['_nodes']['total']
        nodes_mem_percent = stats_content['nodes']['os']['mem']['used_percent']
        send_metric_to_collector("indices.count", indices_count)
        send_metric_to_collector("heap.used.memory", heap_used_memory)
        send_metric_to_collector("heap.max.memory", heap_max_memory)
        send_metric_to_collector("nodes.number", nodes_number)
        send_metric_to_collector("nodes.total", total_nodes_number)
        send_metric_to_collector("nodes.mem.percent", nodes_mem_percent)

        logging.info("elasticsearch cluster health api: {0}".format(es_cluster_health_api))
        health_resp = requests.get(es_cluster_health_api)
        health_content = json.loads(health_resp.content)
        unassigned_shards = health_content['unassigned_shards']
        send_metric_to_collector("unassigned.shards", unassigned_shards)
    except Exception as e:
        logging.error(e)


# 发送指标数据到metrics collector
def send_metric_to_collector(metric_name, metric_data):
    appid = "elasticsearch"
    millon_time = int(time.time() * 1000)
    hostname = socket.gethostname()
    header = {
        "Content-Type": "application/json"
    }
    metrics_json = {
        "metrics": [
            {
                "metricname": metric_name,
                "appid": appid,
                "hostname": hostname,
                "timestamp": millon_time,
                "starttime": millon_time,
                "metrics": {
                    millon_time: metric_data
                }
            }
        ]
    }
    logging.info("[{0}] send metrics to collector data: {1}".format(metric_name, metrics_json))
    try:
        resp = requests.post(metrics_collector_api, json=metrics_json, headers=header)
        logging.info("send metrics result: {0}".format(resp.content))
    except Exception as e:
        logging.error("send metrics failure: {0}".format(e))
        pass


# 检测进程并发送
def check_and_send():
    # 当es进程不存在时，循环终止
    while check_process(es_pid_file):
        get_api_data()
        time.sleep(10)


if __name__ == "__main__":
    check_and_send()
