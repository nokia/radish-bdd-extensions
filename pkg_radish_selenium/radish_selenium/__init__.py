# © 2019 Nokia

# Licensed under the BSD 3 Clause license
# SPDX-License-Identifier: BSD-3-Clause

import os


def get_radish_selenium_dir():
    return os.path.abspath(os.path.dirname(__file__))


def get_radish_selenium_etc_dir():
    return os.path.join(get_radish_selenium_dir(), 'etc')


