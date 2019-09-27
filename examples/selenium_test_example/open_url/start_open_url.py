# © 2019 Nokia

# Licensed under the BSD 3 Clause license
# SPDX-License-Identifier: BSD-3-Clause

from radish.main import main
from radish_ext import get_radish_ext_dir
from radish_ext.sdk.helpers import get_cucumber_json_report_name, json_pretty_dump
from radish_selenium import get_radish_selenium_dir

from selenium_test_example.open_url.ff_location import FeatureFilesLocation

if __name__ == "__main__":
    start_path, full_path_ff = FeatureFilesLocation().get_full_ff_path()
    print("Feature files to run:\n{}".format(json_pretty_dump(full_path_ff)))
    print("Feature files implementation location: {}".format(start_path))
    main(args=['--write-ids',
               '-b', get_radish_ext_dir(),
               '-b', get_radish_selenium_dir(),
               '-b', start_path,
               '-t',
               '--cucumber-json={}'.format(get_cucumber_json_report_name(__file__)),
               '--user-data', 'cfg=ui_conf.yaml',
               '--tags', 'auto',
               *full_path_ff]
         )
