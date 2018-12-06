import subprocess
from maas.client import login


class MaaS(object):

    def __init__(self, conf):
        conf = self._read_conf(conf)
        self.client = login(conf.api,
                            username=conf.username,
                            password=conf.password)

    def _read_conf(self, conf):
        return MaaSConfig(conf)

    def create_node(self, mode="kvm", memory=1024, disk=20):
        statement = "Create a {} node with memory {} MB and disk size {} G"
        print(statement.format(mode, memory, disk))

    def create_nodes(self, mode="kvm", pool="cluster"):
        print("Create {} {}".format(mode, pool))

    def set_power_type_workaround(self,
                                  system_id,
                                  power_type="virsh",
                                  virsh_url="",
                                  virsh_passwd="",
                                  virsh_node=""):
        shell_cmd = ["/usr/bin/maas", "ubuntu", "machine", "update", system_id,
                     "power_type={}".format(power_type),
                     "power_parameters_power_address={}".format(virsh_url),
                     "power_parameters_power_pass={}".format(virsh_passwd),
                     "power_parameters_power_id={}".format(virsh_node)]
        print(shell_cmd)
        process = subprocess.run(shell_cmd)

        return process


class MaaSConfig(object):

    def __init__(self, conf):
        self.conf = conf

    @property
    def api(self):
        return self.conf['api']

    @property
    def username(self):
        return self.conf['username']

    @property
    def password(self):
        return self.conf['password']
