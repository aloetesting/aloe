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

from io import StringIO
from aloe.testing import (
    FeatureTest,
    in_directory,
)


@in_directory('tests/simple_app')
class OutputterTest(FeatureTest):
    """
    Test level 3 outputter
    """

    maxDiff = None

    def test_output(self):
        """Test streamed output"""

        with StringIO() as stream:
            self.run_features('features/highlighting.feature',
                              verbosity=3, stream=stream)

            print("--Output--")
            print(stream.getvalue())
            print("--END--")

            # FIXME: where do these right alignments come from?
            self.assertEqual(stream.getvalue(), """
Feature: Scenario indices

  As a programmer
  I want to see my scenarios with pretty highlighting
  So my output is easy to read

  Scenario: First scenario                                                              features/highlighting.feature:9
    Given I have entered 10 into the calculator
    And I press add

  Scenario Outline: Scenario outline with two examples                                  features/highlighting.feature:13
      | number |
      | 30     |

    Given I have entered <number> into the calculator
    And I press add

  Scenario Outline: Scenario outline with two examples                                  features/highlighting.feature:13
      | number |
      | 40     |

    Given I have entered <number> into the calculator
    And I press add

  Scenario: Scenario with table                                                         features/highlighting.feature:22
    Given I press add:
      | value |
      | 1     |
      | 1     |
      | 2     |

----------------------------------------------------------------------
Ran 3 tests in 0.003s

OK
""".lstrip())

    def test_color_output(self):
        """Test streamed output with color"""

        with StringIO() as stream:
            self.run_features('features/highlighting.feature',
                              verbosity=3, stream=stream,
                              force_color=True)

            print("--Output--")
            print(stream.getvalue())
            print("--END--")

            self.assertEqual(stream.getvalue(), """
Feature: Scenario indices

  As a programmer
  I want to see my scenarios with pretty highlighting
  So my output is easy to read

""".lstrip())
