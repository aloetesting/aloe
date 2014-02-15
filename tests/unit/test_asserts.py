"""
Test cases for the assertion tests
"""

import sys

from nose.tools import assert_equals, assert_raises, with_setup

from blessings import Terminal

from tests import asserts


term = Terminal()


def test_yield_transitions():
    """
    Test yield_transitions
    """

    assert_equals(list(asserts.yield_transitions("1111112222221111")),
                  [
                      (0, 6, '1'),
                      (6, 12, '2'),
                      (12, 15, '1'),
                  ])


@with_setup(asserts.prepare_stdout)
def test_assert_equals_fails_as_expected():
    """
    Test assert_equals fails as expected
    """

    original = """1234
1234
4567"""

    expected = """1234
1234
45678"""

    with assert_raises(AssertionError):
        asserts.assert_equals(original, expected, stream=sys.stdout)

    assert_equals(sys.stdout.getvalue(), """{t.white}  {t.normal}{t.white}1234{t.normal}
{t.white}  {t.normal}{t.white}1234{t.normal}
{t.red}- {t.normal}{t.red}4567{t.normal}
{t.green}+ {t.normal}{t.green}4567{t.normal}{t.black_on_green}8{t.normal}{t.green}{t.normal}
""".format(t=term))
