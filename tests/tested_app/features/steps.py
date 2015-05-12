# Aloe - Cucumber runner for Python based on Lettuce and Nose
# Copyright (C) <2015> Alexey Kotlyarov <a@koterpillar.com>
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

from aloe import before, step, world


@before.each_example
def clear(*args):
    world.numbers = []
    world.result = 0


@step(r'I have entered (\d+) into the calculator')
def enter_number(self, number):
    world.numbers.append(float(number))


@step(r'I press add')
def press_add(self):
    world.result = sum(world.numbers)


@step(r'The result should be (\d+) on the screen')
def assert_result(self, result):
    assert world.result == float(result)
