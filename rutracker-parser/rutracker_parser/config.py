from configparser import ConfigParser
import os.path


class ConfigWorker(object):
    def __init__(self):
        self.config = ConfigParser()
        self.path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files\\config.ini')
        self.config.read(self.path)

    def get_ini_option(self, section, option):
        return self.config.get(section, option)

    def get_ini_dict(self, section):
        return dict(self.config[section])