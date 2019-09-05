# © 2019 Nokia

# Licensed under the BSD 3 Clause license
# SPDX-License-Identifier: BSD-3-Clause

import os
from abc import ABCMeta
from urllib.parse import urlparse, urlunparse

from pkg_radish_ext.radish_ext.sdk.cfg import CfgComponent
from radish_ext.sdk.config import Config
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util import Retry


class RestClientException(Exception):
    pass


class HTTPException(Exception):
    def __init__(self, message=None, status=None, content=None, response=None):
        super(HTTPException, self).__init__()
        self.message = message
        self.status = status
        self.content = content
        self.response = response

    def __str__(self):
        return self.message if self.message else 'HTTP response: %d\n%s' % (self.status, self.content)


class RestConfig(Config, metaclass=ABCMeta):
    def __init__(self):
        super(RestConfig, self).__init__()
        self.connect_timeout = 15
        self.read_timeout = 10
        self.http_proxy = None
        self.https_proxy = None
        self.ssl_verify = False
        self.protocol = 'http'
        self.host = 'localhost'
        self.port = None
        self._url = None
        self.number_of_retries = 3

    def _remove_port_from_url(self):
        parsed_url = urlparse(self._url)
        if parsed_url.port:
            self.log.warning('Removing port {} from url'.format(parsed_url.port))
            parsed_url_parts = list(parsed_url)
            parsed_url_parts[1] = ":".join(parsed_url_parts[1].split(":")[:-1])
            output = urlunparse(parsed_url_parts)
            self.log.info('Url: {} was changed to: {}'.format(self._url, output))
            return output
        else:
            return self._url

    @property
    def url(self):
        forbidden_ports = {
            'https': 443,
            'http': 80,
        }
        if self.protocol and self.port and forbidden_ports[self.protocol] == self.port:
            return self._remove_port_from_url()
        # elif self.protocol and self.port is None and self.protocol in forbidden_ports:
        # output = urlunparse([self.protocol, self.])
        else:
            return self._url

    @url.setter
    def url(self, value):
        self._url = value
        if value is None:
            self.protocol = None
            self.host = None
            self.port = None
            return
        parsed_url = urlparse(value)
        self.protocol = parsed_url.scheme
        self.host = parsed_url.hostname
        self.port = parsed_url.port
        if self.port is None:
            if self.protocol == 'https':
                self.port = 443
            elif self.protocol == 'http':
                self.port = 80
            else:
                self.log.warning('Protocol {0} is not supported in port recognition'.format(self.protocol))

    def __set_schema_proxy(self, cfg_section, proxy_schema):
        proxy_key = '{}_proxy'.format(proxy_schema)
        proxy_value = None if proxy_key not in cfg_section else cfg_section[proxy_key]
        setattr(self, proxy_key, proxy_value)

    def set_http_proxy(self, cfg_section):
        self.__set_schema_proxy(cfg_section, 'http')

    def set_https_proxy(self, cfg_section):
        self.__set_schema_proxy(cfg_section, 'https')

    def set_ssl_verify(self, cfg, section_name):
        ssl_verify_key = 'ssl_verify'
        cfg_section = cfg[section_name]
        if ssl_verify_key in cfg_section:
            ssl_verify_value = os.path.join(os.path.dirname(cfg[CfgComponent.CONFIG_FILE_PATH]),
                                            cfg_section[ssl_verify_key])
        else:
            ssl_verify_value = False
        setattr(self, ssl_verify_key, ssl_verify_value)


class SimpleRestConfig(RestConfig):
    def set_properties(self, url, connect_timeout=15, read_timeout=10, http_proxy=None, https_proxy=None,
                       ssl_verify=False):
        self._url = url
        self.connect_timeout = connect_timeout
        self.read_timeout = read_timeout
        self.http_proxy = http_proxy
        self.https_proxy = https_proxy
        self.ssl_verify = ssl_verify
        return self


class RestConfigFromCfg(RestConfig):
    def set_properties(self, cfg, section):
        if 'url' in cfg[section]:
            self._url = cfg[section]["url"]
        elif 'Ip' in cfg[section]:
            self.host = cfg[section]['Ip']
            self.port = cfg[section].get('Port', None)
            port_str = ':{}'.format(self.port) if self.port else ''
            self.protocol = cfg[section].get('Protocol', 'http')
            self.url = '{0.protocol}://{0.host}{1}'.format(self, port_str)

        else:
            raise NotImplementedError('set_properties not implemented for section: {}, content: {}'.format(
                section, cfg[section]
            ))
        self.set_http_proxy(cfg[section])
        self.set_https_proxy(cfg[section])
        self.set_ssl_verify(cfg, section)
        return self


class RestClient(object):
    def __init__(self, rest_config):
        """
        :param rest_config:
        :type rest_config:  RestConfig
        """
        super(RestClient, self).__init__()
        self.config = rest_config
        self.url = self.config.url.rstrip('/')
        self.timeout = (self.config.connect_timeout, self.config.read_timeout)
        self.proxies = {'http': self.config.http_proxy,
                        'https': self.config.https_proxy}

        self.default_kwargs = {'timeout': self.timeout,
                               'proxies': self.proxies,
                               }

        self.session = Session()
        # Disabling trust environment settings for proxy configuration, default authentication and similar.
        self.session.trust_env = False
        self.session.verify = self.config.ssl_verify

    def __uri(self, query):
        while query.startswith('/'):
            query = query[1:]
        return self.url + '/' + query

    def _get_raw_url(self):
        parsed_url = urlparse(self.url)
        return "%s://%s" % (parsed_url.scheme, parsed_url.netloc)

    @staticmethod
    def is_2xx_ok(status):
        return status / 100 == 2

    @staticmethod
    def is_3xx_ok(status):
        return status / 100 == 3

    def check_status(self, response, is_ok_method='is_2xx_ok'):
        if is_ok_method is None:
            is_ok = getattr(self, 'is_2xx_ok')
        elif hasattr(self, is_ok_method):
            is_ok = getattr(self, is_ok_method)
        else:
            raise RestClientException("%s is_ok_method does not exist" % is_ok_method)
        if not is_ok(response.status_code):
            raise HTTPException(status=response.status_code, content=response.content, response=response)

    def get_final_kwargs(self, **kwargs):
        """Method is used in all HTTP methods to set default kwargs if they are not passed:
               {'timeout' : (connect_timeout, read_timeout)}"""
        final_kwargs = {}
        final_kwargs.update(self.default_kwargs)
        final_kwargs.update(**kwargs)
        return final_kwargs

    def requests_retry_session(self,
                               backoff_factor=0.3,
                               session=None):

        """
        Method which retries sending request after certain amount of time.

        :param backoff_factor: A backoff factor to apply between attempts after the second try.
        :param session: Current session object.
        :return: Session with request retry mechanism.
        """
        retry = Retry(
            total=self.config.number_of_retries,
            read=self.config.number_of_retries,
            connect=self.config.number_of_retries,
            backoff_factor=backoff_factor
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def get(self, query, raw_query=False, **kwargs):
        if raw_query:
            return self.requests_retry_session(session=self.session).get(query, **self.get_final_kwargs(**kwargs))
        else:
            return self.requests_retry_session(session=self.session).get(self.__uri(query),
                                                                         **self.get_final_kwargs(**kwargs))

    def post(self, query, raw_query=False, data=None, json=None, **kwargs):
        if raw_query:
            return self.requests_retry_session(session=self.session).post(query, data=data, json=json,
                                                                          **self.get_final_kwargs(**kwargs))
        else:
            return self.requests_retry_session(session=self.session).post(self.__uri(query), data=data,
                                                                          json=json,
                                                                          **self.get_final_kwargs(**kwargs))

    def put(self, query, raw_query=False, data=None, **kwargs):
        if not raw_query:
            query = self.__uri(query)
        return self.requests_retry_session(session=self.session).put(query, data=data,
                                                                     **self.get_final_kwargs(**kwargs))

    def delete(self, query, raw_query=False, **kwargs):
        if not raw_query:
            query = self.__uri(query)
        return self.requests_retry_session(session=self.session).delete(query, **self.get_final_kwargs(**kwargs))

    def head(self, query, raw_query=False, **kwargs):
        if not raw_query:
            query = self.__uri(query)
        return self.requests_retry_session(session=self.session).head(query, **self.get_final_kwargs(**kwargs))

    def options(self, query, raw_query=False, **kwargs):
        if not raw_query:
            query = self.__uri(query)
        return self.requests_retry_session(session=self.session).options(query, **self.get_final_kwargs(**kwargs))

    def patch(self, query, raw_query=False, data=None, **kwargs):
        if not raw_query:
            query = self.__uri(query)
        return self.requests_retry_session(session=self.session).patch(query, data=data,
                                                                       **self.get_final_kwargs(**kwargs))

    def __del__(self):
        self.session.close()
