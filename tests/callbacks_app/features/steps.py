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

from nose.tools import assert_equal

from aloe import (
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
def before_step(step):
    record_event('step', '{')
    record_event('step_names', ('before', step.sentence))
    record_event('step_testclasses', step.testclass)
    record_event('types', 'before step')


@around.each_step
@contextmanager
def around_step(step):
    record_event('step', '[')
    record_event('step_names', ('around', step.sentence))
    record_event('types', 'around_before step')
    yield
    record_event('types', 'around_after step')
    record_event('step', ']')


@after.each_step
def after_step(step):
    record_event('types', 'after step')
    record_event('step', '}')
    record_event('step_names', ('after', step.sentence))


def record_example_event(when, scenario, outline, steps):
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
    record_event('example', '{')
    record_example_event('before', scenario, outline, steps)
    record_event('types', 'before example')


@around.each_example
@contextmanager
def around_example(scenario, outline, steps):
    record_event('example', '[')
    record_example_event('around', scenario, outline, steps)
    record_event('types', 'around_before example')
    yield
    record_event('types', 'around_after example')
    record_event('example', ']')


@after.each_example
def after_example(scenario, outline, steps):
    record_event('types', 'after example')
    record_event('example', '}')
    record_example_event('after', scenario, outline, steps)


@before.each_feature
def before_feature(feature):
    record_event('feature', '{')
    record_event('feature_names', ('before', feature.name))
    record_event('feature_testclasses', feature.testclass)
    record_event('types', 'before feature')


@around.each_feature
@contextmanager
def around_feature(feature):
    record_event('feature', '[')
    record_event('feature_names', ('around', feature.name))
    record_event('types', 'around_before feature')
    yield
    record_event('types', 'around_after feature')
    record_event('feature', ']')


@after.each_feature
def after_feature(feature):
    record_event('types', 'after feature')
    record_event('feature', '}')
    record_event('feature_names', ('after', feature.name))


@before.all
def before_all():
    record_event('"all"', '{')
    record_event('types', 'before all')


@around.all
@contextmanager
def around_all():
    record_event('"all"', '[')
    record_event('types', 'around_before all')
    yield
    record_event('types', 'around_after all')
    record_event('"all"', ']')


@after.all
def after_all():
    record_event('types', 'after all')
    record_event('"all"', '}')


@step(r'I emit an? ([^ ]+) event of "([^"]+)"')
def emit_event(self, kind, event):
    record_event(kind, event)


@step(r'I emit an? ([^ ]+) event for each letter in "([^"]+)"')
def emit_event_letters(self, kind, letters):
    for letter in letters:
        self.when('I emit a {kind} event of "{letter}"'.format(
            kind=kind,
            letter=letter,
        ))


@step(r'The ([^ ]+) event sequence should be "([^"]+)"')
def check_events(self, kind, events):
    kind = kind.replace('"', '')
    assert_equal(''.join(getattr(world, kind)), events)


@before.each_example
def reset_failures_successes_count(scenario, outline, steps):
    world.passing_steps = 0
    world.failed_steps = 0


@after.each_step
def count_failures_successes(self):
    if self.failed:
        world.failed_steps += 1
    if self.passed:
        world.passing_steps += 1


@step(r'I have a passing step')
def good_step(self):
    pass


@step(r'I have a failing step')
def bad_step(self):
    assert False, "This step is meant to fail."
