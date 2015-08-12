# Aloe - Cucumber runner for Python based on Lettuce and Nose
# Copyright (C) <2015> Alexey Kotlyarov <a@koterpillar.com>
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
Miscellaneous utilities used internally by Aloe.
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()

import re
import sys
from io import BytesIO, StringIO

try:
    from functools import lru_cache  # pylint:disable=no-name-in-module
except ImportError:
    from repoze.lru import lru_cache
from contextlib import contextmanager


@contextmanager
def dummy_cm():
    """A dummy context manager to compare other decorated functions to."""
    pass


PY3 = sys.version_info >= (3, 0)


def always_str(value):
    """
    Make an str on either Python 2 or Python 3.
    """

    if PY3:
        return value
    else:
        return value.encode()


def str_io():
    """
    A stream that can be written to by Nose.
    """

    if PY3:
        return StringIO()
    else:
        return BytesIO()


def unwrap_function(func):
    """
    Given a function to which a decorator was applied, return the original
    function.
    """

    if hasattr(func, '__wrapped__'):
        return func.__wrapped__

    # In Python 2, functools.wraps doesn't set __wrapped__, however, it is
    # possible to check whether the function has been wrapped by a known
    # method, in this case contextlib.contextmanager
    elif func.__code__.co_filename == dummy_cm.__code__.co_filename and \
            func.__code__.co_firstlineno == dummy_cm.__code__.co_firstlineno:
        # Get the original function from the closure
        return func.__closure__[0].cell_contents

    else:
        return func


RE_CAMEL_CASE = re.compile(r'(((?<=[a-z])[A-Z])|([A-Z](?![A-Z]|$)))')


def camel_case_to_spaces(value):
    """
    Splits CamelCase and converts to lower case. Also strips leading and
    trailing whitespace.
    """
    return RE_CAMEL_CASE.sub(r' \1', value).strip().lower()


class memoizedproperty(object):  # pylint:disable=invalid-name
    """
    A property that is only computed on the first access.
    """

    def __init__(self, func):
        self.func = func
        self.name = func.__name__

    def __get__(self, instance, owner):
        """Compute the value and cache it in the class dict."""

        if instance is None:
            return self

        result = self.func(instance)
        instance.__dict__[self.name] = result
        return result


class memoizedtype(type):  # pylint:disable=invalid-name
    """
    A type that caches the created instances.
    """

    @lru_cache(20)
    def __call__(cls, *args, **kwargs):
        # On Python 2, newsuper can't deal with metaclasses
        return super(memoizedtype, cls).__call__(*args, **kwargs)
