# © 2019 Nokia

# Licensed under the BSD 3 Clause license
# SPDX-License-Identifier: BSD-3-Clause

from radish_ext.radish.base_test_data import TestDataBase


class SeleniumTestData(TestDataBase):
    def __init__(self, cfg):
        super(SeleniumTestData, self).__init__(cfg)
        self.pages = {}

    def set_page(self, page_object_id, page_object):
        self.pages[page_object_id] = page_object

    def get_page(self, page_object_id):
        return self.pages.get(page_object_id)
