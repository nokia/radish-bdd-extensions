# © 2019 Nokia

# Licensed under the BSD 3 Clause license
# SPDX-License-Identifier: BSD-3-Clause

import logging
from copy import deepcopy
from io import StringIO

from radish import world
from radish.hookregistry import before, after
from radish.stepmodel import Step
from radish_ext.sdk.cfg import CfgComponent, CfgConfig


def get_my_loggers():
    logger_names = [None, 'requests', 'nose.core', 'paramiko', 'csfpy', 'urllib3']
    loggers = [logging.getLogger(a) for a in logger_names]
    return loggers


def add_log_string_io_handler(context):
    if hasattr(context, 'log_buffer'):
        return
    context.log_buffer = StringIO()
    context.step_log_handler = logging.StreamHandler(context.log_buffer)
    formatter = logging.Formatter("%(asctime)s - %(filename)s:%(lineno)s - %(levelname)s - %(message)s")
    context.step_log_handler.setFormatter(formatter)
    for logger in get_my_loggers():
        logger.addHandler(context.step_log_handler)


def append_logs_to_step_report(step):
    assert isinstance(step, Step)
    step.context.step_log_handler.flush()
    step.context.log_buffer.flush()
    logs = step.context.log_buffer.getvalue()
    step.context.log_buffer.seek(0)
    step.context.log_buffer.truncate(0)

    if logs:
        step.embed(logs, 'text/plain')
        # embed_data_to_step(step, logs, 'text/plain')


def remove_log_string_io_handler(context):
    if not hasattr(context, 'log_buffer'):
        return
    for logger in get_my_loggers():
        logger.removeHandler(context.step_log_handler)
    context.log_buffer.close()
    del context.log_buffer
    del context.step_log_handler


# @before.each_scenario
# def before_each_scenario(scenario):

@before.all
def before_all(features, marker):
    if 'cfg' in world.config.user_data:
        config_dirs = []
        if 'package' in world.config.user_data:
            try:
                package = __import__(world.config.user_data['package'])
                if hasattr(package, 'get_etc_dir'):
                    config_dirs.append(package.get_etc_dir())
            except Exception as e:
                print(f'Error: {e}')
        cfg = CfgComponent(CfgConfig().set_properties(world.config.user_data['cfg'], None, config_dirs))
    else:
        cfg = CfgComponent(CfgConfig())
    for feature in features:
        feature.context.cfg = deepcopy(cfg.cfg)


@before.each_scenario
def before_each_scenario(scenario):
    if hasattr(scenario.parent.context, 'cfg'):
        scenario.context.cfg = deepcopy(scenario.parent.context.cfg)
    add_log_string_io_handler(scenario.context)


@after.each_step
def after_each_step_embed_logs(step):
    append_logs_to_step_report(step)


@after.each_scenario
def after_each_scenario_embed_logs(scenario):
    remove_log_string_io_handler(scenario.context)
