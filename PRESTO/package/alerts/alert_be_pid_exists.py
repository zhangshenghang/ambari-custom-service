#!/usr/bin/env python
# -*- coding: utf-8 -*--

from resource_management import *
import os
import socket
from resource_management.core.logger import Logger

def execute(configurations={}, parameters={}, host_name=None):
    config = Script.get_config()
    doris_pid_dir = config['configurations']['doris-env']['doris_pid_dir'].rstrip("/")
    doris_pid_file = format("{doris_pid_dir}/doris-be.pid")

    result = os.path.exists(doris_pid_file)
    if result:
        result_code = 'OK'
        es_head_process_running = True
    else:
        # OK、WARNING、CRITICAL、UNKNOWN、NONE
        result_code = 'CRITICAL'
        es_head_process_running = False

    if host_name is None:
        host_name = socket.getfqdn()

    # 告警时显示的内容Response
    alert_label = 'Doris Backend is running on {0}' if es_head_process_running else 'Doris Backend is NOT running on {0}'
    alert_label = alert_label.format(host_name)

    return ((result_code, [alert_label]))
