# © 2019 Nokia

# Licensed under the BSD 3 Clause license
# SPDX-License-Identifier: BSD-3-Clause

from copy import deepcopy

from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from testcontainers.selenium import BrowserWebDriverContainer


class SeleniumDriverFactory(object):
    """
    Driver factory for remote WebDriver
    """
    @classmethod
    def get_local_driver(cls, config):
        """

        :type config: radish_ext.sdk.ui.selenium_driver_config.SeleniumDriverConfig
        :rtype: selenium.webdriver.remote.webdriver.WebDriver
        """
        desired_capabilities = deepcopy(config.capabilities)
        browser_name = desired_capabilities.pop('browserName')
        registered_browsers = {'firefox': webdriver.Firefox, 'chrome': webdriver.Chrome, 'opera': webdriver.Opera,
                               'phantomjs': webdriver.PhantomJS, 'safari': webdriver.Safari, 'edge': webdriver.Edge,
                               'ie': webdriver.Ie, 'internetexplorer': webdriver.Ie}
        driver = registered_browsers[browser_name](desired_capabilities=desired_capabilities)
        return driver


    @classmethod
    def get_remote_driver(cls, config):
        """

        :type config: radish_ext.sdk.ui.selenium_driver_config.SeleniumDriverConfig
        :rtype: selenium.webdriver.remote.webdriver.WebDriver
        """
        driver = WebDriver(config.url, desired_capabilities=config.capabilities)
        return driver

    @classmethod
    def get_testcontainers_driver(cls, config):
        """

        :type config: radish_ext.sdk.ui.selenium_driver_config.SeleniumDriverConfig
        :rtype: selenium.webdriver.remote.webdriver.WebDriver
        """
        container = BrowserWebDriverContainer(capabilities=config.capabilities)
        container.start()
        driver = container.get_driver()
        return driver

    @classmethod
    def get_driver(cls, config):
        """

        :type config: radish_selenium.sdk.selenium_driver_config.SeleniumDriverConfig
        :rtype: selenium.webdriver.remote.webdriver.WebDriver
        """
        if config.type == 'remote':
            return cls.get_remote_driver(config)
        elif config.type == 'testcontainers':
            return cls.get_testcontainers_driver(config)
        elif config.type == 'local':
            return cls.get_local_driver(config)
        else:
            raise NotImplementedError(f'{config.type} is not supported driver type')

