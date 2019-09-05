# © 2019 Nokia

# Licensed under the BSD 3 Clause license
# SPDX-License-Identifier: BSD-3-Clause

import logging


class Logging(object):
    def __init__(self, name=None):
        super(Logging, self).__init__()
        if name is None:
            name = '%s.%s' % (self.__module__, self.__class__.__name__)
        self.log = logging.getLogger(name)

    @staticmethod
    def get_logger(logger_name):
        return Logging(logger_name).log

    @staticmethod
    def get_object_logger(_object):
        return Logging.get_logger('%s.%s' % (_object.__module__, _object.__class__.__name__))
