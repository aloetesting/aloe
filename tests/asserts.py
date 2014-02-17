# -*- coding: utf-8 -*-
# <Lettuce - Behaviour Driven Development for python>
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
import re
import sys
from difflib import ndiff
from itertools import tee, izip_longest
# Important: cannot use cStringIO because it does not support unicode!
from StringIO import StringIO

from blessings import Terminal
from lettuce import registry


term = Terminal()


real_stdout = sys.stdout
real_stderr = sys.stderr


def prepare_stdout():
    registry.clear()
    if isinstance(sys.stdout, StringIO):
        del sys.stdout
    std = StringIO()
    sys.stdout = std


def prepare_stderr():
    registry.clear()
    if isinstance(sys.stderr, StringIO):
        del sys.stderr
    std = StringIO()
    sys.stderr = std


def yield_transitions(iterable):
    """
    Yield the tuples of (index, value) indicating the transitions in the
    iterable
    """

    register = None
    last_index = 0

    for i, elem in enumerate(iterable):
        if elem != register:
            if register:
                yield (last_index, i, register)

            register = elem
            last_index = i

    yield (last_index, i + 1, register)


def assert_equals(original, expected, stream=real_stdout):
    """
    A new version of assert_equals that does coloured differences
    """

    try:
        # replace \s with space, this makes literal trailing space visible
        # in the expected results
        expected = expected.replace('\s', ' ')
    except AttributeError:
        pass

    try:
        assert original == expected
    except AssertionError:
        diff = ndiff(expected.splitlines(), original.splitlines())

        # consider each line along with it's next line
        #
        # if the next line is a '? ' line we combine this into the line to
        # indicate where the change has occured
        first_line, second_line = tee(diff)
        next(second_line)  # consume a line from this generator

        for line, next_line in izip_longest(first_line, second_line,
                                            fillvalue=None):

            code, line = line[:2], line[2:]
            if next_line:
                next_code, next_line = next_line[:2], next_line[2:]
            else:
                next_code = ''

            # we don't render '? ' lines, only combine their results in
            if code == '? ':
                continue

            unchanged, changed = {
                '+ ': (term.green, term.black_on_green),
                '- ': (term.red, term.black_on_red),
            }.get(code, (term.white, term.white))

            if next_code == '? ':
                # combine the next line
                # make sure the lines are the same length
                next_line = next_line.ljust(len(line))
                line = u''.join(changed(line[i1:i2]) if char == '+'
                                else unchanged(line[i1:i2])
                                for (i1, i2, char)
                                in yield_transitions(next_line))
            else:
                line = unchanged(line)

            print >> stream, unchanged(code) + line

        raise


def assert_lines(original, expected):
    assert_equals(original, expected)


def assert_lines_unicode(original, expected):
    assert_equals(original, expected)


def assert_lines_with_traceback(one, other):
    lines_one = one.splitlines()
    lines_other = other.splitlines()
    regex = re.compile('File "([^"]+)", line \d+, in.*')

    error = '%r should be in traceback line %r.\nFull output was:\n' + one
    for line1, line2 in zip(lines_one, lines_other):
        if regex.search(line1) and regex.search(line2):
            found = regex.search(line2)

            filename = found.group(1)
            params = filename, line1
            assert filename in line1, error % params

        else:
            assert_equals(line1, line2)


def assert_unicode_equals(original, expected):
    assert_equals(original, expected)


def assert_stderr(expected):
    string = sys.stderr.getvalue()
    assert_equals(string, expected)


def assert_stdout(expected):
    string = sys.stdout.getvalue()
    assert_equals(string, expected)


def assert_stdout_lines(other):
    real_stdout.write(sys.stdout.getvalue())

    assert_equals(sys.stdout.getvalue(), other)


def assert_stderr_lines(other):
    assert_equals(sys.stderr.getvalue(), other)


def assert_stdout_lines_with_traceback(other):
    assert_lines_with_traceback(sys.stdout.getvalue(), other)


def assert_stderr_lines_with_traceback(other):
    assert_lines_with_traceback(sys.stderr.getvalue(), other)
