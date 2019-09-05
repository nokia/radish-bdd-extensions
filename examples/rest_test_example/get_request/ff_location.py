# © 2019 Nokia

# Licensed under the BSD 3 Clause license
# SPDX-License-Identifier: BSD-3-Clause

import os

import rest_test_example
from radish_ext.radish.ff_location_base import FeatureFilesLocationBase


class FeatureFilesLocation(FeatureFilesLocationBase):
    def __init__(self):
        super(FeatureFilesLocation, self).__init__()
        self.start_path = self.get_absolute_file_location_path(__file__)
        self.feature_files_location = os.path.join(self.get_stories_dir(rest_test_example.__package__))
        self.feature_files = [
            "get_request.feature",
        ]


if __name__ == "__main__":
    FeatureFilesLocation().main()
