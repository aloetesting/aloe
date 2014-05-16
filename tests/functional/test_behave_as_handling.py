# -*- coding: utf-8 -*-
# <Lettuce - Behaviour Driven Development for python>
# Copyright (C) <2010-2012>  Gabriel Falcão <gabriel@nacaolivre.org>
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
from nose.tools import assert_raises
from os.path import dirname, join, abspath

from lettuce import Runner
import lettuce
from lettuce.core import fs, StepDefinition

from tests.asserts import (
    assert_equals,
    assert_lines_with_traceback,
    capture_output,
)


current_dir = abspath(dirname(__file__))
lettuce_dir = abspath(dirname(lettuce.__file__))
lettuce_path = lambda *x: fs.relpath(join(lettuce_dir, *x))

call_line = StepDefinition.__call__.im_func.func_code.co_firstlineno + 5


def path_to_feature(name):
    return join(abspath(dirname(__file__)), 'behave_as_features', name, "%s.feature" % name)


def test_simple_behave_as_feature():
    """
    Basic step.behave_as behaviour is working
    """

    with capture_output() as (out, _):
        Runner(path_to_feature('1st_normal_steps'), verbosity=3).run()

    assert_equals(out.getvalue(),
        "\n"
        "Feature: Multiplication                            # tests/functional/behave_as_features/1st_normal_steps/1st_normal_steps.feature:2\n"
        "  In order to avoid silly mistakes                 # tests/functional/behave_as_features/1st_normal_steps/1st_normal_steps.feature:3\n"
        "  Cashiers must be able to multiplicate numbers :) # tests/functional/behave_as_features/1st_normal_steps/1st_normal_steps.feature:4\n"
        "\n"
        "  #1 \n"
        "  Scenario: Regular numbers                        # tests/functional/behave_as_features/1st_normal_steps/1st_normal_steps.feature:6\n"
        "    Given I have entered 10 into the calculator    # tests/functional/behave_as_features/1st_normal_steps/simple_step_definitions.py:11\n"
        "    And I have entered 4 into the calculator       # tests/functional/behave_as_features/1st_normal_steps/simple_step_definitions.py:11\n"
        "    When I press multiply                          # tests/functional/behave_as_features/1st_normal_steps/simple_step_definitions.py:15\n"
        "    Then the result should be 40 on the screen     # tests/functional/behave_as_features/1st_normal_steps/simple_step_definitions.py:19\n"
        "\n"
        "  ----------------------------------------------------------------------------\n"
        "\n"
        "  #2 \n"
        "  Scenario: Shorter version of the scenario above  # tests/functional/behave_as_features/1st_normal_steps/1st_normal_steps.feature:12\n"
        "    Given I multiply 10 and 4 into the calculator  # tests/functional/behave_as_features/1st_normal_steps/simple_step_definitions.py:23\n"
        "    Then the result should be 40 on the screen     # tests/functional/behave_as_features/1st_normal_steps/simple_step_definitions.py:19\n"
        "\n"
        "  ----------------------------------------------------------------------------\n"
        "\n"
        "1 feature (1 passed)\n"
        "2 scenarios (2 passed)\n"
        "6 steps (6 passed)\n"
    )

def test_simple_tables_behave_as_feature():
    "Basic step.behave_as behaviour is working"

    with capture_output() as (out, _):
        Runner(path_to_feature('2nd_table_steps'), verbosity=3).run()

    assert_equals(out.getvalue(),
        "\n"
        "Feature: Multiplication                            # tests/functional/behave_as_features/2nd_table_steps/2nd_table_steps.feature:2\n"
        "  In order to avoid silly mistakes                 # tests/functional/behave_as_features/2nd_table_steps/2nd_table_steps.feature:3\n"
        "  Cashiers must be able to multiplicate numbers :) # tests/functional/behave_as_features/2nd_table_steps/2nd_table_steps.feature:4\n"
        "\n"
        "  #1 \n"
        "  Scenario: Regular numbers                        # tests/functional/behave_as_features/2nd_table_steps/2nd_table_steps.feature:6\n"
        "    Given I multiply these numbers:                # tests/functional/behave_as_features/2nd_table_steps/simple_tables_step_definitions.py:31\n"
        "      | number |\n"
        "      | 55     |\n"
        "      | 2      |\n"
        "    Then the result should be 110 on the screen    # tests/functional/behave_as_features/2nd_table_steps/simple_tables_step_definitions.py:19\n"
        "\n"
        "  ----------------------------------------------------------------------------\n"
        "\n"
        "  #2 \n"
        "  Scenario: Shorter version of the scenario above  # tests/functional/behave_as_features/2nd_table_steps/2nd_table_steps.feature:13\n"
        "    Given I multiply 55 and 2 into the calculator  # tests/functional/behave_as_features/2nd_table_steps/simple_tables_step_definitions.py:23\n"
        "    Then the result should be 110 on the screen    # tests/functional/behave_as_features/2nd_table_steps/simple_tables_step_definitions.py:19\n"
        "\n"
        "  ----------------------------------------------------------------------------\n"
        "\n"
        "1 feature (1 passed)\n"
        "2 scenarios (2 passed)\n"
        "4 steps (4 passed)\n"
    )

def test_failing_tables_behave_as_feature():
    "Basic step.behave_as behaviour is working"

    with capture_output() as (out, _):
        assert_raises(
            SystemExit,
            Runner(path_to_feature('3rd_failing_steps'), verbosity=3).run
        )

    assert_lines_with_traceback(out.getvalue(),
    '\n'
    'Feature: Multiplication                            # tests/functional/behave_as_features/3rd_failing_steps/3rd_failing_steps.feature:2\n'
    '  In order to avoid silly mistakes                 # tests/functional/behave_as_features/3rd_failing_steps/3rd_failing_steps.feature:3\n'
    '  Cashiers must be able to multiplicate numbers :) # tests/functional/behave_as_features/3rd_failing_steps/3rd_failing_steps.feature:4\n'
    '\n'
    '  #1 \n'
    '  Scenario: Regular numbers                        # tests/functional/behave_as_features/3rd_failing_steps/3rd_failing_steps.feature:6\n'
    '    Given I have entered 10 into the calculator    # tests/functional/behave_as_features/3rd_failing_steps/failing_step_definitions.py:11\n'
    '    Traceback (most recent call last):\n'
    '      File "%(lettuce_core_file)s", line %(call_line)d, in __call__\n'
    '        ret = self.function(self.step, *args, **kw)\n'
    '      File "%(step_file)s", line 13, in i_have_entered_NUM_into_the_calculator\n'
    '        assert False, \'Die, die, die my darling!\'\n'
    '    AssertionError: Die, die, die my darling!\n'
    '    And I have entered 4 into the calculator       # tests/functional/behave_as_features/3rd_failing_steps/failing_step_definitions.py:11\n'
    '    When I press multiply                          # tests/functional/behave_as_features/3rd_failing_steps/failing_step_definitions.py:16\n'
    '    Then the result should be 40 on the screen     # tests/functional/behave_as_features/3rd_failing_steps/failing_step_definitions.py:20\n'
    '\n'
    '  ----------------------------------------------------------------------------\n'
    '\n'
    '  #2 \n'
    '  Scenario: Shorter version of the scenario above  # tests/functional/behave_as_features/3rd_failing_steps/3rd_failing_steps.feature:12\n'
    '    Given I multiply 10 and 4 into the calculator  # tests/functional/behave_as_features/3rd_failing_steps/failing_step_definitions.py:24\n'
    '    Traceback (most recent call last):\n'
    '      File "%(lettuce_core_file)s", line %(call_line)d, in behave_as\n'
    '        ret = self.function(self.step, *args, **kw)\n'
    '      File "%(step_file)s", line 29, in multiply_X_and_Y_into_the_calculator\n'
    '        \'\'\'.format(x, y))\n'
    '      File "%(lettuce_core_file)s", line 170, in behave_as\n'
    '        step.run()\n'
    '      File "%(lettuce_core_file)s", line 183, in run\n'
    '        step_definition(*groups)\n'
    '      File "%(lettuce_core_file)s", line 58, in __call__\n'
    '        raise e\n'
    '    AssertionError: Die, die, die my darling!\n'
    '    Then the result should be 40 on the screen     # tests/functional/behave_as_features/3rd_failing_steps/failing_step_definitions.py:20\n'
    '\n'
    '  ----------------------------------------------------------------------------\n'
    '\n'
    '1 feature (1 failed)\n'
    '2 scenarios (2 failed)\n'
    '6 steps (4 skipped, 2 failed)\n'
    '\n'
    'List of failed scenarios:\n'
    '\n'
    ' * Feature: Multiplication\n'
    '    - Scenario: Regular numbers\n'
    '      (tests/functional/behave_as_features/3rd_failing_steps/3rd_failing_steps.feature:6)\n'
    '    - Scenario: Shorter version of the scenario above\n'
    '      (tests/functional/behave_as_features/3rd_failing_steps/3rd_failing_steps.feature:12)\n'
    '\n' % {
            'lettuce_core_file': lettuce_path('core.py'),
            'step_file': abspath(lettuce_path('..', 'tests', 'functional', 'behave_as_features', '3rd_failing_steps', 'failing_step_definitions.py')),
            'call_line':call_line,
        }
)
