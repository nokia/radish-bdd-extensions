# © 2019 Nokia

# Licensed under the BSD 3 Clause license
# SPDX-License-Identifier: BSD-3-Clause

import os

from setuptools import setup, find_packages

pkg_name = 'radish_selenium'

def _packages():
    packages = [f'{pkg_name}.{sub_pkg_name}' for sub_pkg_name in
                find_packages(os.path.join(os.path.dirname(__file__), pkg_name))
                ]
    packages.append('radish_selenium')
    return packages


setup(name=pkg_name,
      version='0.1',
      description='radish bdd ui extension',
      url='https://github.com/',
      author='Bartosz Bielicki, Dariusz Duleba',
      author_email='dariusz.duleba@nokia.com',
      packages=_packages(),
      package_data={},
      include_package_data=True,
      install_requires=['selenium',
                        'page_objects',
                        'radish-ext',
                        'retry',
                        'testcontainers',
                        ],
      zip_safe=False,
      license='BSD 3-Clause License'
      )
