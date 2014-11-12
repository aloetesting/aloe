# -*- coding: utf-8 -*-
# <Lettuce - Behaviour Driven Development for python>
# Copyright (C) <2010-2012>  Gabriel Falcão <gabriel@nacaolivre.org>
# Copyright (C) <2014>  Danielle Madeley <danielle@madeley.id.au>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERsteps.pyCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Uncoloured output is the same as coloured output but with blessings
turned off.
"""

try:
    from imp import reload
except ImportError:
    # python 2.5 fallback
    pass

from blessings import Terminal


# share the code with coloured shell output
from . import colored_shell_output
reload(colored_shell_output)
from . import common_output
reload(common_output)
print_no_features_found = common_output.print_no_features_found

# run with stylings disabled
colored_shell_output.term = common_output.term = Terminal(force_styling=None)
