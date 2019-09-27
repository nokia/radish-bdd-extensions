# © 2019 Nokia

# Licensed under the BSD 3 Clause license
# SPDX-License-Identifier: BSD-3-Clause

import os
import re

from radish import matcher
from radish.matcher import match_step, StepMatch, ParseStepArguments
from radish_ext.sdk.l import Logging


def not_implemented_steps_stub_generator(file_to_append_steps, file_template=None, step_template=None,
                                         quoted_string='{:QuotedString}'):
    """Adding not implemented steps stubs to memory and to file

    :param file_to_append_steps: Steps stubs will be added to file
        if file_to_append_step is None: steps will be added to runtime only
        if file_to_append_step not exists it will be created based on template
    """
    log = Logging.get_logger('csfpy.main_wrapper.NotImplementedStespStub')
    if file_template is None:
        file_template = """from radish.stepregistry import steps


@steps
class GeneratedSteps(object):
    pass
    """

    if step_template is None:
        step_template = '''
    def {method_name}(self, step, {argument_names}):
        """{sentence}"""
        raise NotImplementedError('This step is not implemented yet')
    '''
    if file_to_append_steps is not None:
        if not os.path.exists(file_to_append_steps):
            log.debug('Creating steps definition file: %s' % file_to_append_steps)
            file_to_write_steps = open(file_to_append_steps, 'a')
            file_to_write_steps.write(file_template)
            file_to_write_steps.flush()
        else:
            file_to_write_steps = open(file_to_append_steps, 'a')

    def not_implemented_step_stub_method(*args, **kwargs):
        raise NotImplementedError('This step is not implemented yet')

    # merge step method replacement of original merge_step radish method
    def merge_step(step, steps):
        """
            Merges a single step with the registered steps

            :param Step step: the step from a feature file to merge
            :param list steps: the registered steps
        """
        match = match_step(step.context_sensitive_sentence, steps)
        if not match or not match.func:
            # repalced block of original method
            # instead of rising StepDefinitionNotFoundError adding no_implemented_step_stub_method

            # remove Gherkin step base words
            sentence = re.sub(r'^(And|Given|When|Then|But)\s*', '', step.sentence)
            # replace "quotedStrings"
            sentence = re.sub('([^"]|^)"([^"]+)"([^"]|$)', r'\1{0}\3'.format(quoted_string), sentence)

            if sentence not in steps:
                sentence = add_sentence(sentence)
                steps[sentence] = not_implemented_step_stub_method
            match = StepMatch(not_implemented_step_stub_method, ParseStepArguments(match))
        step.definition_func = match.func
        step.argument_match = match.argument_match

    # radish monkey patching
    matcher.merge_step = merge_step

    def add_sentence(sentence):
        log.debug('Adding step defintion for sentence:\n\t%s' % sentence)
        method_name = re.sub('[^0-9a-zA-Z_]+', '_', sentence).lower()
        method_name = method_name.replace('quotedstring', '')
        method_name = re.sub('_+', '_', method_name)
        method_name = method_name.lstrip('_')
        method_name = method_name.rstrip('_')

        # replace all not expected characters from method name
        if file_to_append_steps is not None:
            step_method_args = ', '.join(['arg_%d' % i for i in range(sentence.count(quoted_string))])
            step = step_template.format(method_name=method_name,
                                        argument_names=step_method_args,
                                        sentence=sentence)
            log.debug('Adding step definition to file:\n%s' % step)
            file_to_write_steps.write(step)
            file_to_write_steps.flush()
        return sentence
