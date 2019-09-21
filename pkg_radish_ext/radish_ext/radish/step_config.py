# © 2019 Nokia

# Licensed under the BSD 3 Clause license
# SPDX-License-Identifier: BSD-3-Clause

from radish_ext.sdk.l import Logging


class StepConfig(object):
    def __init__(self, context):
        """
        context - provided by radish:
            - each feature has its own context
            - for each scenario and its steps context is common however different than feature context
            - feature context may be retrieved in scenario using scenario.parent.context code
            - feature context may be retrieved in step using step.parent.parent.context code
        """
        super(StepConfig, self).__init__()
        self.context = context
        self.cfg = context.cfg
        setattr(self.context, 'stc_%s' % self.__class__.__name__, self)
        self.log = Logging.get_object_logger(self)

    @classmethod
    def get_instance(cls, context):
        instance_attr_name = 'stc_%s' % cls.__name__
        if hasattr(context, instance_attr_name):
            return getattr(context, instance_attr_name)
        return cls(context)

    @staticmethod
    def get_test_tags(all_tags, strip_prefix=False):
        test_tags = [tag.name[len('test_'):] if strip_prefix else tag.name
                     for tag in all_tags
                     if tag.name.startswith("test_")]
        # remove duplicates
        test_tags = list(set(test_tags))
        return test_tags

    @staticmethod
    def get_test_tags_str(all_tags, strip_prefix=False):
        return '_'.join(StepConfig.get_test_tags(all_tags, strip_prefix=strip_prefix))

    @classmethod
    def get_instances(cls, context):
        """
        Returns all class instances created during test execution
        :param context: radish context
        :return: list of class instances stored in radish context
        """
        instances = []
        for step_config_instance in [getattr(context, attr) for attr in dir(context) if attr.startswith('stc')]:
            if isinstance(step_config_instance, cls):
                assert isinstance(step_config_instance, cls)
                instances.append(step_config_instance)
        return instances
