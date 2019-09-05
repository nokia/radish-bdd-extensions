# © 2019 Nokia

# Licensed under the BSD 3 Clause license
# SPDX-License-Identifier: BSD-3-Clause
from radish_ext.radish.template_with_nested_data_replacer import TemplateForNestedDict
from radish_ext.sdk.l import Logging


class TestDataBase(object):

    def __init__(self, cfg) -> None:
        super().__init__()
        self.data = {'cfg': cfg}
        self.log = Logging.get_object_logger(self)

    def replace_test_data(self, template, **kwargs):
        data = TemplateForNestedDict(template).safe_substitute(**self.data, **kwargs)
        return data