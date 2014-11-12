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
import os
import random
from inspect import currentframe
from os.path import dirname, join, abspath
from StringIO import StringIO

from mock import Mock, patch
from sure import expect

from nose.tools import with_setup, assert_raises

import lettuce
from lettuce.fs import FeatureLoader
from lettuce.core import Feature, fs, StepDefinition
from lettuce.registry import STEP_REGISTRY
from lettuce.terrain import world
from lettuce.registry import preserve_registry
from lettuce import Runner

from tests.asserts import (
    assert_equals,
    assert_lines_with_traceback,
    capture_output,
)

current_dir = abspath(dirname(__file__))
lettuce_dir = abspath(dirname(lettuce.__file__))
ojoin = lambda *x: join(current_dir, 'output_features', *x)
sjoin = lambda *x: join(current_dir, 'syntax_features', *x)
tjoin = lambda *x: join(current_dir, 'tag_features', *x)
bjoin = lambda *x: join(current_dir, 'bg_features', *x)

lettuce_path = lambda *x: fs.relpath(join(lettuce_dir, *x))

call_line = StepDefinition.__call__.im_func.func_code.co_firstlineno + 6


def joiner(callback, name):
    return callback(name, "%s.feature" % name)


feature_name = lambda name: joiner(ojoin, name)
syntax_feature_name = lambda name: joiner(sjoin, name)
tag_feature_name = lambda name: joiner(tjoin, name)
bg_feature_name = lambda name: joiner(bjoin, name)


def test_try_to_import_terrain():
    "Runner tries to import terrain, but has a nice output when it fail"
    sandbox_path = ojoin('..', 'sandbox')
    original_path = abspath(".")
    os.chdir(sandbox_path)

    try:
        with capture_output() as (_, err):
            import lettuce
            reload(lettuce)
            raise AssertionError('The runner should raise ImportError !')
    except SystemExit:
        assert_lines_with_traceback(
            err.getvalue(),
            'Lettuce has tried to load the conventional environment module '
            '"terrain"\nbut it has errors, check its contents and '
            'try to run lettuce again.\n\nOriginal traceback below:\n\n'
            "Traceback (most recent call last):\n"
            '  File "%(lettuce_core_file)s", line 44, in <module>\n'
            '    terrain = fs.FileSystem._import("terrain")\n'
            '  File "%(lettuce_fs_file)s", line 63, in _import\n'
            '    module = imp.load_module(name, fp, pathname, description)\n'
            '  File "%(terrain_file)s", line 18\n'
            '    it is here just to cause a syntax error\n'
            "                  ^\n"
            'SyntaxError: invalid syntax\n' % {
                'lettuce_core_file': abspath(join(lettuce_dir, '__init__.py')),
                'lettuce_fs_file': abspath(join(lettuce_dir, 'fs.py')),
                'terrain_file': abspath(lettuce_path('..', 'tests', 'functional', 'sandbox', 'terrain.py')),
            }
        )

    finally:
        os.chdir(original_path)


def test_feature_representation_without_colors():
    "Feature represented without colors"
    feature_file = ojoin('..', 'simple_features', '1st_feature_dir', 'some.feature')

    feature = Feature.from_file(feature_file)
    assert_equals(
        feature.represented(),
        "Feature: Addition                                      # tests/functional/simple_features/1st_feature_dir/some.feature:5\n"
        "  In order to avoid silly mistakes                     # tests/functional/simple_features/1st_feature_dir/some.feature:6\n"
        "  As a math idiot                                      # tests/functional/simple_features/1st_feature_dir/some.feature:7\n"
        "  I want to be told the sum of two numbers             # tests/functional/simple_features/1st_feature_dir/some.feature:8"
    )


def test_scenario_outline_representation_without_colors():
    "Scenario Outline represented without colors"
    feature_file = ojoin('..', 'simple_features', '1st_feature_dir', 'some.feature')

    feature = Feature.from_file(feature_file)
    assert_equals(
        feature.scenarios[0].represented(),
        "  Scenario Outline: Add two numbers                    # tests/functional/simple_features/1st_feature_dir/some.feature:10"
    )


def test_scenario_representation_without_colors():
    "Scenario represented without colors"
    feature_file = ojoin('runner_features', 'first.feature')

    feature = Feature.from_file(feature_file)
    assert_equals(
        feature.scenarios[0].represented(),
        "  Scenario: Do nothing                   # tests/functional/output_features/runner_features/first.feature:6"
    )


def test_undefined_step_represent_string():
    """
    Undefined step represented without colors
    """

    feature_file = ojoin('runner_features', 'first.feature')

    feature = Feature.from_file(feature_file)
    step = feature.scenarios[0].steps[0]
    assert_equals(
        step.represented(),
        "    Given I do nothing                   # tests/functional/output_features/runner_features/first.feature:7 (undefined)"
    )


def test_defined_step_represent_string():
    """Defined step represented without colors"""

    feature_file = ojoin('runner_features', 'first.feature')
    feature_dir = ojoin('runner_features')
    loader = FeatureLoader(feature_dir)
    world._output = StringIO()
    world._is_colored = False
    loader.find_and_load_step_definitions()

    feature = Feature.from_file(feature_file)
    step = feature.scenarios[0].steps[0]
    step.run()

    assert_equals(
        step.represented(),
        "    Given I do nothing                   # tests/functional/output_features/runner_features/dumb_steps.py:6"
    )


def test_output_with_success_colorless2():
    "Testing the colorless output of a successful feature"

    with capture_output() as (out, err):
        runner = Runner(join(abspath(dirname(__file__)),
                             'output_features', 'runner_features'),
                        verbosity=3)
        runner.run()

    assert_equals(out.getvalue(),
        u'\n'
        u'Feature: Dumb feature                    # tests/functional/output_features/runner_features/first.feature:1\n'
        u'  In order to test success               # tests/functional/output_features/runner_features/first.feature:2\n'
        u'  As a programmer                        # tests/functional/output_features/runner_features/first.feature:3\n'
        u'  I want to see that the output is green # tests/functional/output_features/runner_features/first.feature:4\n'
        u'\n'
        u'  #1\n'
        u'  Scenario: Do nothing                   # tests/functional/output_features/runner_features/first.feature:6\n'
        u'    Given I do nothing                   # tests/functional/output_features/runner_features/dumb_steps.py:6\n'
        u'\n'
        u'  ----------------------------------------------------------------------------\n'
        u'\n'
        u'1 feature (1 passed)\n'
        u'1 scenario (1 passed)\n'
        u'1 step (1 passed)\n'
    )


def test_output_with_success_colorless():
    "A feature with two scenarios should separate the two scenarios with a new line (in colorless mode)."

    with capture_output() as (out, err):
        runner = Runner(join(abspath(dirname(__file__)),
                             'output_features', 'many_successful_scenarios'),
                        verbosity=3)
        runner.run()

    assert_equals(out.getvalue(),
        "\n"
        "Feature: Dumb feature                    # tests/functional/output_features/many_successful_scenarios/first.feature:1\n"
        "  In order to test success               # tests/functional/output_features/many_successful_scenarios/first.feature:2\n"
        "  As a programmer                        # tests/functional/output_features/many_successful_scenarios/first.feature:3\n"
        "  I want to see that the output is green # tests/functional/output_features/many_successful_scenarios/first.feature:4\n"
        "\n"
        "  #1\n"
        "  Scenario: Do nothing                   # tests/functional/output_features/many_successful_scenarios/first.feature:6\n"
        "    Given I do nothing                   # tests/functional/output_features/many_successful_scenarios/dumb_steps.py:6\n"
        "\n"
        "  ----------------------------------------------------------------------------\n"
        "\n"
        "  #2\n"
        "  Scenario: Do nothing (again)           # tests/functional/output_features/many_successful_scenarios/first.feature:9\n"
        "    Given I do nothing (again)           # tests/functional/output_features/many_successful_scenarios/dumb_steps.py:6\n"
        "\n"
        "  ----------------------------------------------------------------------------\n"
        "\n"
        "1 feature (1 passed)\n"
        "2 scenarios (2 passed)\n"
        "2 steps (2 passed)\n"
    )


def test_output_with_success_colorless_many_features():
    """Testing the output of many successful features"""

    with capture_output() as (out, err):
        runner = Runner(join(abspath(dirname(__file__)),
                             'output_features', 'many_successful_features'),
                        verbosity=3)
        runner.run()

    assert_equals(out.getvalue(),
        "\n"
        "Feature: First feature, of many              # tests/functional/output_features/many_successful_features/one.feature:1\n"
        "  In order to make lettuce more robust       # tests/functional/output_features/many_successful_features/one.feature:2\n"
        "  As a programmer                            # tests/functional/output_features/many_successful_features/one.feature:3\n"
        "  I want to test its output on many features # tests/functional/output_features/many_successful_features/one.feature:4\n"
        "\n"
        "  #1\n"
        "  Scenario: Do nothing                       # tests/functional/output_features/many_successful_features/one.feature:6\n"
        "    Given I do nothing                       # tests/functional/output_features/many_successful_features/dumb_steps.py:6\n"
        "    Then I see that the test passes          # tests/functional/output_features/many_successful_features/dumb_steps.py:8\n"
        "\n"
        "  ----------------------------------------------------------------------------\n"
        "\n"
        "Feature: Second feature, of many    # tests/functional/output_features/many_successful_features/two.feature:1\n"
        "  I just want to see it green :)    # tests/functional/output_features/many_successful_features/two.feature:2\n"
        "\n"
        "  #1\n"
        "  Scenario: Do nothing              # tests/functional/output_features/many_successful_features/two.feature:4\n"
        "    Given I do nothing              # tests/functional/output_features/many_successful_features/dumb_steps.py:6\n"
        "    Then I see that the test passes # tests/functional/output_features/many_successful_features/dumb_steps.py:8\n"
        "\n"
        "  ----------------------------------------------------------------------------\n"
        "\n"
        "2 features (2 passed)\n"
        "2 scenarios (2 passed)\n"
        "4 steps (4 passed)\n"
    )


def test_output_when_could_not_find_features_colorless():
    """Testing the colorful output of many successful features colorless"""

    path = fs.relpath(join(abspath(dirname(__file__)), 'no_features',
                           'unexistent-folder'))

    with capture_output() as (out, err):
        runner = Runner(path, verbosity=3)
        runner.run()

    assert_equals(out.getvalue(),
        'Oops!\n'
        'Could not find features at ./%s\n' % path
    )


def test_output_when_could_not_find_features_verbosity_level_2():
    """Testing the colorful output of many successful features verbosity 2"""

    path = fs.relpath(join(abspath(dirname(__file__)),
                           'no_features', 'unexistent-folder'))

    with capture_output() as (out, err):
        runner = Runner(path, verbosity=2)
        runner.run()

    assert_equals(out.getvalue(),
        'Oops!\n'
        'Could not find features at ./%s\n' % path
    )


def test_output_with_success_colorless_with_table():
    """Testing the colorless output of success with table"""

    with capture_output() as (out, err):
        runner = Runner(feature_name('success_table'), verbosity=3)
        runner.run()

    assert_equals(out.getvalue(),
        u'\n'
        u'Feature: Table Success           # tests/functional/output_features/success_table/success_table.feature:1\n'
        u'\n'
        u'  #1\n'
        u'  Scenario: Add two numbers ♥    # tests/functional/output_features/success_table/success_table.feature:2\n'
        u'    Given I have 0 bucks         # tests/functional/output_features/success_table/success_table_steps.py:28\n'
        u'    And that I have these items: # tests/functional/output_features/success_table/success_table_steps.py:32\n'
        u'      | name    | price  |\n'
        u'      | Porsche | 200000 |\n'
        u'      | Ferrari | 400000 |\n'
        u'    When I sell the "Ferrari"    # tests/functional/output_features/success_table/success_table_steps.py:42\n'
        u'    Then I have 400000 bucks     # tests/functional/output_features/success_table/success_table_steps.py:28\n'
        u'    And my garage contains:      # tests/functional/output_features/success_table/success_table_steps.py:47\n'
        u'      | name    | price  |\n'
        u'      | Porsche | 200000 |\n'
        u'\n'
        u'  ----------------------------------------------------------------------------\n'
        u'\n'
        u'1 feature (1 passed)\n'
        u'1 scenario (1 passed)\n'
        u'5 steps (5 passed)\n'
    )


def test_output_with_failed_colorless_with_table():
    "Testing the colorless output of failed with table"

    with capture_output() as (out, err):
        runner = Runner(feature_name('failed_table'), verbosity=3)
        assert_raises(SystemExit, runner.run)

    assert_equals(out.getvalue(),
        ("\n"
        "Feature: Table Fail                           # tests/functional/output_features/failed_table/failed_table.feature:1\n"
        "\n"
        "  #1\n"
        "  Scenario: See it fail                       # tests/functional/output_features/failed_table/failed_table.feature:2\n"
        u"    Given I have a dumb step that passes ♥    # tests/functional/output_features/failed_table/failed_table_steps.py:20\n"
        "    And this one fails                        # tests/functional/output_features/failed_table/failed_table_steps.py:24\n"
        "    Traceback (most recent call last):\n"
        '      File "%(lettuce_core_file)s", line %(call_line)d, in __call__\n'
        "        ret = self.function(self.step, *args, **kw)\n"
        '      File "%(step_file)s", line 25, in tof\n'
        "        assert False\n"
        "    AssertionError\n"
        "    Then this one will be skipped             # tests/functional/output_features/failed_table/failed_table_steps.py:28\n"
        "    And this one will be skipped              # tests/functional/output_features/failed_table/failed_table_steps.py:28\n"
        "    And this one does not even has definition # tests/functional/output_features/failed_table/failed_table.feature:12 (undefined)\n"
        "\n"
        "  ----------------------------------------------------------------------------"
        "\n"
        "\n"
        "1 feature (1 failed)\n"
        "1 scenario (1 failed)\n"
        "5 steps (1 passed, 1 undefined, 2 skipped, 1 failed)\n"
        "\n"
        "You can implement step definitions for undefined steps with these snippets:\n"
        "\n"
        "# -*- coding: utf-8 -*-\n"
        "from lettuce import step\n"
        "\n"
        "@step(ur'this one does not even has definition')\n"
        "def this_one_does_not_even_has_definition(self):\n"
        "    raise NotImplementedError()\n"
        "\n"
        "\n"
        "List of failed scenarios:\n"
        "\n"
        " * Feature: Table Fail\n"
        "    - Scenario: See it fail\n"
        "      (tests/functional/output_features/failed_table/failed_table.feature:2)\n"
        "\n"
        ) % {
            'lettuce_core_file': abspath(lettuce_path('core.py')),
            'step_file': abspath(lettuce_path('..', 'tests', 'functional', 'output_features', 'failed_table', 'failed_table_steps.py')),
            'call_line': call_line,
        }
    )


def test_output_with_successful_outline_colorless():
    "With colorless output, a successful outline scenario should print beautifully."

    with capture_output() as (out, err):
        runner = Runner(feature_name('success_outline'), verbosity=3)
        runner.run()

    assert_equals(out.getvalue(),
        u'\n'
        u'Feature: Successful Scenario Outline                              # tests/functional/output_features/success_outline/success_outline.feature:1\n'
        u'  As lettuce author                                               # tests/functional/output_features/success_outline/success_outline.feature:2\n'
        u'  In order to finish the first release                            # tests/functional/output_features/success_outline/success_outline.feature:3\n'
        u'  I want to make scenario outlines work ♥                         # tests/functional/output_features/success_outline/success_outline.feature:4\n'
        u'\n'
        u'  #1\n'
        u'  Scenario Outline: fill a web form                               # tests/functional/output_features/success_outline/success_outline.feature:6\n'
        u'\n'
        u'  Example #1:\n'
        u'    | username | password | email          | title              |\n'
        u'    | john     | doe-1234 | john@gmail.org | John \| My Website |\n'
        u'\n'
        u'    Given I open browser at "http://www.my-website.com/"          # tests/functional/output_features/success_outline/success_outline_steps.py:21\n'
        u'    And click on "sign-up"                                        # tests/functional/output_features/success_outline/success_outline_steps.py:25\n'
        u'    When I fill the field "username" with "<username>"            # tests/functional/output_features/success_outline/success_outline_steps.py:29\n'
        u'    And I fill the field "password" with "<password>"             # tests/functional/output_features/success_outline/success_outline_steps.py:29\n'
        u'    And I fill the field "password-confirm" with "<password>"     # tests/functional/output_features/success_outline/success_outline_steps.py:29\n'
        u'    And I fill the field "email" with "<email>"                   # tests/functional/output_features/success_outline/success_outline_steps.py:29\n'
        u'    And I click "done"                                            # tests/functional/output_features/success_outline/success_outline_steps.py:33\n'
        u'    Then I see the title of the page is "<title>"                 # tests/functional/output_features/success_outline/success_outline_steps.py:37\n'
        u'\n'
        u'  ----------------------------------------------------------------------------\n'
        u'\n'
        u'  Example #2:\n'
        u'    | username | password | email          | title              |\n'
        u'    | mary     | wee-9876 | mary@email.com | Mary \| My Website |\n'
        u'\n'
        u'    Given I open browser at "http://www.my-website.com/"          # tests/functional/output_features/success_outline/success_outline_steps.py:21\n'
        u'    And click on "sign-up"                                        # tests/functional/output_features/success_outline/success_outline_steps.py:25\n'
        u'    When I fill the field "username" with "<username>"            # tests/functional/output_features/success_outline/success_outline_steps.py:29\n'
        u'    And I fill the field "password" with "<password>"             # tests/functional/output_features/success_outline/success_outline_steps.py:29\n'
        u'    And I fill the field "password-confirm" with "<password>"     # tests/functional/output_features/success_outline/success_outline_steps.py:29\n'
        u'    And I fill the field "email" with "<email>"                   # tests/functional/output_features/success_outline/success_outline_steps.py:29\n'
        u'    And I click "done"                                            # tests/functional/output_features/success_outline/success_outline_steps.py:33\n'
        u'    Then I see the title of the page is "<title>"                 # tests/functional/output_features/success_outline/success_outline_steps.py:37\n'
        u'\n'
        u'  ----------------------------------------------------------------------------\n'
        u'\n'
        u'  Example #3:\n'
        u'    | username | password | email       | title             |\n'
        u'    | foo      | foo-bar  | foo@bar.com | Foo \| My Website |\n'
        u'\n'
        u'    Given I open browser at "http://www.my-website.com/"          # tests/functional/output_features/success_outline/success_outline_steps.py:21\n'
        u'    And click on "sign-up"                                        # tests/functional/output_features/success_outline/success_outline_steps.py:25\n'
        u'    When I fill the field "username" with "<username>"            # tests/functional/output_features/success_outline/success_outline_steps.py:29\n'
        u'    And I fill the field "password" with "<password>"             # tests/functional/output_features/success_outline/success_outline_steps.py:29\n'
        u'    And I fill the field "password-confirm" with "<password>"     # tests/functional/output_features/success_outline/success_outline_steps.py:29\n'
        u'    And I fill the field "email" with "<email>"                   # tests/functional/output_features/success_outline/success_outline_steps.py:29\n'
        u'    And I click "done"                                            # tests/functional/output_features/success_outline/success_outline_steps.py:33\n'
        u'    Then I see the title of the page is "<title>"                 # tests/functional/output_features/success_outline/success_outline_steps.py:37\n'
        u'\n'
        u'  ----------------------------------------------------------------------------\n'
        u'\n'
        u'1 feature (1 passed)\n'
        u'3 scenarios (3 passed)\n'
        u'24 steps (24 passed)\n'
    )


def test_output_with_failful_outline_colorless():
    "With colorless output, an unsuccessful outline scenario should print beautifully."

    with capture_output() as (out, err):
        runner = Runner(feature_name('fail_outline'), verbosity=3)
        assert_raises(SystemExit, runner.run)

    assert_equals(out.getvalue(),
        u'\n'
        u'Feature: Failful Scenario Outline                             # tests/functional/output_features/fail_outline/fail_outline.feature:1\n'
        u'  As lettuce author                                           # tests/functional/output_features/fail_outline/fail_outline.feature:2\n'
        u'  In order to finish the first release                        # tests/functional/output_features/fail_outline/fail_outline.feature:3\n'
        u'  I want to make scenario outlines work ♥                     # tests/functional/output_features/fail_outline/fail_outline.feature:4\n'
        u'\n'
        u'  #1\n'
        u'  Scenario Outline: fill a web form                           # tests/functional/output_features/fail_outline/fail_outline.feature:6\n'
        u'\n'
        u'  Example #1:\n'
        u'    | username | password | email          | message       |\n'
        u'    | john     | doe-1234 | john@gmail.org | Welcome, John |\n'
        u'\n'
        u'    Given I open browser at "http://www.my-website.com/"      # tests/functional/output_features/fail_outline/fail_outline_steps.py:21\n'
        u'    And click on "sign-up"                                    # tests/functional/output_features/fail_outline/fail_outline_steps.py:25\n'
        u'    When I fill the field "username" with "<username>"        # tests/functional/output_features/fail_outline/fail_outline_steps.py:29\n'
        u'    And I fill the field "password" with "<password>"         # tests/functional/output_features/fail_outline/fail_outline_steps.py:29\n'
        u'    And I fill the field "password-confirm" with "<password>" # tests/functional/output_features/fail_outline/fail_outline_steps.py:29\n'
        u'    And I fill the field "email" with "<email>"               # tests/functional/output_features/fail_outline/fail_outline_steps.py:29\n'
        u'    And I click "done"                                        # tests/functional/output_features/fail_outline/fail_outline_steps.py:33\n'
        u'    Then I see the message "<message>"                        # tests/functional/output_features/fail_outline/fail_outline_steps.py:37\n'
        "\n"
        "  ----------------------------------------------------------------------------\n"
        u'\n'
        u'  Example #2:\n'
        u'    | username | password | email          | message       |\n'
        u'    | mary     | wee-9876 | mary@email.com | Welcome, Mary |\n'
        u'\n'
        u'    Given I open browser at "http://www.my-website.com/"      # tests/functional/output_features/fail_outline/fail_outline_steps.py:21\n'
        u'    And click on "sign-up"                                    # tests/functional/output_features/fail_outline/fail_outline_steps.py:25\n'
        u'    When I fill the field "username" with "<username>"        # tests/functional/output_features/fail_outline/fail_outline_steps.py:29\n'
        u'    And I fill the field "password" with "<password>"         # tests/functional/output_features/fail_outline/fail_outline_steps.py:29\n'
        u"    Traceback (most recent call last):\n"
        u'      File "%(lettuce_core_file)s", line %(call_line)d, in __call__\n'
        u"        ret = self.function(self.step, *args, **kw)\n"
        u'      File "%(step_file)s", line 30, in when_i_fill_the_field_x_with_y\n'
        u"        if field == 'password' and value == 'wee-9876':  assert False\n"
        u"    AssertionError\n"
        u'    And I fill the field "password-confirm" with "<password>" # tests/functional/output_features/fail_outline/fail_outline_steps.py:29\n'
        u'    And I fill the field "email" with "<email>"               # tests/functional/output_features/fail_outline/fail_outline_steps.py:29\n'
        u'    And I click "done"                                        # tests/functional/output_features/fail_outline/fail_outline_steps.py:33\n'
        u'    Then I see the message "<message>"                        # tests/functional/output_features/fail_outline/fail_outline_steps.py:37\n'
        "\n"
        "  ----------------------------------------------------------------------------\n"
        u'\n'
        u'  Example #3:\n'
        u'    | username | password | email       | message      |\n'
        u'    | foo      | foo-bar  | foo@bar.com | Welcome, Foo |\n'
        u'\n'
        u'    Given I open browser at "http://www.my-website.com/"      # tests/functional/output_features/fail_outline/fail_outline_steps.py:21\n'
        u'    And click on "sign-up"                                    # tests/functional/output_features/fail_outline/fail_outline_steps.py:25\n'
        u'    When I fill the field "username" with "<username>"        # tests/functional/output_features/fail_outline/fail_outline_steps.py:29\n'
        u'    And I fill the field "password" with "<password>"         # tests/functional/output_features/fail_outline/fail_outline_steps.py:29\n'
        u'    And I fill the field "password-confirm" with "<password>" # tests/functional/output_features/fail_outline/fail_outline_steps.py:29\n'
        u'    And I fill the field "email" with "<email>"               # tests/functional/output_features/fail_outline/fail_outline_steps.py:29\n'
        u'    And I click "done"                                        # tests/functional/output_features/fail_outline/fail_outline_steps.py:33\n'
        u'    Then I see the message "<message>"                        # tests/functional/output_features/fail_outline/fail_outline_steps.py:37\n'
        "\n"
        "  ----------------------------------------------------------------------------\n"
        u'\n'
        u'1 feature (1 failed)\n'
        u'3 scenarios (2 passed, 1 failed)\n'
        u'24 steps (19 passed, 4 skipped, 1 failed)\n'
        u'\n'
        u'List of failed scenarios:\n'
        u'\n'
        u' * Feature: Failful Scenario Outline\n'
        u'    - Scenario Outline: fill a web form\n'
        u'      (tests/functional/output_features/fail_outline/fail_outline.feature:6)\n'
        u'\n' % {
            'lettuce_core_file': abspath(lettuce_path('core.py')),
            'step_file': abspath(lettuce_path('..', 'tests', 'functional', 'output_features', 'fail_outline', 'fail_outline_steps.py')),
            'call_line': call_line,
        }
    )


def test_output_snippets_with_groups_within_double_quotes_colorless():
    "Testing that the proposed snippet is clever enough to identify groups within double quotes. colorless"

    with capture_output() as (out, err):
        runner = Runner(feature_name('double-quoted-snippet'), verbosity=3)
        assert_raises(SystemExit, runner.run)

    assert_equals(out.getvalue(),
        u'\n'
        u'Feature: double-quoted snippet proposal                          # tests/functional/output_features/double-quoted-snippet/double-quoted-snippet.feature:1\n'
        u'\n'
        u'  #1\n'
        u'  Scenario: Propose matched groups                               # tests/functional/output_features/double-quoted-snippet/double-quoted-snippet.feature:2\n'
        u'    Given I have "stuff here" and "more @#$%ˆ& bizar sutff h3r3" # tests/functional/output_features/double-quoted-snippet/double-quoted-snippet.feature:3 (undefined)\n'
        u'\n'
        u'  ----------------------------------------------------------------------------\n'
        u'\n'
        u'1 feature (1 failed)\n'
        u'1 scenario (1 failed)\n'
        u'1 step (1 undefined)\n'
        u'\n'
        u'You can implement step definitions for undefined steps with these snippets:\n'
        u'\n'
        u"# -*- coding: utf-8 -*-\n"
        u'from lettuce import step\n'
        u'\n'
        u'@step(ur\'I have "([^\"]*)" and "([^\"]*)"\')\n'
        u'def i_have_str_and_str(self, param1, param2):\n'
        u'    raise NotImplementedError()\n'
        u'\n'
    )


def test_output_snippets_with_groups_within_single_quotes_colorless():
    "Testing that the proposed snippet is clever enough to identify groups within single quotes. colorless"

    with capture_output() as (out, err):
        runner = Runner(feature_name('single-quoted-snippet'), verbosity=3)
        assert_raises(SystemExit, runner.run)

    assert_equals(out.getvalue(),
        u'\n'
        u'Feature: single-quoted snippet proposal                          # tests/functional/output_features/single-quoted-snippet/single-quoted-snippet.feature:1\n'
        u'\n'
        u'  #1\n'
        u'  Scenario: Propose matched groups                               # tests/functional/output_features/single-quoted-snippet/single-quoted-snippet.feature:2\n'
        u'    Given I have \'stuff here\' and \'more @#$%ˆ& bizar sutff h3r3\' # tests/functional/output_features/single-quoted-snippet/single-quoted-snippet.feature:3 (undefined)\n'
        u'\n'
        u'  ----------------------------------------------------------------------------\n'
        u'\n'
        u'1 feature (1 failed)\n'
        u'1 scenario (1 failed)\n'
        u'1 step (1 undefined)\n'
        u'\n'
        u'You can implement step definitions for undefined steps with these snippets:\n'
        u'\n'
        u"# -*- coding: utf-8 -*-\n"
        u'from lettuce import step\n'
        u'\n'
        u'@step(ur\'I have "([^"]*)" and "([^"]*)"\')\n'
        u'def i_have_str_and_str(self, param1, param2):\n'
        u'    raise NotImplementedError()\n'
        u'\n'
    )


def test_output_snippets_with_groups_within_redundant_quotes():
    "Testing that the proposed snippet is clever enough to avoid duplicating the same snippet"

    with capture_output() as (out, err):
        runner = Runner(feature_name('redundant-steps-quotes'), verbosity=3)
        assert_raises(SystemExit, runner.run)

    assert_equals(out.getvalue(),
        u'\n'
        u'Feature: avoid duplicating same snippet                          # tests/functional/output_features/redundant-steps-quotes/redundant-steps-quotes.feature:1\n'
        u'\n'
        u'  #1\n'
        u'  Scenario: Propose matched groups                               # tests/functional/output_features/redundant-steps-quotes/redundant-steps-quotes.feature:2\n'
        u'    Given I have "stuff here" and "more @#$%ˆ& bizar sutff h3r3" # tests/functional/output_features/redundant-steps-quotes/redundant-steps-quotes.feature:3 (undefined)\n'
        u'    Given I have "blablabla" and "12345"                         # tests/functional/output_features/redundant-steps-quotes/redundant-steps-quotes.feature:4 (undefined)\n'
        u'\n'
        u'  ----------------------------------------------------------------------------\n'
        u'\n'
        u'1 feature (1 failed)\n'
        u'1 scenario (1 failed)\n'
        u'2 steps (2 undefined)\n'
        u'\n'
        u'You can implement step definitions for undefined steps with these snippets:\n'
        u'\n'
        u"# -*- coding: utf-8 -*-\n"
        u'from lettuce import step\n'
        u'\n'
        u'@step(ur\'I have "([^"]*)" and "([^"]*)"\')\n'
        u'def i_have_str_and_str(self, param1, param2):\n'
        u'    raise NotImplementedError()\n'
        u'\n'
    )


def test_output_snippets_with_normalized_unicode_names():
    "Testing that the proposed snippet is clever enough normalize method names even with latin accents"

    with capture_output() as (out, err):
        runner = Runner(feature_name('latin-accents'), verbosity=3)
        assert_raises(SystemExit, runner.run)

    assert_equals(out.getvalue(),
        u'\n'
        u'Funcionalidade: melhorar o output de snippets do lettuce                                      # tests/functional/output_features/latin-accents/latin-accents.feature:2\n'
        u'  Como autor do lettuce                                                                       # tests/functional/output_features/latin-accents/latin-accents.feature:3\n'
        u'  Eu quero ter um output refinado de snippets                                                 # tests/functional/output_features/latin-accents/latin-accents.feature:4\n'
        u'  Para melhorar, de uma forma geral, a vida do programador                                    # tests/functional/output_features/latin-accents/latin-accents.feature:5\n'
        u'\n'
        u'  #1\n'
        u'  Cenário: normalizar snippets com unicode                                                    # tests/functional/output_features/latin-accents/latin-accents.feature:7\n'
        u'    Dado que eu tenho palavrões e outras situações                                            # tests/functional/output_features/latin-accents/latin-accents.feature:8 (undefined)\n'
        u'    E várias palavras acentuadas são úteis, tais como: \"(é,não,léo,chororó,chácara,epígrafo)\" # tests/functional/output_features/latin-accents/latin-accents.feature:9 (undefined)\n'
        u'    Então eu fico felizão                                                                     # tests/functional/output_features/latin-accents/latin-accents.feature:10 (undefined)\n'
        u'\n'
        u'  ----------------------------------------------------------------------------\n'
        u'\n'
        u'1 feature (1 failed)\n'
        u'1 scenario (1 failed)\n'
        u'3 steps (3 undefined)\n'
        u'\n'
        u'You can implement step definitions for undefined steps with these snippets:\n'
        u'\n'
        u'# -*- coding: utf-8 -*-\n'
        u'from lettuce import step\n'
        u'\n'
        u'@step(ur\'eu fico felizão\')\n'
        u'def eu_fico_felizao(self):\n'
        u'    raise NotImplementedError()\n'
        u'\n'
        u'@step(ur\'que eu tenho palavrões e outras situações\')\n'
        u'def que_eu_tenho_palavroes_e_outras_situacoes(self):\n'
        u'    raise NotImplementedError()\n'
        u'\n'
        u'@step(ur\'várias palavras acentuadas são úteis, tais como: "([^"]*)"\')\n'
        u'def varias_palavras_acentuadas_sao_uteis_tais_como_str(self, param1):\n'
        u'    raise NotImplementedError()\n'
        u'\n'
    )


def test_output_level_2_success():
    """Output with verbosity 2 must show only the scenario names, followed
    by "... OK" in case of success
    """

    with capture_output() as (out, err):
        runner = Runner(join(abspath(dirname(__file__)),
                             'output_features', 'many_successful_scenarios'),
                        verbosity=2)
        runner.run()

    assert_equals(out.getvalue(),
        "Feature: Dumb feature\n"
        "Do nothing... OK\n"
        "Do nothing (again)... OK\n"
        "\n"
        "1 feature (1 passed)\n"
        "2 scenarios (2 passed)\n"
        "2 steps (2 passed)\n"
    )


def test_output_level_2_fail():
    'Output with verbosity 2 must show only the scenario names, followed by "... FAILED" in case of fail'

    with capture_output() as (out, err):
        runner = Runner(feature_name('failed_table'), verbosity=2)
        assert_raises(SystemExit, runner.run)

    assert_equals(out.getvalue(),
        u'Feature: Table Fail\n'
        u'See it fail... FAILED\n'
        u'And this one fails                            # tests/functional/output_features/failed_table/failed_table_steps.py:24\n'
        u'    Traceback (most recent call last):\n'
        u'      File "%(lettuce_core_file)s", line %(call_line)d, in __call__\n'
        u'        ret = self.function(self.step, *args, **kw)\n'
        u'      File "%(step_file)s", line 25, in tof\n'
        u'        assert False\n'
        u'    AssertionError\n'
        u'\n'
        u'\n'
        u'1 feature (1 failed)\n'
        u'1 scenario (1 failed)\n'
        u'5 steps (1 passed, 1 undefined, 2 skipped, 1 failed)\n'
        u'\n'
        u'You can implement step definitions for undefined steps with these snippets:\n'
        u'\n'
        u'# -*- coding: utf-8 -*-\n'
        u'from lettuce import step\n'
        u'\n'
        u'@step(ur\'this one does not even has definition\')\n'
        u'def this_one_does_not_even_has_definition(self):\n'
        u'    raise NotImplementedError()\n'
        u'\n'
        u'\n'
        u'List of failed scenarios:\n'
        u'\n'
        u' * Feature: Table Fail\n'
        u'    - Scenario: See it fail\n'
        u'      (tests/functional/output_features/failed_table/failed_table.feature:2)\n'
        u'\n' % {
            'lettuce_core_file': abspath(lettuce_path('core.py')),
            'step_file': abspath(lettuce_path('..', 'tests', 'functional', 'output_features', 'failed_table', 'failed_table_steps.py')),
            'call_line': call_line,
        }
    )


def test_output_level_2_error():
    'Output with verbosity 2 must show only the scenario names, followed by "... ERROR" in case of fail'

    with capture_output() as (out, err):
        runner = Runner(feature_name('error_traceback'), verbosity=2)
        assert_raises(SystemExit, runner.run)

    assert_equals(out.getvalue(),
        u'Feature: Error traceback for output testing\n'
        u'It should pass... OK\n'
        u'It should raise an exception different of AssertionError... ERROR\n'
        u'Given my step that blows a exception                                 # tests/functional/output_features/error_traceback/error_traceback_steps.py:9\n'
        u'    Traceback (most recent call last):\n'
        u'      File "%(lettuce_core_file)s", line %(call_line)d, in __call__\n'
        u'        ret = self.function(self.step, *args, **kw)\n'
        u'      File "%(step_file)s", line 10, in given_my_step_that_blows_a_exception\n'
        u'        raise RuntimeError\n'
        u'    RuntimeError\n'
        u'\n'
        u'\n'
        u'1 feature (1 failed)\n'
        u'2 scenarios (1 passed, 1 failed)\n'
        u'2 steps (1 passed, 1 failed)\n'
        u'\n'
        u'List of failed scenarios:\n'
        u'\n'
        u' * Feature: Error traceback for output testing\n'
        u'    - Scenario: It should raise an exception different of AssertionError\n'
        u'      (tests/functional/output_features/error_traceback/error_traceback.feature:5)\n'
        u'\n' % {
            'lettuce_core_file': abspath(lettuce_path('core.py')),
            'step_file': abspath(lettuce_path('..', 'tests', 'functional', 'output_features', 'error_traceback', 'error_traceback_steps.py')),
            'call_line': call_line,
        }
    )


def test_output_level_1_success():
    """Output with verbosity 2 must show only the scenario names, followed by
    "... OK" in case of success
    """

    with capture_output() as (out, err):
        runner = Runner(join(abspath(dirname(__file__)),
                             'output_features', 'many_successful_scenarios'),
                        verbosity=1)
        runner.run()

    assert_equals(out.getvalue(),
        ".."
        "\n"
        "1 feature (1 passed)\n"
        "2 scenarios (2 passed)\n"
        "2 steps (2 passed)\n"
    )


def test_output_level_1_fail():
    'Output with verbosity 2 must show only the scenario names, followed by "... FAILED" in case of fail'

    with capture_output() as (out, err):
        runner = Runner(feature_name('failed_table'), verbosity=1)
        assert_raises(SystemExit, runner.run)

    assert_equals(out.getvalue(),
        u'F\n'
        u'\n'
        u'<Step: "And this one fails">\n'
        u'Traceback (most recent call last):\n'
        u'  File "%(lettuce_core_file)s", line %(call_line)d, in __call__\n'
        u'    ret = self.function(self.step, *args, **kw)\n'
        u'  File "%(step_file)s", line 25, in tof\n'
        u'    assert False\n'
        u'AssertionError\n'
        u'\n'
        u'1 feature (0 passed)\n'
        u'1 scenario (0 passed)\n'
        u'5 steps (1 failed, 2 skipped, 1 undefined, 1 passed)\n'
        u'\n'
        u'List of failed scenarios:\n'
        u'\n'
        u' * Feature: Table Fail\n'
        u'    - Scenario: See it fail\n'
        u'      (tests/functional/output_features/failed_table/failed_table.feature:2)\n'
        u'\n' % {
            'lettuce_core_file': abspath(lettuce_path('core.py')),
            'step_file': abspath(lettuce_path('..', 'tests', 'functional', 'output_features', 'failed_table', 'failed_table_steps.py')),
            'call_line': call_line,
        }
    )


def test_output_level_1_error():
    'Output with verbosity 2 must show only the scenario names, followed by "... ERROR" in case of fail'

    with capture_output() as (out, err):
        runner = Runner(feature_name('error_traceback'), verbosity=1)
        assert_raises(SystemExit, runner.run)

    assert_equals(out.getvalue(),
        u'.E\n'
        u'\n'
        u'<Step: \"Given my step that blows a exception\">\n'
        u'Traceback (most recent call last):\n'
        u'  File "%(lettuce_core_file)s", line %(call_line)d, in __call__\n'
        u'    ret = self.function(self.step, *args, **kw)\n'
        u'  File "%(step_file)s", line 10, in given_my_step_that_blows_a_exception\n'
        u'    raise RuntimeError\n'
        u'RuntimeError\n'
        u'\n'
        u'1 feature (0 passed)\n'
        u'2 scenarios (1 passed)\n'
        u'2 steps (1 failed, 1 passed)\n'
        u'\n'
        u'List of failed scenarios:\n'
        u'\n'
        u' * Feature: Error traceback for output testing\n'
        u'    - Scenario: It should raise an exception different of AssertionError\n'
        u'      (tests/functional/output_features/error_traceback/error_traceback.feature:5)\n'
        u'\n' % {
            'lettuce_core_file': abspath(lettuce_path('core.py')),
            'step_file': abspath(lettuce_path('..', 'tests', 'functional', 'output_features', 'error_traceback', 'error_traceback_steps.py')),
            'call_line': call_line,
        }
    )


def test_commented_scenario():
    """Test one commented scenario"""

    with capture_output() as (out, err):
        runner = Runner(feature_name('commented_feature'), verbosity=1)
        runner.run()

    assert_equals(out.getvalue(),
        "."
        "\n"
        "1 feature (1 passed)\n"
        "1 scenario (1 passed)\n"
        "1 step (1 passed)\n"
    )


@preserve_registry
def test_blank_step_hash_value():
    """syntax checking: Blank in step hash column = empty string"""

    STEP_REGISTRY.clear()
    from lettuce import step

    @step('ignore step')
    def ignore_step(step):
        pass

    @step('string length calc')
    def string_lenth_calc(step):
        for hash in step.hashes:
            if len(hash["string"]) + len(hash["string2"]) != int(hash["length"]):
                raise AssertionError("fail")

    filename = syntax_feature_name('blank_values_in_hash')

    with capture_output() as (out, err):
        runner = Runner(filename, verbosity=1)
        runner.run()

    assert_equals(out.getvalue(),
        "."
        "\n"
        "1 feature (1 passed)\n"
        "1 scenario (1 passed)\n"
        "4 steps (4 passed)\n"
    )


@preserve_registry
def test_run_only_fast_tests():
    "Runner can filter by tags"

    STEP_REGISTRY.clear()
    from lettuce import step

    good_one = Mock()
    bad_one = Mock()

    @step('I wait for 0 seconds')
    def wait_for_0_seconds(step):
        good_one(step.sentence)

    @step('the time passed is 0 seconds')
    def time_passed_0_sec(step):
        good_one(step.sentence)

    @step('I wait for 60 seconds')
    def wait_for_60_seconds(step):
        bad_one(step.sentence)

    @step('the time passed is 1 minute')
    def time_passed_1_min(step):
        bad_one(step.sentence)

    filename = tag_feature_name('timebound')

    with capture_output() as (out, err):
        runner = Runner(filename, verbosity=1, tags=['fast-ish'])
        runner.run()

    assert_equals(out.getvalue(),
        "."
        "\n"
        "1 feature (1 passed)\n"
        "1 scenario (1 passed)\n"
        "2 steps (2 passed)\n"
    )


def test_run_random():
    "Randomise the feature order"

    path = fs.relpath(join(abspath(dirname(__file__)), 'no_features', 'unexistent-folder'))

    runner = Runner(path, random=True)
    assert_equals(True, runner.random)
    with patch.object(random, 'shuffle') as pshuffle:
        runner.run()
        pshuffle.assert_called_once_with([])


@preserve_registry
def test_background_with_header():
    "Running background with header"

    STEP_REGISTRY.clear()
    from lettuce import step, world

    @step(ur'the variable "(\w+)" holds (\d+)')
    def set_variable(step, name, value):
        setattr(world, name, int(value))

    @step(ur'the variable "(\w+)" is equal to (\d+)')
    def check_variable(step, name, expected):
        expected = int(expected)
        expect(world).to.have.property(name).being.equal(expected)

    @step(ur'the variable "(\w+)" times (\d+) is equal to (\d+)')
    def multiply_and_verify(step, name, times, expected):
        times = int(times)
        expected = int(expected)
        (getattr(world, name) * times).should.equal(expected)

    filename = bg_feature_name('header')

    with capture_output() as (out, err):
        runner = Runner(filename, verbosity=1)
        runner.run()

    assert_equals(out.getvalue(),
        ".."
        "\n"
        "1 feature (1 passed)\n"
        "2 scenarios (2 passed)\n"
        "7 steps (7 passed)\n"
    )


def test_background_without_header():
    "Running background without header"

    STEP_REGISTRY.clear()
    from lettuce import step, world, before, after

    actions = {}

    @before.each_background
    def register_background_before(background):
        actions['before'] = unicode(background)

    @after.each_background
    def register_background_after(background):
        actions['after'] = {
            'background': unicode(background),
        }

    @step(ur'the variable "(\w+)" holds (\d+)')
    def set_variable(step, name, value):
        setattr(world, name, int(value))

    @step(ur'the variable "(\w+)" is equal to (\d+)')
    def check_variable(step, name, expected):
        expected = int(expected)
        expect(world).to.have.property(name).being.equal(expected)

    @step(ur'the variable "(\w+)" times (\d+) is equal to (\d+)')
    def multiply_and_verify(step, name, times, expected):
        times = int(times)
        expected = int(expected)
        (getattr(world, name) * times).should.equal(expected)

    filename = bg_feature_name('naked')

    with capture_output() as (out, err):
        runner = Runner(filename, verbosity=1)
        runner.run()

    assert_equals(out.getvalue(),
        ".."
        "\n"
        "1 feature (1 passed)\n"
        "2 scenarios (2 passed)\n"
        "7 steps (7 passed)\n"
    )

    expect(actions).to.equal({
        'after': {
            'background': u'<Background for feature: Without Header>'
        },
        'before': u'<Background for feature: Without Header>'
    })


@preserve_registry
def test_output_background_with_success_colorless():
    """
    A feature with background should print it accordingly under verbosity 3
    """

    STEP_REGISTRY.clear()
    from lettuce import step

    line = currentframe().f_lineno  # get line number
    @step(ur'the variable "(\w+)" holds (\d+)')
    def just_pass(step, *args):
        pass

    filename = bg_feature_name('simple')

    with capture_output() as (out, err):
        runner = Runner(filename, verbosity=3)
        runner.run()

    assert_equals(out.getvalue(), u"""
Feature: Simple and successful                # tests/functional/bg_features/simple/simple.feature:1
  As the Lettuce maintainer                   # tests/functional/bg_features/simple/simple.feature:2
  In order to make sure the output is pretty  # tests/functional/bg_features/simple/simple.feature:3
  I want to automate its test                 # tests/functional/bg_features/simple/simple.feature:4

  #1
  Scenario: multiplication changing the value # tests/functional/bg_features/simple/simple.feature:9

  Background:                                 # tests/functional/bg_features/simple/simple.feature:6
    Given the variable "X" holds 2            # tests/functional/test_runner.py:{line}

  Scenario:
    Given the variable "X" is equal to 2      # tests/functional/bg_features/simple/steps.py:5

  ----------------------------------------------------------------------------

1 feature (1 passed)
1 scenario (1 passed)
1 step (1 passed)
"""
        .format(line=line+2)  # increment is line number of step past line
    )


def test_background_with_scenario_before_hook():
    "Running background with before_scenario hook"

    STEP_REGISTRY.clear()
    from lettuce import step, world, before

    @before.each_scenario
    def reset_variable(scenario):
        world.X = None

    @step(ur'the variable "(\w+)" holds (\d+)')
    def set_variable(step, name, value):
        setattr(world, name, int(value))

    @step(ur'the variable "(\w+)" is equal to (\d+)')
    def check_variable(step, name, expected):
        expected = int(expected)
        expect(world).to.have.property(name).being.equal(expected)

    @step(ur'the variable "(\w+)" times (\d+) is equal to (\d+)')
    def multiply_and_verify(step, name, times, expected):
        times = int(times)
        expected = int(expected)
        (getattr(world, name) * times).should.equal(expected)

    filename = bg_feature_name('header')

    with capture_output() as (out, err):
        runner = Runner(filename, verbosity=1)
        runner.run()

    assert_equals(out.getvalue(),
        ".."
        "\n"
        "1 feature (1 passed)\n"
        "2 scenarios (2 passed)\n"
        "7 steps (7 passed)\n"
    )


def test_many_features_a_file():
    "syntax checking: Fail if a file has more than one feature"

    filename = syntax_feature_name('many_features_a_file')

    with capture_output() as (out, err):
        runner = Runner(filename)
        assert_raises(SystemExit, runner.run)

    assert_equals(err.getvalue(), u"""
Syntax error at: {filename}
18:1 Syntax Error: Expected EOF (max one feature per file)
Feature: Addition
^
        """.format(filename=filename).strip()
    )


def test_feature_without_name():
    "syntax checking: Fail on features without name"

    filename = syntax_feature_name('feature_without_name')

    with capture_output() as (out, err):
        runner = Runner(filename)
        assert_raises(SystemExit, runner.run)

    assert_equals(err.getvalue(), u"""
Syntax error at: {filename}
1:1 Feature must have a name
        """.format(filename=filename).strip())


def test_feature_missing_scenarios():
    "syntax checking: Fail on features missing scenarios"

    filename = syntax_feature_name("feature_missing_scenarios")

    with capture_output() as (out, err):
        runner = Runner(filename)
        assert_raises(SystemExit, runner.run)

    assert_equals(err.getvalue(), u"""
Syntax error at: {filename}
2:1 Syntax Error: Expected "Scenario"

^
        """.format(filename=filename).strip())
