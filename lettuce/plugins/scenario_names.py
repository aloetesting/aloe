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

from __future__ import print_function

from gettext import (gettext as _,
                     ngettext as N_)

from blessings import Terminal

from lettuce.terrain import after, before

from .common_output import *


term = Terminal()


@before.each_feature
def before_each_feature(feature):
    """
    Print the feature name
    """

    print(term.bold(feature.represented(annotate=False, description=False)))


@before.each_scenario
def before_each_scenario(scenario):
    """
    Print the scenario name
    """

    if scenario.outlines:
        print(scenario.name,
              N_("(%d example)", "(%d examples)", len(scenario.outlines)) %
              len(scenario.outlines), end="... ")
    else:
        print(scenario.name, end="... ")


@after.each_example
def after_each_example(scenario, outline, steps):
    """
    Print the result
    """
    if all(step.passed for step in steps):
        print(term.green(_("OK")), end=' ')
    elif any(not step.has_definition for step in steps):
        print(term.yellow(_("UNDEF")), end=' ')
    else:
        print(term.red(_("FAILED")), end=' ')

        for step in steps:
            if step.failed:
                print(term.bold_red(step.represented(indent=0)))
                print(term.red(step.represent_traceback()))


@after.each_scenario
def after_each_scenario(scenario):
    """
    Print a terminator
    """
    print()
