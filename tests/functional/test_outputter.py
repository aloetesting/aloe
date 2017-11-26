# -*- coding: utf-8 -*-
"""
Test level 3 outputter
"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
# pylint:disable=redefined-builtin, unused-wildcard-import, wildcard-import
from builtins import *
# pylint:enable=redefined-builtin, unused-wildcard-import, wildcard-import

import os
from contextlib import contextmanager

from aloe.result import Terminal
from aloe.testing import (
    FeatureTest,
    in_directory,
)
from aloe.utils import TestWrapperIO
from mock import patch


class MockTermElement(object):
    """
    Wraps an element being output by the MockTerminal (i.e. term.bold) and
    replaces it with a string that can be checked in tests.

    Like with the attributes in Terminal it can be used as a callable or
    a string.
    """
    def __init__(self, attr):
        self.attr = attr

    def __call__(self, str_):
        # strips the string to make the output easier to read
        return 't.{attr}({str})'.format(attr=self.attr,
                                        str=str_.strip())

    def __str__(self):
        return '<t.{attr}>'.format(attr=self.attr)

    def __mul__(self, other):
        return str(self) * other


class MockTerminal(Terminal):
    """Mock terminal to output printable elements instead of ANSI sequences"""

    def colored(self, color):
        return MockTermElement(color)

    move_up = MockTermElement('move_up')


@in_directory('tests/simple_app')
class OutputterTest(FeatureTest):
    """
    Test level 3 outputter
    """

    maxDiff = None

    feature = os.path.join('features', 'highlighting.feature')

    def test_uncolored_output(self):
        """Test streamed output"""

        stream = TestWrapperIO()

        with patch('aloe.result.AloeTestResult.printSummary'):
            self.run_features(self.feature, verbosity=3, stream=stream)

            self.assertEqual(stream.getvalue(), """
Feature: Highlighting

  As a programmer
  I want to see my scenarios with pretty highlighting
  So my output is easy to read

  非ASCII字显示得正常

  Scenario: behave_as works                            # {feature}:15
    Given I have a table
    Given I have entered 10 into the calculator
    And I press [+]

  Scenario Outline: Scenario outlines                  # {feature}:19
      | number |
      | 30     |

    Given I have a table
    Given I have entered 30 into the calculator
    And I press add

  Scenario Outline: Scenario outlines                  # {feature}:19
      | number |
      | 40     |

    Given I have a table
    Given I have entered 40 into the calculator
    And I press add

  @tables
  Scenario: Scenario with table                        # {feature}:29
    Given I have a table
    Given I have a table:
      | value |
      | 1     |
      | 1     |
      | 2     |

  Scenario: Scenario with a multiline                  # {feature}:36
    Given I have a table
    Given I have a table:
      \"\"\"
      Not actually a table :-P
      \"\"\"

""".lstrip().format(feature=self.feature))

    def test_color_output(self):
        """Test streamed output with color"""

        stream = TestWrapperIO()

        with \
                patch('aloe.result.Terminal', new=MockTerminal), \
                patch('aloe.result.AloeTestResult.printSummary'):
            self.run_features(self.feature,
                              verbosity=3, stream=stream,
                              force_color=True)

            self.assertEqual(stream.getvalue(), """
Feature: Highlighting

  As a programmer
  I want to see my scenarios with pretty highlighting
  So my output is easy to read

  非ASCII字显示得正常

  Scenario: behave_as works                            t.grey(# {feature}:15)
t.green(Given I have a table)
t.green(Given I have entered 10 into the calculator)
t.green(And I press [+])

  Scenario Outline: Scenario outlines                  t.grey(# {feature}:19)
      | number |
      | 30     |

t.green(Given I have a table)
t.green(Given I have entered 30 into the calculator)
t.green(And I press add)

  Scenario Outline: Scenario outlines                  t.grey(# {feature}:19)
      | number |
      | 40     |

t.green(Given I have a table)
t.green(Given I have entered 40 into the calculator)
t.green(And I press add)

t.cyan(@tables)
  Scenario: Scenario with table                        t.grey(# {feature}:29)
t.green(Given I have a table)
t.green(Given I have a table:)
      | t.green(value) |
      | t.green(1) |
      | t.green(1) |
      | t.green(2) |

  Scenario: Scenario with a multiline                  t.grey(# {feature}:36)
t.green(Given I have a table)
t.green(Given I have a table:)
      \"\"\"
      t.green(Not actually a table :-P)
      \"\"\"

""".lstrip().format(feature=self.feature))

    @contextmanager
    def environment_override(self, key, value):
        """A context manager to temporary set an environment variable."""

        old_value = os.environ.pop(key, None)
        os.environ[key] = value
        try:
            yield
        finally:
            os.environ.pop(key)
            if old_value is not None:
                os.environ[key] = old_value

    def test_customized_color_output(self):
        """Test streamed color output with overridden colors."""

        stream = TestWrapperIO()

        with self.environment_override('CUCUMBER_COLORS',
                                       'failed=magenta:passed=blue'):
            with \
                    patch('aloe.result.Terminal', new=MockTerminal), \
                    patch('aloe.result.AloeTestResult.printSummary'):
                self.run_features(self.feature,
                                  verbosity=3, stream=stream,
                                  force_color=True)

            self.assertEqual(stream.getvalue(), """
Feature: Highlighting

  As a programmer
  I want to see my scenarios with pretty highlighting
  So my output is easy to read

  非ASCII字显示得正常

  Scenario: behave_as works                            t.grey(# {feature}:15)
t.blue(Given I have a table)
t.blue(Given I have entered 10 into the calculator)
t.blue(And I press [+])

  Scenario Outline: Scenario outlines                  t.grey(# {feature}:19)
      | number |
      | 30     |

t.blue(Given I have a table)
t.blue(Given I have entered 30 into the calculator)
t.blue(And I press add)

  Scenario Outline: Scenario outlines                  t.grey(# {feature}:19)
      | number |
      | 40     |

t.blue(Given I have a table)
t.blue(Given I have entered 40 into the calculator)
t.blue(And I press add)

t.cyan(@tables)
  Scenario: Scenario with table                        t.grey(# {feature}:29)
t.blue(Given I have a table)
t.blue(Given I have a table:)
      | t.blue(value) |
      | t.blue(1) |
      | t.blue(1) |
      | t.blue(2) |

  Scenario: Scenario with a multiline                  t.grey(# {feature}:36)
t.blue(Given I have a table)
t.blue(Given I have a table:)
      \"\"\"
      t.blue(Not actually a table :-P)
      \"\"\"

""".lstrip().format(feature=self.feature))

    def test_tty_output(self):
        """Test streamed output with tty control codes"""

        stream = TestWrapperIO()

        with \
                patch('aloe.result.Terminal', new=MockTerminal) as mock_term, \
                patch('aloe.result.AloeTestResult.printSummary'):

            mock_term.is_a_tty = True
            self.run_features('-n', '1',
                              self.feature,
                              verbosity=3, stream=stream)

            # we are going to see the scenario written out 3 times
            # once as a preview, then each line individually followed by a
            # green version of it
            self.assertEqual(stream.getvalue(), """
Feature: Highlighting

  As a programmer
  I want to see my scenarios with pretty highlighting
  So my output is easy to read

  非ASCII字显示得正常

  Scenario: behave_as works                            t.grey(# {feature}:15)
t.grey(Given I have a table
    Given I have entered 10 into the calculator
    And I press [+])
<t.move_up><t.move_up><t.move_up>t.yellow(Given I have a table)
<t.move_up>t.green(Given I have a table)
t.yellow(Given I have entered 10 into the calculator)
<t.move_up>t.green(Given I have entered 10 into the calculator)
t.yellow(And I press [+])
<t.move_up>t.green(And I press [+])

""".lstrip().format(feature=self.feature))

    def test_full_color_output_no_mocks(self):
        """Test full color output with no mocks"""

        self.assert_feature_success('--color',
                                    self.feature,
                                    verbosity=3)
