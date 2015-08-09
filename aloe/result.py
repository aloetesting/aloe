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
from aloe.strings import represent_table
from blessings import Terminal
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
    def __init__(self, stream):
        self.stream = stream

    def __getattr__(self, attr):
        if attr in ('stream', '__getstate__'):
            raise AttributeError(attr)
        return getattr(self.stream,attr)

    def write(self, arg=None, return_=False):
        if not self.stream:
            return

        elif arg:
            self.stream.write(arg)

            if return_:
                self.stream.write(term.move_up * arg.count('\n'))

    def writeln(self, arg=None, return_=False):
        if arg:
            self.write(arg, return_=return_)

        self.write('\n') # text-mode streams translate to \r\n if needed

        if return_:
            self.write(term.move_up)


StreamWrapper = StreamWrapper(None)
term = Terminal()


@outer_around.each_feature
@contextmanager
def feature_wrapper(feature):

    try:
        if feature.tags:
            StreamWrapper.writeln(term.cyan(feature.represent_tags()))

        lines = feature.represented(annotate=False).splitlines()
        StreamWrapper.writeln(term.bold_white(lines[0]))
        StreamWrapper.writeln()
        StreamWrapper.writeln(term.white('\n'.join(lines[1:])))
        StreamWrapper.writeln()

        yield
    finally:
        pass


@outer_around.each_example
@contextmanager
def example_wrapper(scenario, outline, steps):
    """Display scenario execution."""

    try:
        if scenario.tags:
            StreamWrapper.writeln(term.cyan(scenario.represent_tags()))

        # blessings doesn't degrade term.color nicely if there's no styling
        # available
        gray = term.color(8) if term.does_styling else str

        start, end = scenario.represented().rsplit('#')
        StreamWrapper.write(term.bold_white(start))
        StreamWrapper.writeln(gray(end))

        if outline:
            StreamWrapper.writeln(represent_table([outline.keys(),
                                                   outline.values()],
                                                  indent=6,
                                                  cell_wrap=term.white))
            StreamWrapper.writeln()

        # write a preview of the steps
        if term.does_styling:
            StreamWrapper.writeln(
                gray('\n'.join(
                    step.represented(annotate=False)
                    for step in steps
                ) + '\n'),
                return_=True
            )

        yield
    finally:
        StreamWrapper.writeln()


@outer_around.each_step
@contextmanager
def step_wrapper(step):
    """Display step execution."""

    try:
        if term.does_styling:
            StreamWrapper.writeln(
                step.represented(annotate=False, color=term.color(11)),
                return_=True)

        yield
    finally:
        if step.passed:
            color = term.bold_green
        elif step.failed:
            color = term.bold_red
        else:
            color = term.yellow

        StreamWrapper.writeln(
            step.represented(annotate=False, color=color)
        )


class AloeTestResult(TextTestResult):
    def __init__(self, stream, descriptions, verbosity,
                 config=None, errorClasses=None):
        super().__init__(stream, descriptions, verbosity,
                         config=config, errorClasses=errorClasses)
        self.showAll = verbosity == 2
        self.showSteps = verbosity >= 3

        StreamWrapper.stream = stream if self.showSteps else None
