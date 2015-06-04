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

from importlib import import_module
try:
    reload
except NameError:
    # pylint:disable=no-name-in-module,redefined-builtin
    from importlib import reload
    # pylint:enable=no-name-in-module,redefined-builtin
from os.path import join, dirname


class FeatureLoader(object):
    """Loader class responsible for findind features and step
    definitions along a given path on filesystem"""

    @classmethod
    def find_and_load_step_definitions(cls, dir_):
        """
        Load the steps from the specified directory.
        """

        for path, dirs, files in os.walk(dir_):
            for filename in fnmatch.filter(files, '*.py'):
                root = dirname(join(path, filename))
                sys.path.insert(0, root)
                to_load = cls.filename(filename)
                module = import_module(to_load)
                reload(module)  # Make sure steps and hooks are registered
                sys.path.remove(root)

    @classmethod
    def find_feature_directories(cls, dir_):
        """
        Locate directories to load features from.

        The directories must be in a package directory (have '__init__.py' all
        the way up) and be named 'features'.
        """

        for path, dirs, files in os.walk(dir_):
            if '__init__.py' in files and 'features' in dirs:
                yield join(path, 'features')

    @classmethod
    def filename(cls, path):
        """
        Return only the filename from a full path, without extension.
        """
        fname = os.path.split(path)[1]
        fname = os.path.splitext(fname)[0]

        return fname
