# -*- coding: utf-8 -*-
"""
Test basic Language functions.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()

from nose.tools import assert_equal

from aloe.languages import Language


def test_language_is_english_by_default():
    """Language class is english by default"""

    lang = Language()

    assert_equal(lang.code, 'en')
    assert_equal(lang.name, 'English')
    assert_equal(lang.native, 'English')
    assert_equal(lang.FEATURE, 'Feature')
    assert_equal(lang.SCENARIO, 'Scenario')
