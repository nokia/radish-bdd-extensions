# © 2019 Nokia
#
# Licensed under the BSD 3 Clause license
# SPDX-License-Identifier: BSD-3-Clause
#

import logging.config
import os


def get_radish_ext_dir():
    return os.path.abspath(os.path.dirname(__file__))


def get_radish_ext_etc_dir():
    return os.path.join(get_radish_ext_dir(), 'etc')


log_conf = 'll.conf'
if os.path.exists(log_conf):
    log_config_path = log_conf
else:
    config_dir = get_radish_ext_etc_dir()
    log_config_path = os.path.join(config_dir, log_conf)
logging.config.fileConfig(log_config_path)
