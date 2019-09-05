# © 2019 Nokia

# Licensed under the BSD 3 Clause license
# SPDX-License-Identifier: BSD-3-Clause

from abc import abstractmethod, ABCMeta

from pkg_radish_ext.radish_ext.sdk.l import Logging


class Config(object, metaclass=ABCMeta):
    def __init__(self):
        super(Config, self).__init__()
        self.log = Logging.get_object_logger(self)

    @abstractmethod
    def set_properties(self, *args, **kwargs):
        pass
