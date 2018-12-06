import yaml


class Config:

    def __init__(self):
        """
        Initialize an empty Config object
        """
        self.string = ''
        self.config_yaml = None

    def read(self, filename_list):
        print('TODO: will be implemented later to merge multiple conf files.')
        # as a prototype we use yaml for now
        # maybe we should migrate to launcher conf later
        self.config_yaml = self.read_yaml(self.string)

    def read_string(self, string):
        self.string = string
        print('Reading conf file...')

    def read_yaml(self, stream):
        return yaml.load(stream)

