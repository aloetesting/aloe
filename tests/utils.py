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
Utilities for tests.
"""

from contextlib import contextmanager


def appender(target, *args):
    """
    A function that appends given arguments and its own to the specified
    list.
    """

    def append(*append_args):
        """Append the earlier specified and given arguments to the target."""
        target.append(args + append_args)

    return append


def before_after(before, after):
    """
    A context manager calling given functions before and after the context,
    respectively, with the same arguments as it is given itself.
    """

    @contextmanager
    def around(*args, **kwargs):
        """Call given functions before and after the context."""
        before(*args, **kwargs)
        yield
        after(*args, **kwargs)

    return around
