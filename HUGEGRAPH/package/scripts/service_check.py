from resource_management import *
from resource_management.core.logger import Logger


class service_check(Script):
    def service_check(self, env):
        import params
        env.set_params(params)
        Logger.info("******** check hugegraph process ********")
        cmd = format('curl {hostname}:{restserver_port}')
        Execute(cmd, user=params.hugegraph_user)
        Logger.info("check successfully!")


if __name__ == "__main__":
    service_check().execute()
