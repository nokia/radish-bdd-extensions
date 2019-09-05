# © 2019 Nokia

# Licensed under the BSD 3 Clause license
# SPDX-License-Identifier: BSD-3-Clause

from nose.tools import assert_equals, assert_in, assert_equal

from pkg_radish_ext.radish_ext.sdk.l import Logging
from radish_rest.radish.requests_steps_config import get_requests_config
from radish_rest.radish.requests_tools import RequestsBaseTools


class RequestsBaseSteps(object):
    ignore = ['_log_response']

    def __init__(self):
        super(RequestsBaseSteps, self).__init__()
        self.log = Logging.get_object_logger(self)
        self.tools = RequestsBaseTools()

    def _log_response(self, response):
        self.tools.log_response(response)

    def request_is_sent_to_url_by_a_http_client_with_http_method_and_uri(self, step, request_name, url, http_method):
        """request {request_name:QuotedString} is sent to url {url:QuotedString} by a http client with {http_method:QuotedString} method"""
        stc = get_requests_config(step.context)
        url = stc.test_data.replace_test_data(url)
        client = stc.get_client(url)
        self.log.debug('http_method: {0} ,url: {1} '.format(http_method, url))
        http_request_method = getattr(client, http_method.lower())
        response = http_request_method(client.url, raw_query=True)
        self._log_response(response)
        stc.test_data.set_request_response(request_name, response)
        return response

    def response_code_for_request_is(self, step, request_name, expected_status_code):
        """response code for request {:QuotedString} is {:d}"""
        stc = get_requests_config(step.context)
        response = stc.test_data.get_request_response(request_name)
        self._log_response(response)
        assert_equal(
            expected_status_code,
            response.status_code,
            'expected status_code {0} != {1.status_code} received status_code, received content: {1.content}'.format(
                expected_status_code, response
            )
        )

    def response_body_for_request_contains(self, step, request_name):
        """response body for request {:QuotedString} contains:"""
        feature_file_step_text = step.text
        if feature_file_step_text == "${empty}":
            feature_file_step_text = ""
        elif feature_file_step_text == "${do_not_check}":
            self.log.info("Response body assertion not needed.")
            return
        stc = get_requests_config(step.context)
        response = stc.test_data.get_request_response(request_name)
        self._log_response(response)
        assert_in(feature_file_step_text,
                  response.content,
                  'Response body "{0}" does not contain: "{1}"'.format(response.content, feature_file_step_text)
                  )

    def the_request_is_rejected(self, step, request_name):
        """the request {:QuotedString} is rejected"""
        stc = get_requests_config(step.context)
        response = stc.test_data.get_request_response(request_name)
        self._log_response(response)
        assert_in(self.tools.get_request_category(response), [4, 5], response.content)

    def response_headers_for_request_are(self, step, request_name):
        """Response headers for request {request_name:QuotedString} are:
        | header_name  | header_value |"""
        stc = get_requests_config(step.context)
        self.log.info(step.table)
        for response_header in step.table:
            header_name = response_header['header_name']
            header_value = response_header['header_value']
        response = stc.test_data.get_request_response(request_name)
        self.log.info(response)
        assert_equal(
            header_value,
            response.headers[header_name],
            'expected header_value "{0}" != "{1}" received header_value'.format(
                header_value, response.headers[header_name]
            )
        )

    def response_headers_for_request_contains(self, step, request_name):
        """Response headers for request {request_name:QuotedString} contains:
        | header_name  | header_value |"""
        stc = get_requests_config(step.context)
        self.log.info(step.table)
        for response_header in step.table:
            header_name = response_header['header_name']
            header_value = response_header['header_value']
        response = stc.test_data.get_request_response(request_name)
        self.log.info(response)
        assert_in(
            header_value,
            response.headers[header_name],
            'expected header_value "{0}" not in "{1}" received header_value'.format(
                header_value, response.headers[header_name]
            )
        )

    def response_body_for_request_is(self, step, request_name):
        """Response body for request {request_name:QuotedString} is:"""
        stc = get_requests_config(step.context)
        body = step.text
        response = stc.test_data.get_request_response(request_name)
        self.log.info(response)

        if body is not None:
            body = stc.test_data.replace_test_data(body)
            if '\\n' in body:
                self.log.debug('Replacing escaped end of line character in {}'.format(body))
                body = body.replace('\\n', '\n')

        assert_equal(
            body,
            response.text,
            'expected body "{0}" != "{1.text}" received body'.format(
                body, response
            )
        )

    def body_is_defined(self, step, body_name):
        """Body {body_name:QuotedString} is defined"""
        stc = get_requests_config(step.context)
        body = step.text
        stc.test_data.set_body(body_name=body_name, body=body)
        self.log.info(body)

    def response_body_is_empty(self, step):
        """response body is empty"""
        expected_response_content = ''
        stc = get_requests_config(step.context)
        self.log.debug(stc.test_data.response.content)
        assert_equal(str(expected_response_content), str(stc.test_data.response.content),
                     "Response body is '{}' and is not empty".format(stc.test_data.response.content))
