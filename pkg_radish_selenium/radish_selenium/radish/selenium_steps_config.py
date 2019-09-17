# © 2019 Nokia

# Licensed under the BSD 3 Clause license
# SPDX-License-Identifier: BSD-3-Clause

import unicodedata

from radish_ext.radish.step_config import StepConfig
from radish_selenium.radish.selenium_test_data import SeleniumTestData
from radish_selenium.sdk.selenium_driver_factory import SeleniumDriverFactory
from radish_selenium.sdk.selenium_driver_config import SeleniumDriverConfig


class SeleniumStepConfig(StepConfig):
    def __init__(self, context):
        super(SeleniumStepConfig, self).__init__(context)
        self.driver = None
        self.web_driver_config = SeleniumDriverConfig().set_properties(self.cfg, 'Selenium')
        self.web_driver_factory = SeleniumDriverFactory
        self.test_data = SeleniumTestData(self.cfg)

    def attach_screenshot_to_tests_report(self, step):
        self.log.debug('Attaching screenshot to tests report')
        if self.driver is None:
            self.log.debug("Driver is not opened - can not attach screenshot")
            return
        step.embed(self.driver.get_screenshot_as_base64(), 'image/png', encode_data_to_base64=False)

    def attach_page_source_to_test_report(self, step, page_source):
        if isinstance(page_source, bytes):
            page_source = page_source.decode('utf-8')
        page_source = unicodedata.normalize('NFKD', page_source)
        data_str = page_source.encode('ascii', 'ignore')
        if data_str != page_source:
            self.log.warning('Skipping unicode characters - to allow html attachment in results')
        step.embed(data=data_str,
                   mime_type='text/html',
                   encode_data_to_base64=True)

    def attach_driver_page_source_to_test_report(self, step, driver=None):
        self.log.debug('Attaching html to tests report')
        if driver is None:
            if self.driver is None:
                self.log.debug("Driver is not opened - can not attach html source")
                return
            driver = self.driver
        self.attach_page_source_to_test_report(step=step, page_source=driver.page_source)

    def open_browser_if_not_opened(self):
        if self.driver:
            self.log.debug('Browser already opened: {}'.format(self.driver))
            return False
        else:
            self.open_browser()
            return True

    def open_browser(self):
        self.driver = self.web_driver_factory.get_driver(self.web_driver_config)


def get_selenium_config(context):
    stc = SeleniumStepConfig.get_instance(context)
    assert isinstance(stc, SeleniumStepConfig)
    return stc
