# © 2019 Nokia

# Licensed under the BSD 3 Clause license
# SPDX-License-Identifier: BSD-3-Clause

import json
from os.path import basename, splitext


def get_cucumber_json_report_name(start_file_name):
    """
    The cucmber report name is generated based on start_file_name
        * "start" string will be removed and rest of start_file_name will be used in cucumber report name

    :param start_file_name: start file name parsed to cucumber report name
    :return: cucumber json file name
    """
    return 'cucumber_result_{}.json'.format(basename(splitext(start_file_name)[0]).replace('start_', ''))

def json_pretty_dump(json_):
    return json.dumps(json_, indent=4, sort_keys=True)
