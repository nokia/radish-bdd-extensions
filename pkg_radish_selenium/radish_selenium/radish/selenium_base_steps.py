# © 2019 Nokia

# Licensed under the BSD 3 Clause license
# SPDX-License-Identifier: BSD-3-Clause

from nose.tools import assert_equal, assert_in
from radish.stepmodel import Step
from radish_ext.radish.steps_decorator import ext_steps_replace_from_test_data
from radish_ext.sdk.l import Logging
from radish_selenium.radish.selenium_steps_config import get_selenium_config
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait


def open_web_browser(scenario):
    stc_selenium = get_selenium_config(scenario.context)
    stc_selenium.log.info('Open web browser for scenario: {}'.format(scenario))
    try:
        stc_selenium.open_browser()
    except Exception as e:
        stc_selenium.log.exception('Webdriver open problem: {}'.format(e))
        stc_selenium.driver = None
    return stc_selenium.driver


def attach_screenshot_on_failure(step):
    if step.state is not Step.State.FAILED:
        return
    stc_selenium = get_selenium_config(step.context)
    try:
        stc_selenium.attach_screenshot_to_tests_report(step)
    except:
        stc_selenium.log.exception('Getting screenshot error')


def attach_page_source_on_failure(step):
    if step.state is not Step.State.FAILED:
        return
    stc_selenium = get_selenium_config(step.context)
    try:
        stc_selenium.attach_driver_page_source_to_test_report(step, stc_selenium.driver)
    except:
        stc_selenium.log.exception('Getting page source error')


def attach_console_log_on_failure(step):
    if step.state is not Step.State.FAILED:
        return
    stc_selenium = get_selenium_config(step.context)
    try:
        stc_selenium.attach_driver_console_log_to_test_report(step, stc_selenium.driver)
    except:
        stc_selenium.log.exception('Getting console log error')


def close_web_browser(scenario):
    stc_selenium = get_selenium_config(scenario.context)
    stc_selenium.log.info('Close web browser for scenario: {}'.format(scenario))
    if stc_selenium.driver:
        try:
            stc_selenium.driver.close()
        except:
            stc_selenium.log.exception('Driver close failure')
        stc_selenium.driver = None


@ext_steps_replace_from_test_data()
class SeleniumBaseSteps:
    ignore = ['_attach_screenshot', '_get_driver', '_get_element_text_in_outer_html']

    def __init__(self) -> None:
        super().__init__()
        self.log = Logging.get_object_logger(self)

    def _attach_screenshot(self, step):
        stc_selenium = get_selenium_config(step.context)
        stc_selenium.attach_screenshot_to_tests_report(step)

    def _get_driver(self, context):
        stc_selenium = get_selenium_config(context)
        assert isinstance(stc_selenium.driver, WebDriver), f'{stc_selenium.driver} is not supported Driver'
        return stc_selenium.driver

    def _get_element_text_in_outer_html(self, step, by, by_value, text_to_search):
        driver = self._get_driver(step.context)
        input_elements = driver.find_elements(by, by_value)
        for element in input_elements:
            input_html = element.get_attribute('outerHTML')
            if text_to_search in input_html:
                self.log.debug(element)
                yield element

    def open_url_in_a_web_browser(self, step, url):
        """open url {url:QuotedString} in a web browser"""
        open_web_browser(step)
        driver = self._get_driver(step.context)
        driver.get(url)

    def user_input_text(self, step, text, identifier):
        """User input text {text:QuotedString} in {identifier:QuotedString} field"""
        for input_element in self._get_element_text_in_outer_html(step, By.TAG_NAME, 'input', identifier):
            input_element.send_keys(text)
            self._attach_screenshot(step)
            break
        else:
            raise AssertionError(f'Did not find input element with text {identifier}')

    def user_submit_form(self, step, identifier):
        """User submit {identifier:QuotedString} form"""
        for submit_button in self._get_element_text_in_outer_html(step,
                                                                  By.XPATH,
                                                                  '//button[@type="submit"]',
                                                                  identifier):
            submit_button.click()
            self._attach_screenshot(step)
            break
        else:
            raise AssertionError(f'Did not find submit button for {identifier}')

    def click_link(self, step, link_text):
        """click link {link_text:QuotedString}"""
        driver = self._get_driver(step.context)
        link = driver.find_element_by_link_text(link_text)
        link.click()

    def page_title_should_be(self, step, title):
        """page title should be {title:QuotedString}"""
        stc_selenium = get_selenium_config(step.context)
        assert isinstance(stc_selenium.driver, WebDriver)
        assert_equal(stc_selenium.driver.title, title)
        self._attach_screenshot(step)

    def page_title_should_contain(self, step, title):
        """page title should contain {title:QuotedString}"""
        stc_selenium = get_selenium_config(step.context)
        assert isinstance(stc_selenium.driver, WebDriver)
        assert_in(title, stc_selenium.driver.title)
        self._attach_screenshot(step)

    def user_should_see_link(self, step, link_text):
        """User should see link {link_text:QuotedString} on page"""
        driver = self._get_driver(step.context)
        WebDriverWait(driver, 10).until(
            ec.visibility_of_element_located((By.LINK_TEXT, link_text)))
        self._attach_screenshot(step)
