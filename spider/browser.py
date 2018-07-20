#! /usr/bin/env python
# coding: utf8
# @Time: 17-12-30
# @Author: yyq

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from config import CFG


class SimulationChrome(object):
    def __init__(self):
        self.__init_browser()

    def __init_browser(self):
        browser_options = Options()
        browser_options.add_argument("--headless")

        browser_path = CFG.CHROME_BROWSER_PATH
        self.browser = Chrome(executable_path=browser_path, chrome_options=browser_options)
        self.browser.set_page_load_timeout(10)
        self.browser.set_script_timeout(10)
        self.browser.implicitly_wait(20)


# browser = SimulationChrome().browser
