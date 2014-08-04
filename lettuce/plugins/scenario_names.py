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

try:
    from imp import reload
except ImportError:
    # python 2.5 fallback
    pass

from blessings import Terminal

from lettuce.terrain import after, before

from . import common_output
reload(common_output)
print_no_features_found = common_output.print_no_features_found


term = common_output.term = Terminal(force_styling=None)


@before.each_feature('output')
def before_each_feature(feature):
    """
    Print the feature name
    """

    print(term.bold(feature.represented(annotate=False, description=False)))


@before.each_scenario('output')
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


@after.each_example('output')
def after_each_example(scenario, outline, steps):
    """
    Print the result
    """
    for step in steps:
        if not step.has_definition:
            print(term.yellow(_("UNDEF")), end='')
            break
        elif step.failed:
            if isinstance(step.why.exception, AssertionError):
                print(term.red(_("FAILED")))
            else:
                print(term.red(_("ERROR")))
            print(term.bold_red(step.represented(indent=0)))
            print(term.red(step.represent_traceback()))
            break
    else:
        print(term.green(_("OK")), end='')


@after.each_scenario('output')
def after_each_scenario(scenario):
    """
    Print a terminator
    """
    print()
