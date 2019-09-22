# © 2019 Nokia

# Licensed under the BSD 3 Clause license
# SPDX-License-Identifier: BSD-3-Clause

import random
import re
import string
from functools import wraps

from radish_ext.radish.step_config import iter_all_context_step_configs, StepConfig
from radish_ext.sdk.l import Logging

log = Logging.get_logger(__name__)


def _ext_step_decorator(decorator):
    def decorate(cls):
        for attr in cls.__dict__:  # there's propably a better way to do this
            if callable(getattr(cls, attr)) and \
                    ((hasattr(cls, 'ignore') and attr not in cls.ignore) or not hasattr(cls, 'ignore')):
                setattr(cls, attr, decorator(getattr(cls, attr)))
        return cls

    return decorate


def ext_steps_replace_from_test_data():
    return _ext_step_decorator(replace_or_generate_test_data)


def steps_arguments_update(update_function, f):
    @wraps(f)
    def decorated(*a, **kw):
        step = None
        if len(a) >= 2:
            step = a[1]
            StepConfig.get_instance(step.context)
            args = list(a[2:])
            for number, arg in enumerate(args):
                if isinstance(arg, str):
                    for step_config in iter_all_context_step_configs(step.context):
                        new_arg = step_config.test_data.replace_test_data(arg)
                        args[number] = new_arg
            a = list(a[0:2]) + args

        if kw:
            if 'step' in kw:
                step = kw['step']
                StepConfig.get_instance(step.context)
            for k, v in kw.items():
                if k not in ['step'] and isinstance(v, str):
                    for step_config in iter_all_context_step_configs(step.context):
                        new_v = update_function(step_config, v)
                        kw[k] = new_v
        return f(*a, **kw)

    return decorated


def replace_or_generate_test_data(f):
    return generate_test_data(replace_values_based_on_test_data(f))


def replace_values_based_on_test_data(f):
    def x(step_config, value):
        return step_config.test_data.replace_test_data(value)

    return steps_arguments_update(x, f)


def generate_test_data(f):
    def x(step_config, value):
        pattern = r'\${generate.(?P<prefix>.*)}'
        m = re.search(pattern, value)
        if m:
            prefix = m.group('prefix')
            step_config.test_data.data['generate'][prefix] = prefix + ''.join(
                random.choice(string.ascii_lowercase)
                for i in range(10))
            ret = re.sub(pattern, step_config.test_data.data['generate'][prefix], value)
            if ret != value:
                log.info(f'generate IN : {value} OUT: {ret}')
        return value

    return steps_arguments_update(x, f)
