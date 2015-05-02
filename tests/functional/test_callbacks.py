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
Test callbacks.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()

import operator
from functools import reduce

from nose.tools import assert_equals

from lychee import world
from . import (
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
        Test feature callbacks execution order.
        """

        self.assert_feature_success('features/feature_callbacks_1.feature',
                                    'features/feature_callbacks_2.feature')

        self.assertEquals(world.feature_names, self.name_sequence([
            'Feature callbacks (preparation)',
            'Feature callbacks (test)',
        ]))

    def test_all_callbacks(self):
        """
        Test 'all' callbacks.
        """

        self.assert_feature_success('features/all_callbacks_1.feature',
                                    'features/all_callbacks_2.feature')

        assert_equals(''.join(world.all), '{[ABCD]}')
