# © 2019 Nokia

# Licensed under the BSD 3 Clause license
# SPDX-License-Identifier: BSD-3-Clause

from copy import deepcopy

from radish import before, world
from radish_ext.sdk.cfg import CfgComponent, CfgConfig
from radish_selenium import get_radish_selenium_etc_dir


@before.all
def before_all(features, marker):
    if "cfg" in world.config.user_data:
        cfg = CfgComponent(CfgConfig().set_properties(world.config.user_data['cfg'], None,
                                                      [get_radish_selenium_etc_dir()]))
    else:
        cfg = CfgComponent(CfgConfig())
    for feature in features:
        feature.context.cfg = deepcopy(cfg.cfg)
