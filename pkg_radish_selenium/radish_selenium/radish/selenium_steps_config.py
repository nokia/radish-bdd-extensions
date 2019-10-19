# © 2019 Nokia

# Licensed under the BSD 3 Clause license
# SPDX-License-Identifier: BSD-3-Clause

import unicodedata

from radish_ext.radish.step_config import StepConfig
from radish_selenium.radish.selenium_test_data import SeleniumTestData
from radish_selenium.sdk.selenium_driver_config import SeleniumDriverConfig
from radish_selenium.sdk.selenium_driver_factory import SeleniumDriverFactory


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
        try:
            step.embed(self.driver.get_screenshot_as_base64(), 'image/png', encode_data_to_base64=False)
        except Exception as e:
            self.log.warning(f'Get browser screen shot error:\n{e}')

    def attach_page_source_to_test_report(self, step, page_source):
        if isinstance(page_source, bytes):
            page_source = page_source.decode('utf-8')
        page_source = unicodedata.normalize('NFKD', page_source)
        step.embed(data=page_source,
                   mime_type='text/html',
                   encode_data_to_base64=True)

    def attach_driver_page_source_to_test_report(self, step, driver=None):
        self.log.debug('Attaching html to tests report')
        if driver is None:
            if self.driver is None:
                self.log.debug("Driver is not opened - can not attach html source")
                return
            driver = self.driver
        try:
            self.attach_page_source_to_test_report(step=step, page_source=driver.page_source)
        except Exception as e:
            self.log.warning(f'Get browser page_source error:\n{e}')

    def attach_driver_console_log_to_test_report(self, step, driver=None):
        self.log.debug(('Attaching console log to tests report'))
        if driver is None:
            if self.driver is None:
                self.log.debug('Driver is not opened - can not get console logs')
                return
            driver = self.driver
        console_logs = []
        try:
            for entry in driver.get_log('browser'):
                console_logs.append(str(entry))
            step.embed(data='\n'.join(console_logs),
                       encode_data_to_base64=True)
        except Exception as e:
            self.log.warning(f'Get browser console log error:\n{e}')

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
