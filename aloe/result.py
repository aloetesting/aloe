# Aloe - Cucumber runner for Python based on Lettuce and Nose
# Copyright (C) <2015> Danielle Madeley <danielle@madeley.id.au>
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
Cucumber-esque outputter for Nose.
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
# pylint:disable=redefined-builtin, unused-wildcard-import, wildcard-import
from builtins import *
# pylint:enable=redefined-builtin, unused-wildcard-import, wildcard-import
from future import standard_library
standard_library.install_aliases()

from contextlib import contextmanager

from aloe.registry import (
    CallbackDecorator,
    CALLBACK_REGISTRY,
    PriorityClass,
)

from nose.result import TextTestResult

# A decorator to add callbacks which wrap the steps looser than all the other
# callbacks.
# pylint:disable=invalid-name
outer_around = CallbackDecorator(CALLBACK_REGISTRY, 'around',
                                 priority_class=PriorityClass.DISPLAY)
# pylint:enable=invalid-name
#

class StreamWrapper(object):
    """Used to decorate file-like objects with a handy 'writeln' method"""
    def __init__(self,stream):
        self.stream = stream

    def __getattr__(self, attr):
        if attr in ('stream', '__getstate__'):
            raise AttributeError(attr)
        return getattr(self.stream,attr)

    def writeln(self, arg=None):
        if not self.stream:
            return

        elif arg:
            self.write(arg)

        self.write('\n') # text-mode streams translate to \r\n if needed

StreamWrapper = StreamWrapper(None)


@outer_around.each_feature
@contextmanager
def feature_wrapper(feature):

    try:
        StreamWrapper.writeln(feature.represented())

        yield
    finally:
        pass


@outer_around.each_example
@contextmanager
def example_wrapper(scenario, outline, steps):
    """Display scenario execution."""

    try:
        StreamWrapper.writeln(scenario.represented())

        yield
    finally:
        pass


@outer_around.each_step
@contextmanager
def step_wrapper(step):
    """Display step execution."""

    try:
        StreamWrapper.writeln(step.represented())
        if step.table:
            StreamWrapper.writeln(step.represent_table())

        yield
    finally:
        pass


class AloeTestResult(TextTestResult):
    def __init__(self, stream, descriptions, verbosity,
                 config=None, errorClasses=None):
        super().__init__(stream, descriptions, verbosity,
                         config=config, errorClasses=errorClasses)
        self.showAll = verbosity == 2
        self.showSteps = verbosity > 2

        if self.showSteps:
            StreamWrapper.stream = stream
