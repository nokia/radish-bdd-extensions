# © 2019 Nokia

# Licensed under the BSD 3 Clause license
# SPDX-License-Identifier: BSD-3-Clause

from pkg_radish_ext.radish_ext.sdk.l import Logging
from radish_ext.sdk.helpers import json_pretty_dump


class RequestsBaseTools(object):
    def __init__(self):
        super(RequestsBaseTools, self).__init__()
        self.log = Logging.get_object_logger(self)

    def log_response(self, response, with_details=True):
        """
        :param response: to be logged
        :param with_details: if True response and request details logged
        """
        self.log.debug(response)
        if with_details:
            self.log.debug("Request method: {0.method} url: {0.url}".format(response.request))
            self.log.debug("Request headers \n{}".format(json_pretty_dump(dict(response.request.headers))))
            self.log.debug("Response headers \n{}".format(json_pretty_dump(dict(response.headers))))
            self.log.debug("Response history: {}".format(response.history))
            self.log.debug("Response cookies: {}".format(json_pretty_dump(list(response.cookies.items()))))
            self.log.debug("Response cookies paths: {}".format(json_pretty_dump(response.cookies.list_paths())))
            self.log.debug("Response cookies domains: {}".format(json_pretty_dump(response.cookies.list_domains())))

        self.log.debug("Response content: {}".format(response.content))

    def get_request_category(self, response):
        """
        All HTTP response status codes are separated into five classes (or categories)

        There are five values for the first digit:

            1xx (Informational): The request was received, continuing process
            2xx (Successful): The request was successfully received, understood, and accepted
            3xx (Redirection): Further action needs to be taken in order to complete the request
            4xx (Client Error): The request contains bad syntax or cannot be fulfilled
            5xx (Server Error): The server failed to fulfill an apparently valid request

        :param response: request response
        :return: first digit of status_code - representing response category
        :rtype: int
        """
        return response.status_code // 100
