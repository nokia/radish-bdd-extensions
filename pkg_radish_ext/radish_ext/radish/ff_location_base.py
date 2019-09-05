# © 2019 Nokia

# Licensed under the BSD 3 Clause license
# SPDX-License-Identifier: BSD-3-Clause

import os


class FeatureFilesLocationBaseException(Exception):
    pass


class FeatureFilesLocationBase(object):
    def __init__(self):
        super(FeatureFilesLocationBase, self).__init__()
        self._start_path = self.get_absolute_file_location_path(__file__)
        self._feature_files_location = ""
        self._feature_files = []

    @property
    def start_path(self):
        """Absolute path to the feature files implementation location."""
        return self._start_path

    @start_path.setter
    def start_path(self, value):
        self._start_path = value

    @property
    def feature_files_location(self):
        """Absolute path to the directory where feature files are located."""
        return self._feature_files_location

    @feature_files_location.setter
    def feature_files_location(self, value):
        self._feature_files_location = value

    @property
    def feature_files(self):
        """List of feature files names located in feature_files_location directory."""
        return self._feature_files

    @feature_files.setter
    def feature_files(self, values):
        self._feature_files = values

    @staticmethod
    def get_absolute_path(path):
        return os.path.abspath(path)

    def get_absolute_file_location_path(self, file_path):
        return self.get_absolute_path(os.path.dirname(file_path))

    @staticmethod
    def get_stories_dir(package_name='asset_tests'):
        try:
            imported_module = __import__(package_name)
        except ImportError:
            raise FeatureFilesLocationBaseException('"stories" directory not found')
        tmp_stories_dir = os.path.join(os.path.dirname(imported_module.__file__), 'stories')
        if os.path.exists(tmp_stories_dir) is True:
            stories_dir = tmp_stories_dir
        else:
            raise FeatureFilesLocationBaseException('"stories" directory not found')
        return stories_dir

    def get_full_ff_path(self):
        full_path_ff = [os.path.join(self.feature_files_location, a) for a in self.feature_files]
        return self.start_path, full_path_ff

    def get_full_ff_path_with_start_path(self):
        start_path, full_path_ff = self.get_full_ff_path()
        return ['{}:{}'.format(start_path, a) for a in full_path_ff]

    def main(self):
        print(("\n".join(self.get_full_ff_path_with_start_path())))
