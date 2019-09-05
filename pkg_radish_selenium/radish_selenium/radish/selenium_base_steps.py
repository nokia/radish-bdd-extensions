# © 2019 Nokia

# Licensed under the BSD 3 Clause license
# SPDX-License-Identifier: BSD-3-Clause
from string import Template

from nose.tools import assert_equal, assert_in
from radish.stepmodel import Step

from radish_ext.radish.template_with_nested_data_replacer import TemplateForNestedDict
from radish_selenium.radish.selenium_steps_config import get_selenium_config
from selenium.webdriver.remote.webdriver import WebDriver


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


def close_web_browser(scenario):
    stc_selenium = get_selenium_config(scenario.context)
    stc_selenium.log.info('Close web browser for scenario: {}'.format(scenario))
    if stc_selenium.driver:
        try:
            stc_selenium.driver.close()
        except:
            stc_selenium.log.exception('Driver close failure')
        stc_selenium.driver = None


class SeleniumBaseSteps:
    def open_url_in_a_web_browser(self, step, url):
        """open url {url:QuotedString} in a web browser"""
        open_web_browser(step)
        stc_selenium = get_selenium_config(step.context)
        url = stc_selenium.test_data.replace_test_data(url)
        assert isinstance(stc_selenium.driver, WebDriver)
        stc_selenium.driver.get(url)

    def page_title_is(self, step, title):
        """page title is {title:QuotedString}"""
        stc_selenium = get_selenium_config(step.context)
        assert isinstance(stc_selenium.driver, WebDriver)
        assert_equal(stc_selenium.driver.title, title)
        stc_selenium.attach_screenshot_to_tests_report(step)

    def page_title_contains(self, step, title):
        """page title contains {title:QuotedString}"""
        stc_selenium = get_selenium_config(step.context)
        assert isinstance(stc_selenium.driver, WebDriver)
        assert_in(title, stc_selenium.driver.title)
        stc_selenium.attach_screenshot_to_tests_report(step)
