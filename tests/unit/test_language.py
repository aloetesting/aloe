# -*- coding: utf-8 -*-
# Aloe - Cucumber runner for Python based on Lettuce and Nose
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

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from pyparsing import Keyword

from nose.tools import assert_equals

from aloe.languages import Language


def test_language_is_english_by_default():
    """Language class is english by default"""

    lang = Language()

    assert_equals(lang.code, 'en')
    assert_equals(lang.name, 'English')
    assert_equals(lang.native, 'English')
    assert_equals(lang.FEATURE, 'Feature')
    assert_equals(lang.SCENARIO, 'Scenario')
