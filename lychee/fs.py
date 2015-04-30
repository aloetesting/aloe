# -*- coding: utf-8 -*-
# Lychee - Cucumber runner for Python based on Lettuce and Nose
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

# TODO: Remove unused code inherited from Lettuce

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import open
from future import standard_library
standard_library.install_aliases()

import re
import os
import imp
import sys
import codecs
import fnmatch
import zipfile

from functools import wraps
from glob import glob
try:
    reload
except NameError:
    from importlib import reload
from os import walk
from os.path import abspath, join, dirname, curdir


class FeatureLoader(object):
    """Loader class responsible for findind features and step
    definitions along a given path on filesystem"""

    @staticmethod
    def find_steps_dir(feature_file):
        """
        Find the steps directory corresponding to the feature file.

        This is the first directory upwards of the feature file
        containing any Python files.

        If no steps directory can be found, return the filesystem root.
        """

        base_dir = dirname(abspath(feature_file))

        while base_dir != '/':
            files = FileSystem.locate(base_dir, '*.py')
            if files:
                break
            base_dir = dirname(base_dir)

        return base_dir

    @staticmethod
    def find_and_load_step_definitions(steps_dir):
        """
        Load the steps from the specified directory.
        """
        files = FileSystem.locate(steps_dir, '*.py')

        for filename in files:
            root = dirname(filename)
            sys.path.insert(0, root)
            to_load = FileSystem.filename(filename, with_extension=False)
            try:
                module = __import__(to_load)
            except ValueError as e:
                import traceback
                err_msg = traceback.format_exc(e)
                if 'empty module name' in err_msg.lower():
                    continue
                else:
                    e.args = ('{0} when importing {1}'
                              .format(e, filename)),
                    raise e

            reload(module)  # Make sure steps end hooks are registered
            sys.path.remove(root)


class FileSystem(object):
    """File system abstraction, mainly used for indirection, so that
    lettuce can be well unit-tested :)
    """

    @classmethod
    def relpath(cls, path):
        '''Returns the absolute path for the given path.'''
        current_path = abspath(curdir)
        absolute_path = abspath(path)
        return re.sub("^" + re.escape(current_path), '', absolute_path).\
            lstrip("/")

    @classmethod
    def locate(cls, path, match, recursive=True):
        """Locate files recursively in a given path"""
        root_path = abspath(path)
        if recursive:
            return_files = []
            for path, dirs, files in walk(root_path):
                for filename in fnmatch.filter(files, match):
                    return_files.append(join(path, filename))
            return return_files
        else:
            return glob(join(root_path, match))

    @classmethod
    def filename(cls, path, with_extension=True):
        """Returns only the filename from a full path. If the argument
        with_extension is False, return the filename without
        extension.

        Examples::

        >>> from lychee.fs import FileSystem
        >>> path = '/full/path/to/some_file.py'
        >>> assert FileSystem.filename(path) == 'some_file.py'
        >>> assert FileSystem.filename(path, False) == 'some_file'

        """
        fname = os.path.split(path)[1]
        if not with_extension:
            fname = os.path.splitext(fname)[0]

        return fname
