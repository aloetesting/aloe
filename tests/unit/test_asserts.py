"""
Test cases for the assertion tests
"""

import sys
from cStringIO import StringIO

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
                      (12, 16, '1'),
                  ])


# def test_assert_equals_fails_as_expected():
#     """
#     Test assert_equals fails as expected
#     """
#
#     original = """1234
# 1234
# 456790"""
#
#     expected = """1234
# 1234
# 4567890"""
#
#     with assert_raises(AssertionError):
#         stream = StringIO()
#         asserts.assert_equals(original, expected, stream=stream)
#
#     print stream.getvalue()
#
#     expected = """{t.white}  {t.normal}{t.white}1234{t.normal}
# {t.white}  {t.normal}{t.white}1234{t.normal}
# {t.red}- {t.normal}{t.red}456790{t.normal}
# {t.green}+ {t.normal}{t.green}4567{t.normal}{t.black_on_green}8{t.normal}{t.green}90{t.normal}
# """.format(t=term)
#
#     print expected
#
#     asserts.assert_equals(stream.getvalue(), expected)
