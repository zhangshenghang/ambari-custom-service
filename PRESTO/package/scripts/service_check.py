from resource_management import *
from time import sleep
from resource_management.core.logger import Logger


class service_check(Script):
    def service_check(self, env):
        import params
        env.set_params(params)
        Logger.info("run service_check")
        sleep(2)
        Logger.info("check successfully!")



if __name__ == "__main__":
    service_check().execute()
