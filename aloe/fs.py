# -*- coding: utf-8 -*-
# Aloe - Cucumber runner for Python based on Lettuce and Nose
# Copyright (C) <2010-2012>  Gabriel Falcão <gabriel@nacaolivre.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Filesystem-related utilities.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()

import os
import sys
import fnmatch

from glob import glob
from importlib import import_module
try:
    reload
except NameError:
    # pylint:disable=no-name-in-module,redefined-builtin
    from importlib import reload
    # pylint:enable=no-name-in-module,redefined-builtin
from os import walk
from os.path import abspath, join, dirname


class FeatureLoader(object):
    """Loader class responsible for findind features and step
    definitions along a given path on filesystem"""

    @classmethod
    def find_steps_dir(cls, feature_file):
        """
        Find the steps directory corresponding to the feature file.

        This is the first directory upwards of the feature file
        containing any Python files.

        If no steps directory can be found, return the filesystem root.
        """

        base_dir = dirname(abspath(feature_file))

        while base_dir != '/':
            files = cls.locate(base_dir, '*.py')
            if files:
                break
            base_dir = abspath(join(base_dir, '..'))

        return base_dir

    @classmethod
    def find_and_load_step_definitions(cls, steps_dir):
        """
        Load the steps from the specified directory.
        """
        files = cls.locate(steps_dir, '*.py')

        for filename in files:
            root = dirname(filename)
            sys.path.insert(0, root)
            to_load = cls.filename(filename)
            module = import_module(to_load)
            reload(module)  # Make sure steps and hooks are registered
            sys.path.remove(root)

    @staticmethod
    def locate(root_path, match, recursive=True):
        """Locate files recursively in a given path"""
        if recursive:
            return_files = []
            for path, _, files in walk(root_path):
                for filename in fnmatch.filter(files, match):
                    return_files.append(join(path, filename))
            return return_files
        else:
            return glob(join(root_path, match))

    @classmethod
    def filename(cls, path):
        """
        Return only the filename from a full path, without extension.
        """
        fname = os.path.split(path)[1]
        fname = os.path.splitext(fname)[0]

        return fname
