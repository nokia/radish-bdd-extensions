# © 2019 Nokia

# Licensed under the BSD 3 Clause license
# SPDX-License-Identifier: BSD-3-Clause

import logging

from page_objects import PageObject, PageElement, MultiPageElement
from retry import retry
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from radish_ext.sdk.l import Logging


class CSFPageObject(PageObject):
    def __init__(self, webdriver, root_uri=None):
        assert isinstance(webdriver, WebDriver), 'webdriver={} needs to be selenium Webdriver object'.format(webdriver)
        super(CSFPageObject, self).__init__(webdriver=webdriver, root_uri=root_uri)
        self.log = Logging.get_object_logger(self)

    def close_driver(self):
        if self.w:
            self.w.close()
            self.w = None

    def get_screenshot(self):
        return self.w.get_screenshot_as_base64()

    def wait_until_angular_ready(self):
        WebDriverWait(self.w, 10).until(CSFAnglularReady())


class CSFAnglularReady(object):
    """
    If page is running angular.js, wait until it's ready for taking requests. In other case simply skip waiting.

    Previous script running by ExtendedSelenium2Library:
    Path: ExtendedSelenium2Libary/keywords/extendedwaiting.py line 188
          ExtendedSelenium2Libary/__init__.py line 109

        var cb=arguments[arguments.length-1];
        if(window.angular){
            var $inj;
            try {
                 $inj=angular.element(document.querySelector('[data-ng-app],[ng-app],.ng-scope')||document).injector()||angular.injector(['ng'])
            }
            catch(ex){
                $inj=angular.injector(['ng'])
            };
            $inj.get=$inj.get||$inj;
            $inj.get('$browser').notifyWhenNoOutstandingRequests(function(){
                cb(true)
            })
        }
        else {
            cb(true)
        }

        Link to solution: https://github.com/selenide/selenide/issues/525#issuecomment-301173696
    """
    def __call__(self, driver):
        # copy paste this script into console in browser to check, if page running angular.js is ready
        # (window.angular !== undefined) && (angular.element(document.body).injector() !== undefined)" \
        #                  " && (angular.element(document.body).injector().get('$http').pendingRequests.length === 0)
        script = "return (window.angular === undefined) ||" \
                 "((window.angular !== undefined) && (angular.element(document.body).injector() !== undefined)" \
                 " && (angular.element(document.body).injector().get('$http').pendingRequests.length === 0))"
        angularReady = driver.execute_script(script)
        return angularReady is True


class CSFPageElement(PageElement):
    def find(self, context):
        return context.find_element(*self.locator)


class CSFPageWaitForElementInvisible(PageElement):
    """Page element - wait until page element is invisible

    e.g.

    When executed self.not_loading_table_data
        - selenium wait until xpath='//span[text()="Loading..."]' will not be visible


    class SaasPageObjectNBOPortal(CSFPageObject):
        not_loading_table_data = CSFPageWaitForElementInvisible(xpath='//span[text()="Loading..."]')

        def nbo_sees_subscriber_request(self, client_model):
            self.not_loading_table_data
    """

    def find(self, context):
        ww = WebDriverWait(context, 15)
        ww.until(expected_conditions.invisibility_of_element_located(self.locator))


class CSFMultiPageElement(MultiPageElement):
    def find(self, context):
        return context.find_elements(*self.locator)


class CSFPageElementWithRetry(CSFPageElement):
    @retry(NoSuchElementException, tries=5, delay=0.1,
           logger=logging.getLogger('%s.CSFPageElementWithRetry' % __name__))
    def find(self, context):
        return super(CSFPageElementWithRetry, self).find(context=context)
