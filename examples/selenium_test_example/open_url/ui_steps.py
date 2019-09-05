# © 2019 Nokia

# Licensed under the BSD 3 Clause license
# SPDX-License-Identifier: BSD-3-Clause

from radish import steps, after
from radish_selenium.radish.selenium_base_steps import SeleniumBaseSteps, attach_page_source_on_failure, close_web_browser


@after.each_step()
def on_ui_test_failure(step):
    attach_page_source_on_failure(step)

@after.each_scenario()
def close_scenarion_browser(scenario):
    close_web_browser(scenario)

@steps
class SeleniumSteps(SeleniumBaseSteps):
    pass