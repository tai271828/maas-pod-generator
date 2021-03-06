import os
import subprocess
import uuid
import libvirt
import time
import xml.etree.ElementTree as ET
from maas.client import login
from maas.client.enum import LinkMode
from provision import get_provision_pkg_dir


class MaaS(object):

    DATA_ROOT = os.path.join(get_provision_pkg_dir(), 'data')
    KVM_XML_TEMPLATE_PATH = os.path.join(DATA_ROOT, 'kvm-domain-template.xml')
    KVM_POOL_XML_PATH = os.path.join(DATA_ROOT, 'kvm-pool-template.xml')
    KVM_VOL_XML_TEMP_PATH = os.path.join(DATA_ROOT,
                                         'kvm-volume-template.xml')

    def __init__(self, conf):
        self.conf = self._read_conf(conf)
        # kvm xml template tree root
        self.ktree = self._read_kvm_xml_template(MaaS.KVM_XML_TEMPLATE_PATH)
        self.ktree_root = self.ktree.getroot()
        self.kptree = self._read_kvm_xml_template(MaaS.KVM_POOL_XML_PATH)
        self.kptree_root = self.kptree.getroot()
        self.kvtree = self._read_kvm_xml_template(MaaS.KVM_VOL_XML_TEMP_PATH)
        self.kvtree_root = self.kvtree.getroot()
        self.client = login(self.conf.api,
                            username=self.conf.username,
                            password=self.conf.password)

        conn = libvirt.open(self.conf.qemu)
        if conn is None:
            print("CRITICAL: Failed to connect to the hypervizor")

        self.conn = conn
        self.pool = None
        self.mac_suffix = 0

    def _read_conf(self, conf):
        return MaaSConfig(conf)

    def _read_kvm_xml_template(self, file_path):
        return ET.parse(file_path)

    def create_pool(self,
                    uuid_string=None,
                    name='mpg-volume-pool',
                    path='/home/ubuntu/mpg-pool'):
        if not uuid_string:
            uuid_string = str(uuid.uuid4())
        tree_uuid = self.kptree.find('uuid')
        tree_uuid.text = uuid_string

        tree_name = self.kptree.find('name')
        tree_name.text = name
        tree_target = self.kptree.find('target')
        tree_target_path = tree_target.find('path')
        tree_target_path.text = path

        xml_string_pool = ET.tostring(self.kptree_root,
                                      encoding='unicode',
                                      method='xml')

        self.pool = self.conn.storagePoolDefineXML(xml_string_pool)
        self.pool.setAutostart(1)
        self.pool.create()

    def _create_volume(self,
                       name='volume.img',
                       capacity=20,
                       path='/home/ubuntu/mpg-pool/'):
        path = path + name

        tree_name = self.kvtree.find('name')
        tree_name.text = name
        tree_target = self.kvtree.find('target')
        tree_target_path = tree_target.find('path')
        tree_target_path.text = path
        tree_capacity = self.kvtree.find('capacity')
        tree_capacity.text = str(capacity)

        xml_string_volume = ET.tostring(self.kvtree_root,
                                        encoding='unicode',
                                        method='xml')

        self.pool.createXML(xml_string_volume, 0)

    def create_node(self,
                    mode="kvm",
                    uuid_string=None, mac_address=None,
                    domain_name="mpg-kvm-prototype",
                    disk_source_dir="/home/ubuntu/mpg-pool/",
                    memory=2097152, disk=20):
        statement = "Create a {} node with memory {} MB and disk size {} G"
        print(statement.format(mode, memory, disk))

        self._create_volume(name=domain_name + '.img', capacity=disk)

        if not uuid_string:
            uuid_string = str(uuid.uuid4())
        tree_uuid = self.ktree.find('uuid')
        tree_uuid.text = uuid_string

        if 'ram' in self.conf.pods[domain_name]:
            memory = self.conf.pods[domain_name]['ram']
        tree_memory = self.ktree.find('memory')
        tree_memory.text = str(memory)
        tree_current_memory = self.ktree.find('currentMemory')
        tree_current_memory.text = str(memory)

        if not mac_address:
            fake_mac_template = "ee:dd:dd:dd:dd:{:02x}"
            # use pop so the mac would never duplicate
            fake_mac = fake_mac_template.format(self.mac_suffix.pop())
            mac_address = fake_mac
        tree_devices = self.ktree.find('devices')
        tree_devices_interface = tree_devices.find('interface')
        tree_devices_interface_mac = tree_devices_interface.find('mac')
        tree_devices_interface_mac.attrib['address'] = mac_address
        print(mac_address)

        tree_devices_disk = tree_devices.find('disk')
        tree_devices_disk_source = tree_devices_disk.find('source')
        disk_source = os.path.join(disk_source_dir, domain_name + '.img')
        tree_devices_disk_source.attrib['file'] = disk_source

        tree_name = self.ktree.find('name')
        tree_name.text = domain_name

        xml_string = ET.tostring(self.ktree_root,
                                 encoding='unicode',
                                 method='xml')

        instance = self.conn.defineXML(xml_string)
        if instance is None:
            print("CRITICAL: Failed to define the instance")

        instances = self.conn.listDefinedDomains()
        print('Defined instances: {}'.format(instances))

        # we delegate the task to MaaS POD
        # instance.create()
        # print("Creating a domain instance.")
        # print("Created a domain instance.")

    def create_nodes(self, mode="kvm", pool="cluster"):
        print("Create {} {}".format(mode, pool))
        self.mac_suffix = list(range(1, len(self.conf.pods.keys()) + 1))
        for node_name in self.conf.pods:
            node = self.conf.pods[node_name]
            node_kwargs = {'domain_name': node_name}
            if 'ram' in node:
                node_kwargs['memory'] = node['ram']
            if 'disk' in node:
                node_kwargs['disk'] = node['disk']
            self.create_node(**node_kwargs)

    def create_pod(self,
                   pod_name='mpg-pod',
                   pod_type='virsh'):
        power_address = self.conf.qemu
        power_pass = self.conf.password
        shell_cmd = ["/usr/bin/maas", "humble", "pods", "create"]
        shell_cmd_args = ["type={}".format(pod_type),
                          "name={}".format(pod_name),
                          "power_address={}".format(power_address),
                          "power_pass={}".format(power_pass)]
        shell_cmd.extend(shell_cmd_args)
        print(shell_cmd)
        process = subprocess.run(shell_cmd)

        return process

    def deploy_node(self, node_name, distro):
        for machine in self.client.machines.list():
            if machine.hostname == node_name:
                print('Node {} is specified to deploy {}'.format(node_name,
                                                                 distro))
                machine.deploy(distro_series=distro)

    def deploy_nodes(self):
        # deploy the node if the field "distro" is present
        for node_name in self.conf.pods:
            node = self.conf.pods[node_name]
            if 'distro' in node:
                self.deploy_node(node_name, node['distro'])

    def _fetch_machines(self):
        mpg_machines = []
        for machine in self.client.machines.list():
            if 'mpg-' in machine.hostname:
                mpg_machines.append(machine)

        assert len(mpg_machines) > 0

        return mpg_machines

    def update_interface(self, link_type='dhcp'):
        mpg_machines_ready = []
        timeout_cnt = 0
        mpg_machines = self._fetch_machines()
        while len(mpg_machines_ready) != len(mpg_machines):
            time.sleep(10)
            mpg_machines = self._fetch_machines()
            for mpg_machine in mpg_machines:
                if mpg_machine.status.name == 'READY':
                    mpg_machines_ready.append(mpg_machine)
            if len(mpg_machines_ready) != len(mpg_machines):
                mpg_machines_ready = []
            if timeout_cnt > 30:
                return
            timeout_cnt += 1

        for mpg_machine in mpg_machines_ready:
            ml = mpg_machine.interfaces[0].links
            if link_type == 'dhcp':
                ml.create(LinkMode.DHCP)
                ml[0].delete()

    def set_power_type(self,
                       system_id,
                       power_type="virsh",
                       virsh_url="",
                       virsh_passwd="",
                       virsh_node=""):
        return self.set_power_type_workaround(system_id,
                                              power_type,
                                              virsh_url,
                                              virsh_passwd,
                                              virsh_node)

    @staticmethod
    def set_power_type_workaround(system_id,
                                  power_type="virsh",
                                  virsh_url="",
                                  virsh_passwd="",
                                  virsh_node=""):
        # maas-cli python wrapper is not ready to support this
        # feature yet so we have this workaround.
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

    @property
    def pods(self):
        return self.conf['pods']
