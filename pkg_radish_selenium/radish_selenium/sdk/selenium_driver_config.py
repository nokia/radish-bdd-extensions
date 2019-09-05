# © 2019 Nokia

# Licensed under the BSD 3 Clause license
# SPDX-License-Identifier: BSD-3-Clause

from radish_ext.sdk.config import Config


class SeleniumDriverConfig(Config):
    def __init__(self):
        super(SeleniumDriverConfig, self).__init__()
        self.capabilities = None
        self.url = None

    def set_properties(self, cfg, section):
        """
        yaml settings example:
        Selenium:
          url: http://localhost:4444/wd/hub
          capabilities:
        #    browserName: firefox
            browserName: chrome
        #    version: "65.0"
        #    enableVNC: True
        #    enableVideo: False
            proxy:
              proxyType: 'MANUAL'
              sslProxy: '135.245.192.7:8000'
              httpProxy: '135.245.192.7:8000'
        :type cfg: dict
        :type section: string
        :rtype: SeleniumDriverConfig
        """
        selenium_cfg = cfg.get(section)
        self.log.info(selenium_cfg)
        self.url = selenium_cfg.get('url')
        self.capabilities = selenium_cfg.get('capabilities')
        return self
