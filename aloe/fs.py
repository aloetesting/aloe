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


def path_to_module_name(filename):
    """Convert a path to a file to a Python module name."""

    dotted_path = []
    while True:
        filename, component = os.path.split(filename)
        dotted_path.insert(0, component)
        if filename == '':
            break

    dotted_path[-1] = os.path.splitext(dotted_path[-1])[0]
    if dotted_path[-1] == '__init__':
        dotted_path.pop()

    return '.'.join(dotted_path)


class FeatureLoader(object):
    """Loader class responsible for findind features and step
    definitions along a given path on filesystem"""

    @classmethod
    def find_and_load_step_definitions(cls, dir_):
        """
        Load the steps from the specified directory.
        """

        for path, _, files in os.walk(dir_):
            for filename in fnmatch.filter(files, '*.py'):
                # Import the module using its fully qualified name
                filename = os.path.relpath(os.path.join(path, filename))
                module_name = path_to_module_name(filename)

                try:
                    module = import_module(module_name)
                except (ImportError, TypeError) as exc:
                    import pdb; pdb.set_trace()
                    raise
                reload(module)  # Make sure steps and hooks are registered

    @classmethod
    def find_feature_directories(cls, dir_):
        """
        Locate directories to load features from.

        The directories must be in a package directory (have '__init__.py' all
        the way up) and be named 'features'.
        """

        # A set of package directories discovered
        packages = set(dir_)

        for path, dirs, files in os.walk(dir_):
            # Is this a package?
            if '__init__.py' in files:
                packages.add(path)

            if path in packages:
                # Does this package have a feature directory?
                if 'features' in dirs:
                    yield os.path.join(path, 'features')

            else:
                # This is not a package, prune search
                dirs[:] = []
