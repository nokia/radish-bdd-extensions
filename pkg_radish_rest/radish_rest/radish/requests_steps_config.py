# © 2019 Nokia

# Licensed under the BSD 3 Clause license
# SPDX-License-Identifier: BSD-3-Clause

from pkg_radish_ext.radish_ext.radish.step_config import StepConfig
from radish_rest.radish.requests_test_data import RequestTestData
from radish_rest.sdk.rest import RestConfig, RestClient, SimpleRestConfig


class RequestsStepsConfig(StepConfig):
    def __init__(self, context):
        super(RequestsStepsConfig, self).__init__(context)
        self.test_data = RequestTestData(self.cfg)
        self.client = None

    def get_client(self, url):
        if self.client is None:
            rest_config = SimpleRestConfig()
            rest_config.set_properties(url=url)
            self.client = RestClient(rest_config)
        return self.client


def get_requests_config(context):
    """
    Get single config object shared by context for scenario
        the same object for each scenario step
    :param context: step or scenario context
    :return:  RequestsStepsConfig
    """
    stc = RequestsStepsConfig.get_instance(context)
    assert isinstance(stc, RequestsStepsConfig)
    return stc
