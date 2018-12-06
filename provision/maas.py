import os
import subprocess
import libvirt
import xml.etree.ElementTree as ET
from maas.client import login
from provision import get_provision_pkg_dir


class MaaS(object):

    KVM_XML_TEMPLATE_PATH = os.path.join(get_provision_pkg_dir(),
                                         'data',
                                         'kvm-template.xml')

    def __init__(self, conf):
        self.conf = self._read_conf(conf)
        # kvm xml template tree root
        self.ktree = self._read_kvm_xml_template()
        self.ktree_root = self.ktree.getroot()
        self.client = login(self.conf.api,
                            username=self.conf.username,
                            password=self.conf.password)

    def _read_conf(self, conf):
        return MaaSConfig(conf)

    def _read_kvm_xml_template(self):
        return ET.parse(MaaS.KVM_XML_TEMPLATE_PATH)

    def create_node(self, mode="kvm", memory=1024, disk=20):
        statement = "Create a {} node with memory {} MB and disk size {} G"
        print(statement.format(mode, memory, disk))

        conn = libvirt.open(self.conf.qemu)
        if conn == None:
            print("CRITICAL: Failed to connect to the hypervizor")

        xml_string = ET.tostring(self.ktree_root,
                                 encoding='unicode',
                                 method='xml')
        instance = conn.defineXML(xml_string)
        if instance == None:
            print("CRITICAL: Failed to define the instance")

        instances = conn.listDefinedDomains()
        print('Defined instances: {}'.format(instances))

        instance.create()
        print("Creating a domain instance.")
        print("Created a domain instance.")

        print("Try to get the ethernet IP of the guest os")

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

    @property
    def qemu(self):
        return self.conf['qemu']
