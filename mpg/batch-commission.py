#!/usr/bin/env python3
import subprocess
from maas.client import login
DEFAULT_API = "http://10.101.49.75/MAAS/"
DEFAULT_QEMU = "qemu+ssh://ubuntu@10.101.49.75/system"
DEFAULT_UNAME = "ubuntu"
DEFAULT_PASSWD = "insecure"

client = login(DEFAULT_API, username=DEFAULT_UNAME, password=DEFAULT_PASSWD)

def set_power_type_workaround(system_id,
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
    cprocess = subprocess.run(shell_cmd)

    return cprocess

for machine in client.machines.list():
    if machine.status_name == "New":
        print(repr(machine))
        machine_sid = machine.system_id
        machine_hname = machine.hostname
        set_power_type_workaround(machine_sid,
                                  virsh_url=DEFAULT_QEMU,
                                  virsh_passwd=DEFAULT_PASSWD,
                                  virsh_node=machine_hname)
        machine.commission()
        print("Commissioning {}".format(machine_hname))

