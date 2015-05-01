# Lychee - Cucumber runner for Python based on Lettuce and Nose
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
Steps for testing the basic Gherkin test functionality.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()

from contextlib import contextmanager

from nose.tools import assert_equals, assert_is_instance

from lychee import (
    after,
    around,
    before,
    step,
    world,
)


def record_event(kind, value):
    """
    Record an event of a particular kind. Used for testing the order of
    callback execution.
    """

    kind = kind.replace('"', '')

    if not hasattr(world, kind):
        setattr(world, kind, [])
    events = getattr(world, kind)

    events.append(value)


@before.each_step
def before_step(*args):
    record_event('step', '{')


@around.each_step
@contextmanager
def around_step(*args):
    record_event('step', '[')
    yield
    record_event('step', ']')


@after.each_step
def after_step(*args):
    record_event('step', '}')


@before.each_example
def before_example(*args):
    record_event('example', '{')


@around.each_example
@contextmanager
def around_example(*args):
    record_event('example', '[')
    yield
    record_event('example', ']')


@after.each_example
def after_example(*args):
    record_event('example', '}')


@before.each_feature
def before_feature(feature):
    record_event('feature', '{')
    record_event('feature_names', ('before', feature.name))


@around.each_feature
@contextmanager
def around_feature(feature):
    record_event('feature', '[')
    record_event('feature_names', ('around', feature.name))
    yield
    record_event('feature', ']')


@after.each_feature
def after_feature(feature):
    record_event('feature', '}')
    record_event('feature_names', ('after', feature.name))


@before.all
def before_all():
    record_event('"all"', '{')


@around.all
@contextmanager
def around_all():
    record_event('"all"', '[')
    yield
    record_event('"all"', ']')


@after.all
def after_all():
    record_event('"all"', '}')


@step(r'I emit an? ([^ ]+) event of "([^"]+)"')
def emit_event(self, kind, event):
    record_event(kind, event)


@step(r'The ([^ ]+) event sequence should be "([^"]+)"')
def check_events(self, kind, events):
    kind = kind.replace('"', '')
    assert_equals(''.join(getattr(world, kind)), events)
