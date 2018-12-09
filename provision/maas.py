import os
import subprocess
import uuid
import libvirt
import xml.etree.ElementTree as ET
from maas.client import login
from provision import get_provision_pkg_dir


class MaaS(object):

    DATA_ROOT = os.path.join(get_provision_pkg_dir(), 'data')
    KVM_XML_TEMPLATE_PATH = os.path.join(DATA_ROOT, 'kvm-template.xml')
    KVM_POOL_XML_PATH = os.path.join(DATA_ROOT, 'kvm-pool.xml')
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

        self.pool = None

    def _read_conf(self, conf):
        return MaaSConfig(conf)

    def _read_kvm_xml_template(self, file_path):
        return ET.parse(file_path)

    def _create_pool(self, conn,
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

        self.pool = conn.storagePoolDefineXML(xml_string_pool)
        self.pool.setAutostart(1)
        self.pool.create()

    def _create_volume(self,
                       name='volume.img',
                       capacity=20,
                       path='/home/ubuntu/mpg-pool/volume.img'):
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

    def create_node(self, mode="kvm", memory=1024, disk=20):
        statement = "Create a {} node with memory {} MB and disk size {} G"
        print(statement.format(mode, memory, disk))

        conn = libvirt.open(self.conf.qemu)
        if conn == None:
            print("CRITICAL: Failed to connect to the hypervizor")

        self._create_pool(conn)
        self._create_volume()

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
