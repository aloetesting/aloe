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
Cucumber-esque outputter for Nose.
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
# pylint:disable=redefined-builtin, unused-wildcard-import, wildcard-import
from builtins import *
# pylint:enable=redefined-builtin, unused-wildcard-import, wildcard-import
from future import standard_library
standard_library.install_aliases()

from nose.result import TextTestResult


class AloeTestResult(TextTestResult):
    def __init__(self, stream, descriptions, verbosity,
                 config=None, errorClasses=None):
        super().__init__(stream, descriptions, verbosity,
                         config=config, errorClasses=errorClasses)
        print("Verbosity", verbosity)
        self.showAll = verbosity == 2
        self.showSteps = verbosity > 2

    def startTest(self, test):
        super().startTest(test)
        if self.showSteps:
            self.stream.writeln("Starting test %s" % test)

    def stopTest(self, test):
        super().stopTest(test)
        if self.showSteps:
            self.stream.writeln("Stopping test %s" % test)

    def addSuccess(self, test):
        super().addSuccess(test)
        if self.showSteps:
            self.stream.writeln("BOO YAH")
