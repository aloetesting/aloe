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

import blessings

from aloe.testing import (
    FeatureTest,
    in_directory,
)
from aloe.result import Terminal
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


MOCK_ATTTRIBUTES = blessings.COLORS | set((
    'grey',
    'move_up',
))


class MockTerminal(Terminal):
    """Mock terminal to output printable elements instead of ANSI sequences"""

    def __getattribute__(self, attr):
        if attr in MOCK_ATTTRIBUTES:
            return MockTermElement(attr)
        return super(MockTerminal, self).__getattribute__(attr)


@in_directory('tests/simple_app')
class OutputterTest(FeatureTest):
    """
    Test level 3 outputter
    """

    maxDiff = None

    def test_uncolored_output(self):
        """Test streamed output"""

        stream = TestWrapperIO()

        with patch('aloe.result.AloeTestResult.printSummary'):
            self.run_features('features/highlighting.feature',
                              verbosity=3, stream=stream)

            self.assertEqual(stream.getvalue(), """
Feature: Highlighting

  As a programmer
  I want to see my scenarios with pretty highlighting
  So my output is easy to read

  Scenario: behave_as works                            # features/highlighting.feature:13
    Given I have a table
    Given I have entered 10 into the calculator
    And I press [+]

  Scenario Outline: Scenario outlines                  # features/highlighting.feature:17
      | number |
      | 30     |

    Given I have a table
    Given I have entered 30 into the calculator
    And I press add

  Scenario Outline: Scenario outlines                  # features/highlighting.feature:17
      | number |
      | 40     |

    Given I have a table
    Given I have entered 40 into the calculator
    And I press add

  @tables
  Scenario: Scenario with table                        # features/highlighting.feature:27
    Given I have a table
    Given I have a table:
      | value |
      | 1     |
      | 1     |
      | 2     |

  Scenario: Scenario with a multiline                  # features/highlighting.feature:34
    Given I have a table
    Given I have a table:
      \"\"\"
      Not actually a table :-P
      \"\"\"

""".lstrip())

    def test_color_output(self):
        """Test streamed output with color"""

        stream = TestWrapperIO()

        with \
                patch('aloe.result.Terminal', new=MockTerminal), \
                patch('aloe.result.AloeTestResult.printSummary'):
            self.run_features('features/highlighting.feature',
                              verbosity=3, stream=stream,
                              force_color=True)

            self.assertEqual(stream.getvalue(), """
Feature: Highlighting

  As a programmer
  I want to see my scenarios with pretty highlighting
  So my output is easy to read

  Scenario: behave_as works                            t.grey(# features/highlighting.feature:13)
t.green(Given I have a table)
t.green(Given I have entered 10 into the calculator)
t.green(And I press [+])

  Scenario Outline: Scenario outlines                  t.grey(# features/highlighting.feature:17)
      | number |
      | 30     |

t.green(Given I have a table)
t.green(Given I have entered 30 into the calculator)
t.green(And I press add)

  Scenario Outline: Scenario outlines                  t.grey(# features/highlighting.feature:17)
      | number |
      | 40     |

t.green(Given I have a table)
t.green(Given I have entered 40 into the calculator)
t.green(And I press add)

t.cyan(@tables)
  Scenario: Scenario with table                        t.grey(# features/highlighting.feature:27)
t.green(Given I have a table)
t.green(Given I have a table:)
      | t.green(value) |
      | t.green(1) |
      | t.green(1) |
      | t.green(2) |

  Scenario: Scenario with a multiline                  t.grey(# features/highlighting.feature:34)
t.green(Given I have a table)
t.green(Given I have a table:)
      \"\"\"
      t.green(Not actually a table :-P)
      \"\"\"

""".lstrip())

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
                self.run_features('features/highlighting.feature',
                                  verbosity=3, stream=stream,
                                  force_color=True)

            self.assertEqual(stream.getvalue(), """
Feature: Highlighting

  As a programmer
  I want to see my scenarios with pretty highlighting
  So my output is easy to read

  Scenario: behave_as works                            t.grey(# features/highlighting.feature:13)
t.blue(Given I have a table)
t.blue(Given I have entered 10 into the calculator)
t.blue(And I press [+])

  Scenario Outline: Scenario outlines                  t.grey(# features/highlighting.feature:17)
      | number |
      | 30     |

t.blue(Given I have a table)
t.blue(Given I have entered 30 into the calculator)
t.blue(And I press add)

  Scenario Outline: Scenario outlines                  t.grey(# features/highlighting.feature:17)
      | number |
      | 40     |

t.blue(Given I have a table)
t.blue(Given I have entered 40 into the calculator)
t.blue(And I press add)

t.cyan(@tables)
  Scenario: Scenario with table                        t.grey(# features/highlighting.feature:27)
t.blue(Given I have a table)
t.blue(Given I have a table:)
      | t.blue(value) |
      | t.blue(1) |
      | t.blue(1) |
      | t.blue(2) |

  Scenario: Scenario with a multiline                  t.grey(# features/highlighting.feature:34)
t.blue(Given I have a table)
t.blue(Given I have a table:)
      \"\"\"
      t.blue(Not actually a table :-P)
      \"\"\"

""".lstrip())

    def test_tty_output(self):
        """Test streamed output with tty control codes"""

        stream = TestWrapperIO()

        with \
                patch('aloe.result.Terminal', new=MockTerminal) as mock_term, \
                patch('aloe.result.AloeTestResult.printSummary'):

            mock_term.is_a_tty = True
            self.run_features('-n', '1',
                              'features/highlighting.feature',
                              verbosity=3, stream=stream)

            # we are going to see the scenario written out 3 times
            # once as a preview, then each line individually followed by a
            # green version of it
            self.assertEqual(stream.getvalue(), """
Feature: Highlighting

  As a programmer
  I want to see my scenarios with pretty highlighting
  So my output is easy to read

  Scenario: behave_as works                            t.grey(# features/highlighting.feature:13)
t.grey(Given I have a table
    Given I have entered 10 into the calculator
    And I press [+])
<t.move_up><t.move_up><t.move_up>t.yellow(Given I have a table)
<t.move_up>t.green(Given I have a table)
t.yellow(Given I have entered 10 into the calculator)
<t.move_up>t.green(Given I have entered 10 into the calculator)
t.yellow(And I press [+])
<t.move_up>t.green(And I press [+])

""".lstrip())

    def test_full_color_output_no_mocks(self):
        """Test full color output with no mocks"""

        self.assert_feature_success('--color',
                                    'features/highlighting.feature',
                                    verbosity=3)
