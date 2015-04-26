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


@step(r'I emit a step event of "([^"]+)"')
def emit_event(self, event):
    record_event('step', event)


@step(r'The step event sequence should be "([^"]+)"')
def check_events(self, events):
    assert ''.join(world.step) == events
