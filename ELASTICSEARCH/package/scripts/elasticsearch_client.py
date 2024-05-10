#!/usr/bin/env python
# -*- coding: utf-8 -*--

from resource_management.libraries.script.script import Script
from resource_management.core.logger import Logger
from resource_management.core.resources import Directory
from resource_management import *
from elastic_common import kill_process
from resource_management.core.exceptions import ClientComponentHasNoStatus
from resource_management.core.logger import Logger


# 该client只是一个示例，为了讲解如何实现 “Download Client Configs” 配置文件。无实际逻辑，可自由扩展
class Client(Script):
    def install(self, env):
        Logger.info("Install complete")
        self.configure(env)

    def configure(self, env):
        Logger.info("Configuration complete")

    def status(self, env):
        raise ClientComponentHasNoStatus()


if __name__ == "__main__":
    Client().execute()
