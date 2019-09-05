# © 2019 Nokia

# Licensed under the BSD 3 Clause license
# SPDX-License-Identifier: BSD-3-Clause
from radish_ext.radish.base_test_data import TestDataBase


class RequestTestData(TestDataBase):
    def __init__(self, cfg):
        super(RequestTestData, self).__init__(cfg)
        self.response = {}
        self.body = {}

    def get_request_response(self, request_name):
        return self.response.get(request_name)

    def set_request_response(self, request_name, response):
        self.response[request_name] = response

    def get_body(self, body_name):
        return self.body[body_name]

    def set_body(self, body_name, body):
        self.body[body_name] = body

    def replace_test_data(self, template):
        return super().replace_test_data(template, body=self.body)
