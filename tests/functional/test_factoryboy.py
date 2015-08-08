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
Basic scenario tests.
"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
# pylint:disable=redefined-builtin, unused-wildcard-import, wildcard-import
from builtins import *
# pylint:enable=redefined-builtin, unused-wildcard-import, wildcard-import
from future import standard_library
standard_library.install_aliases()

from aloe import world

from aloe.testing import (
    FeatureTest,
    in_directory,
)


@in_directory('tests/factoryboy_app')
class FactoryBoyTest(FeatureTest):
    """
    Test that calculator feature works as expected.
    """

    def test_factoryboy(self):
        """
        Test running the calculator feature.
        """

        self.assert_feature_success('features/good.feature')
        self.assert_feature_fail('features/bad.feature')
