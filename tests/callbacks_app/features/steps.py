# -*- coding: utf-8 -*-
"""
Steps for testing the basic Gherkin test functionality.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
# pylint:disable=redefined-builtin
from builtins import super
# pylint:enable=redefined-builtin

from contextlib import contextmanager

from nose.tools import assert_equal

from aloe import (
    after,
    around,
    before,
    step,
    world,
)
from aloe.testclass import TestCase


class CallbackTestCase(TestCase):  # pylint:disable=abstract-method
    """Base for Gherkin test cases recording the use of setUp()/tearDown()."""

    def setUp(self):
        """Emit a 'setUp' event."""

        super().setUp()
        record_event('testclass', '[')

    def tearDown(self):
        """Emit a 'tearDown' event."""

        record_event('testclass', ']')
        super().tearDown()


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
def before_step(self):
    """Record the "before step" event."""
    record_event('step', '{')
    record_event('step_names', ('before', self.sentence))
    record_event('step_testclasses', self.testclass)
    record_event('step_tests', self.test)
    record_event('types', 'before step')


@around.each_step
@contextmanager
def around_step(self):
    """Record the "around step" event."""
    record_event('step', '[')
    record_event('step_names', ('around', self.sentence))
    record_event('types', 'around_before step')
    yield
    record_event('types', 'around_after step')
    record_event('step', ']')


@after.each_step
def after_step(self):
    """Record the "after step" event."""
    record_event('types', 'after step')
    record_event('step', '}')
    record_event('step_names', ('after', self.sentence))


def record_example_event(when, scenario, outline, steps):
    """Record a scenario- or scenario outline-level event."""
    if outline:
        result = "Outline: " + scenario.name
        result += ' (' + \
            ', '.join('='.join((k, v)) for k, v in outline.items()) + \
            ')'
    else:
        result = "Scenario: " + scenario.name

    result += ", steps={}".format(len(steps))
    record_event('example_names', (when, result))


@before.each_example
def before_example(scenario, outline, steps):
    """Record the "before example" event."""
    record_event('example', '{')
    record_example_event('before', scenario, outline, steps)
    record_event('types', 'before example')


@around.each_example
@contextmanager
def around_example(scenario, outline, steps):
    """Record the "around example" event."""
    record_event('example', '[')
    record_example_event('around', scenario, outline, steps)
    record_event('types', 'around_before example')
    yield
    record_event('types', 'around_after example')
    record_event('example', ']')


@after.each_example
def after_example(scenario, outline, steps):
    """Record the "after example" event."""
    record_event('types', 'after example')
    record_event('example', '}')
    record_example_event('after', scenario, outline, steps)


@before.each_feature
def before_feature(feature):
    """Record the "before feature" event."""
    record_event('feature', '{')
    record_event('feature_names', ('before', feature.name))
    record_event('feature_testclasses', feature.testclass)
    record_event('types', 'before feature')


@around.each_feature
@contextmanager
def around_feature(feature):
    """Record the "around feature" event."""
    record_event('feature', '[')
    record_event('feature_names', ('around', feature.name))
    record_event('types', 'around_before feature')
    yield
    record_event('types', 'around_after feature')
    record_event('feature', ']')


@after.each_feature
def after_feature(feature):
    """Record the "after feature" event."""
    record_event('types', 'after feature')
    record_event('feature', '}')
    record_event('feature_names', ('after', feature.name))


@before.all
def before_all():
    """Record the "before all" event."""
    record_event('"all"', '{')
    record_event('types', 'before all')


@around.all
@contextmanager
def around_all():
    """Record the "around all" event."""
    record_event('"all"', '[')
    record_event('types', 'around_before all')
    yield
    record_event('types', 'around_after all')
    record_event('"all"', ']')


@after.all
def after_all():
    """Record the "after all" event."""
    record_event('types', 'after all')
    record_event('"all"', '}')


@step(r'I emit an? ([^ ]+) event of "([^"]+)"')
@step(r'Я записываю событие ([^ ]+) "([^"]+)"')
def emit_event(self, kind, event):
    """Record a user-defined event."""
    record_event(kind, event)


@step(r'I emit an? ([^ ]+) event for each letter in "([^"]+)"')
def emit_event_letters(self, kind, letters):
    """
    Record several user-defined events in succession.

    Used to test behave_as.
    """

    for letter in letters:
        self.when('I emit a {kind} event of "{letter}"'.format(
            kind=kind,
            letter=letter,
        ))


@step(r'Я записываю событие ([^ ]+) для каждой буквы в "([^"]+)"')
def emit_event_letters_ru(self, kind, letters):
    """
    Record several user-defined events in succession, using the Russian step
    definition.

    Used to test behave_as.
    """

    for letter in letters:
        self.when('Я записываю событие {kind} "{letter}"'.format(
            kind=kind,
            letter=letter,
        ))


@step(r'The ([^ ]+) event sequence should be "([^"]+)"')
@step(r'Последовательность событий ([^ ]+) должна быть "([^"]+)"')
def check_events(self, kind, events):
    """Check the recorded events of a particular type."""
    kind = kind.replace('"', '')
    assert_equal(''.join(getattr(world, kind)), events)


@after.each_step
def count_failures_successes(self):
    """Count the number of passed and failed steps."""
    if self.failed:
        world.failed_steps += 1
    if self.passed:
        world.passing_steps += 1


@before.each_example
def reset_failures_successes_count(scenario, outline, steps):
    """Reset the passed/failed step count for each scenario."""
    world.passing_steps = 0
    world.failed_steps = 0


@step(r'I have a passing step')
def good_step(self):
    """A step that always passes."""
    pass


@step(r'I have a failing step')
def bad_step(self):
    """A step that always fails."""
    assert False, "This step is meant to fail."
