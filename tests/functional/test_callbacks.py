"""
Test callbacks.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()

import operator
from functools import reduce  # pylint:disable=redefined-builtin

from nose.tools import assert_equal

from aloe import world
from aloe.testclass import TestCase
from aloe.testing import (
    FeatureTest,
    in_directory,
)


@in_directory('tests/callbacks_app')
class CallbackTest(FeatureTest):
    """
    Test callbacks functionality.
    """

    @staticmethod
    def name_sequence(names):
        """
        Build a "before-around-after" list.
        """

        return reduce(operator.add, (
            [
                (when, name)
                for when in ('before', 'around', 'after')
            ]
            for name in names
        ))

    def test_step_callbacks(self):
        """
        Test step callbacks execution order.
        """

        self.assert_feature_success('features/step_callbacks.feature')

        self.assertEquals(world.step_names, self.name_sequence([
            'Given I emit a step event of "A"',
            'And I emit a step event of "B"',
            'Then the step event sequence should be "{[A]}{[B]}{["',
        ]))

        # Check step.testclass
        self.assertEquals(len(world.step_testclasses), 3)
        for testclass in world.feature_testclasses:
            self.assertTrue(issubclass(testclass, TestCase))
            self.assertEquals(testclass.__name__, "Step callbacks")

    def test_example_callbacks(self):
        """
        Test example callbacks execution order.
        """

        self.assert_feature_success('features/example_callbacks.feature')

        self.assertEquals(world.example_names, self.name_sequence([
            'Scenario: Example callbacks in a simple scenario, steps=3',
            'Outline: Example callbacks in a scenario with examples ' +
            '(event=C), steps=2',
            'Outline: Example callbacks in a scenario with examples ' +
            '(event=D), steps=2',
            'Scenario: Check the events from previous example, steps=1',
        ]))

    def test_feature_callbacks(self):
        """
        Test feature callbacks execution order and arguments.
        """

        self.assert_feature_success('features/feature_callbacks_1.feature',
                                    'features/feature_callbacks_2.feature')

        names = (
            'Feature callbacks (preparation)',
            'Feature callbacks (test)',
        )

        self.assertEquals(world.feature_names, self.name_sequence(names))

        # Check feature.testclass
        self.assertEquals(len(world.feature_testclasses), 2)
        for feature_name, testclass in zip(names, world.feature_testclasses):
            self.assertTrue(issubclass(testclass, TestCase))
            self.assertEquals(testclass.__name__, feature_name)

    def test_all_callbacks(self):
        """
        Test 'all' callbacks.
        """

        self.assert_feature_success('features/all_callbacks_1.feature',
                                    'features/all_callbacks_2.feature')

        assert_equal(''.join(world.all), '{[ABCD]}')

        # Run all the features; some will fail because they expect only a
        # subset to be run
        self.run_features()
        assert_equal(''.join(world.all), '{[ABCD]}')

    def test_relative_order(self):
        """
        Test the relative order of callbacks - from global to specific.
        """

        self.assert_feature_success('features/all_callbacks_1.feature',
                                    'features/all_callbacks_2.feature')

        def wrap(type_, *inner_event_lists):
            """
            A list of events having before/after (plus around) events wrapped
            around the inner list.
            """

            return (
                'before ' + type_,
                'around_before ' + type_,
            ) + tuple(
                event
                for event_list in inner_event_lists
                for event in event_list
            ) + (
                'around_after ' + type_,
                'after ' + type_,
            )

        self.assertEqual(
            wrap('test', ('inner',)),
            (
                'before test',
                'around_before test',
                'inner',
                'around_after test',
                'after test',
            )
        )

        expected = wrap(
            'all',
            wrap(
                'feature',  # all_callbacks_1
                wrap(
                    'example',
                    wrap('step'),
                ),
                wrap(
                    'example',
                    wrap('step'),
                ),
            ),
            wrap(
                'feature',  # all_callbacks_2
                wrap(
                    'example',
                    wrap('step'),
                ),
                wrap(
                    'example',
                    wrap('step'),
                    wrap('step'),
                ),
            ),
        )

        assert_equal(tuple(world.types), expected)

    def test_behave_as(self):
        """
        Test 'behave_as' called on a step.
        """

        self.assert_feature_success('features/behave_as.feature')

    def test_behave_as_ru(self):
        """
        Test 'behave_as' on a non-English feature.
        """

        self.assert_feature_success('features/behave_as_ru.feature')

    def test_step_failed(self):
        """
        Test the value of step.failed.
        """

        # The test fails
        self.run_features('features/step_failed.feature')

        assert_equal(world.passing_steps, 2)
        assert_equal(world.failed_steps, 1)


@in_directory('tests/multiple_steps_app')
class MultipleDirectoriesCallbackTest(FeatureTest):
    """
    Test before.all callbacks when running features from multiple directories.
    """

    def test_single_app(self):
        """
        Test all the callbacks are called when running a single feature.
        """

        self.assert_feature_success('one/features/check_started.feature')

        self.assertEquals(world.started_callbacks_one, {
            'one': True,
            'two': True,
        })

    def test_multiple_apps(self):
        """
        Test what is loaded and called when running features from multiple
        directories.
        """

        self.assert_feature_success()

        self.assertEquals(world.started_callbacks_one, {
            'one': True,
            'two': True,
        })

        self.assertEquals(world.started_callbacks_two, {
            'one': True,
            'two': True,
        })
