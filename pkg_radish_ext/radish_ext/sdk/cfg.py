# © 2019 Nokia

# Licensed under the BSD 3 Clause license
# SPDX-License-Identifier: BSD-3-Clause

import os

import jinja2
import yaml

from pkg_radish_ext.radish_ext import get_radish_ext_etc_dir
from pkg_radish_ext.radish_ext.sdk.l import Logging
from radish_ext.sdk.config import Config


class CfgComponentException(Exception):
    pass


class CfgConfig(Config):
    def __init__(self):
        super(CfgConfig, self).__init__()
        self.cfg_dir = get_radish_ext_etc_dir()
        self.yaml = None
        self.j2_config_template = None
        self.default_cfg_dirs = ['.']
        self.custom_cfg_dirs = []

    def set_properties(self, yaml_, j2_config_template, custom_cfg_dirs=None):
        self.yaml = yaml_
        self.j2_config_template = j2_config_template
        if custom_cfg_dirs is not None:
            self.custom_cfg_dirs = self.default_cfg_dirs + custom_cfg_dirs
        else:
            self.custom_cfg_dirs = self.default_cfg_dirs
        return self


class CfgComponent(object):
    CONFIG_FILE_PATH = "__config_file_path__"

    def __init__(self, cfg_config):
        super(CfgComponent, self).__init__()
        self.log = Logging.get_object_logger(self)
        self.config = cfg_config
        if self.config.yaml:
            cfg_dir = self.find_config_directory(self.config.yaml, self.config.custom_cfg_dirs + [self.config.cfg_dir])
            self.log.debug("Using config directory: %s" % cfg_dir)

            with open(os.path.join(cfg_dir, self.config.yaml)) as f:
                cfg = yaml.load(f, Loader=yaml.FullLoader)
            if self.config.j2_config_template is None:
                self.cfg = cfg
            else:
                jinja2_env = jinja2.Environment(loader=jinja2.FileSystemLoader(cfg_dir))
                template = jinja2_env.get_template(self.config.j2_config_template)
                self.cfg = yaml.load(template.render(**cfg))

            self.cfg[CfgComponent.CONFIG_FILE_PATH] = os.path.join(cfg_dir, self.config.yaml)
        else:
            self.cfg = yaml.load("")
            print(dir(self.cfg))

    @staticmethod
    def find_config_directory(file_name, cfg_dirs):
        for i in cfg_dirs:
            if os.path.isfile(os.path.join(i, file_name)):
                cfg_dir = i
                break
        else:
            raise CfgComponentException('Config file %s not found in %s' % (file_name, cfg_dirs))
        return cfg_dir


def cfg_from_file(cfg_yaml_path):
    return CfgComponent(CfgConfig().set_properties(os.path.basename(cfg_yaml_path),
                                                   None,
                                                   [os.path.dirname(cfg_yaml_path)])).cfg
