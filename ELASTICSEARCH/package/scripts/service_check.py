from resource_management import *
from elastic_common import kill_process
from time import sleep
from resource_management.core.logger import Logger


class service_check(Script):
    def service_check(self, env):
        import params
        env.set_params(params)
        Logger.info("******** check elasticsearch process ********")
        sleep(15)
        # cmd = format('cat {elastic_pid_dir}/elasticsearch.pid')
        cmd = format('curl {elasticsearch_service_host}:{elasticsearch_port}')
        Execute(cmd, user=params.elastic_user)
        Logger.info("check successfully!")


if __name__ == "__main__":
    service_check().execute()
