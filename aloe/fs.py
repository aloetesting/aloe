# -*- coding: utf-8 -*-
"""
Filesystem-related utilities.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import os
import sys
import fnmatch
from imp import find_module, load_module, acquire_lock, release_lock

from future.utils import raise_from

from aloe.exceptions import StepDiscoveryError


def path_to_module_name(filename):
    """Convert a path to a file to a Python module name."""

    filename = os.path.relpath(filename)

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


class Importer(object):
    """A cut-down version of Nose importer."""

    # pylint:disable=invalid-name,missing-docstring,redefined-builtin
    # pylint:disable=too-many-branches

    def importFromPath(self, path, fqname):
        """Import a dotted-name package whose tail is at path. In other words,
        given foo.bar and path/to/foo/bar.py, import foo from path/to/foo then
        bar from path/to/foo/bar, returning bar.
        """
        # find the base dir of the package
        path_parts = os.path.normpath(os.path.abspath(path)).split(os.sep)
        name_parts = fqname.split('.')
        if path_parts[-1] == '__init__.py':
            path_parts.pop()
        path_parts = path_parts[:-(len(name_parts))]
        dir_path = os.sep.join(path_parts)
        # then import fqname starting from that dir
        return self.importFromDir(dir_path, fqname)

    def importFromDir(self, dir, fqname):
        """Import a module *only* from path, ignoring sys.path and
        reloading if the version in sys.modules is not the one we want.
        """
        dir = os.path.normpath(os.path.abspath(dir))

        # special case for __main__
        if fqname == '__main__':
            return sys.modules[fqname]

        path = [dir]
        parts = fqname.split('.')
        part_fqname = ''
        mod = parent = fh = None

        for part in parts:
            if part_fqname == '':
                part_fqname = part
            else:
                part_fqname = "%s.%s" % (part_fqname, part)
            try:
                acquire_lock()
                fh, filename, desc = find_module(part, path)
                old = sys.modules.get(part_fqname)
                if old is not None:
                    # test modules frequently have name overlap; make sure
                    # we get a fresh copy of anything we are trying to load
                    # from a new path
                    if self.sameModule(old, filename):
                        mod = old
                    else:
                        del sys.modules[part_fqname]
                        mod = load_module(part_fqname, fh, filename, desc)
                else:
                    mod = load_module(part_fqname, fh, filename, desc)
            finally:
                if fh:
                    fh.close()
                release_lock()
            if parent:
                setattr(parent, part, mod)
            if hasattr(mod, '__path__'):
                path = mod.__path__
            parent = mod
        return mod

    def _dirname_if_file(self, filename):
        # We only take the dirname if we have a path to a non-dir,
        # because taking the dirname of a symlink to a directory does not
        # give the actual directory parent.
        if os.path.isdir(filename):
            return filename
        else:
            return os.path.dirname(filename)

    def sameModule(self, mod, filename):
        mod_paths = []
        if hasattr(mod, '__path__'):
            for path in mod.__path__:
                mod_paths.append(self._dirname_if_file(path))
        elif hasattr(mod, '__file__'):
            mod_paths.append(self._dirname_if_file(mod.__file__))
        else:
            # builtin or other module-like object that
            # doesn't have __file__; must be new
            return False
        new_path = self._dirname_if_file(filename)
        for mod_path in mod_paths:
            if os.path.samefile(mod_path, new_path):
                return True
        return False


class FeatureLoader(object):
    """Loader class responsible for findind features and step
    definitions along a given path on filesystem"""

    importer = Importer()

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
                    cls.importer.importFromPath(filename, module_name)
                except ImportError as exc:
                    raise_from(
                        StepDiscoveryError(
                            "Cannot load step definition file: '%s'" % filename
                        ),
                        exc
                    )

    @classmethod
    def find_feature_directories(cls, dir_):
        """
        Locate directories to load features from.

        The directories must be named 'features'; they must either reside
        directly in the specified directory, or otherwise all their parents
        must be packages (have __init__.py files).
        """

        # A set of package directories discovered
        packages = set()

        for path, dirs, files in os.walk(dir_, followlinks=True):
            # Is this a package?
            if '__init__.py' in files:
                packages.add(path)

            if path == dir_ or path in packages:
                # Does this package have a feature directory?
                if 'features' in dirs:
                    yield os.path.join(path, 'features')

            else:
                # This is not a package, prune search
                dirs[:] = []
