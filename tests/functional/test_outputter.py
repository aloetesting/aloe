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
Test level 3 outputter
"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
# pylint:disable=redefined-builtin, unused-wildcard-import, wildcard-import
from builtins import *
# pylint:enable=redefined-builtin, unused-wildcard-import, wildcard-import
from future import standard_library
standard_library.install_aliases()

from unittest.mock import patch

from io import StringIO
from aloe.testing import (
    FeatureTest,
    in_directory,
)


class TermElement(object):
    def __init__(self, attr):
        self.attr = attr

    def __call__(self, s):
        # strips the string to make the output easier to read
        return 't.{attr}({s})'.format(attr=self.attr, s=s.strip())

    def __str__(self):
        return '<t.{attr}>'.format(attr=self.attr)

    def __mul__(self, other):
        return str(self) * other


class MockTerminal(object):

    def __init__(self, stream, force_styling=None):
        self.stream = stream
        self.does_styling = True

    def __getattr__(self, attr):
        if attr in ('stream',
                    'does_styling',
                    '__getstate__'):
            raise AttributeError(attr)

        # callable factory
        return TermElement(attr)

    def color(self, color):

        return getattr(self, 'color%s' % color)


@in_directory('tests/simple_app')
class OutputterTest(FeatureTest):
    """
    Test level 3 outputter
    """

    maxDiff = None

    def test_output(self):
        """Test streamed output"""

        with \
                StringIO() as stream, \
                patch('aloe.result.AloeTestResult.printSummary'):
            self.run_features('features/highlighting.feature',
                              verbosity=3, stream=stream)

            print("--Output--")
            print(stream.getvalue())
            print("--END--")

            self.assertEqual(stream.getvalue(), """
Feature: Scenario indices

  As a programmer
  I want to see my scenarios with pretty highlighting
  So my output is easy to read

  Scenario: First scenario                              features/highlighting.feature:9
    Given I have entered 10 into the calculator
    And I press add

  Scenario Outline: Scenario outline with two examples  features/highlighting.feature:13
      | number |
      | 30     |

    Given I have entered <number> into the calculator
    And I press add

  Scenario Outline: Scenario outline with two examples  features/highlighting.feature:13
      | number |
      | 40     |

    Given I have entered <number> into the calculator
    And I press add

  Scenario: Scenario with table                         features/highlighting.feature:22
    Given I press add:
      | value |
      | 1     |
      | 1     |
      | 2     |

""".lstrip())

    def test_color_output(self):
        """Test streamed output with color"""

        with \
                patch('aloe.result.Terminal', new=MockTerminal), \
                patch('aloe.result.AloeTestResult.printSummary'), \
                StringIO() as stream:
            self.run_features('features/highlighting.feature',
                              verbosity=3, stream=stream,
                              force_color=True)

            print("--Output--")
            print(stream.getvalue())
            print("--END--")

            self.assertEqual(stream.getvalue(), """
t.bold_white(Feature: Scenario indices)

t.white(As a programmer
  I want to see my scenarios with pretty highlighting
  So my output is easy to read)

t.bold_white(Scenario: First scenario)t.color8(features/highlighting.feature:9)
t.color8(Given I have entered 10 into the calculator
    And I press add)
<t.move_up><t.move_up>t.color11(Given I have entered 10 into the calculator)
<t.move_up>t.bold_green(Given I have entered 10 into the calculator)
t.color11(And I press add)
<t.move_up>t.bold_green(And I press add)

t.bold_white(Scenario Outline: Scenario outline with two examples)t.color8(features/highlighting.feature:13)
      | t.white(number) |
      | t.white(30) |

t.color8(Given I have entered <number> into the calculator
    And I press add)
<t.move_up><t.move_up>t.color11(Given I have entered <number> into the calculator)
<t.move_up>t.bold_green(Given I have entered <number> into the calculator)
t.color11(And I press add)
<t.move_up>t.bold_green(And I press add)

t.bold_white(Scenario Outline: Scenario outline with two examples)t.color8(features/highlighting.feature:13)
      | t.white(number) |
      | t.white(40) |

t.color8(Given I have entered <number> into the calculator
    And I press add)
<t.move_up><t.move_up>t.color11(Given I have entered <number> into the calculator)
<t.move_up>t.bold_green(Given I have entered <number> into the calculator)
t.color11(And I press add)
<t.move_up>t.bold_green(And I press add)

t.bold_white(Scenario: Scenario with table)t.color8(features/highlighting.feature:22)
t.color8(Given I press add:
      | value |
      | 1     |
      | 1     |
      | 2     |)
<t.move_up><t.move_up><t.move_up><t.move_up><t.move_up>t.color11(Given I press add:)
      | t.color11(value) |
      | t.color11(1) |
      | t.color11(1) |
      | t.color11(2) |
<t.move_up><t.move_up><t.move_up><t.move_up><t.move_up>t.bold_green(Given I press add:)
      | t.bold_green(value) |
      | t.bold_green(1) |
      | t.bold_green(1) |
      | t.bold_green(2) |

""".lstrip())
