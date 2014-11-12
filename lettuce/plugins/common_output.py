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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Common output functions
"""

import os
from itertools import groupby

from gettext import (gettext as _,
                     ngettext as N_)

from blessings import Terminal

from lettuce import core
from lettuce.terrain import after


term = Terminal()


def print_no_features_found(where):
    """
    No features found to run
    """

    where = core.fs.relpath(where)
    if not where.startswith(os.sep):
        where = '.%s%s' % (os.sep, where)

    print _(u"Oops!")
    print _(u"Could not find features at %s" % where)


@after.harvest('common_output')
def print_note(total):
    print
    print u"Summary for all applications tested:"


@after.harvest('common_output')
@after.all('common_output')
def print_summary(total):
    """
    Print the summary
    """

    def print_breakdown(klass):
        """
        Create the breakdown of passes and fails
        """

        breakdown = []

        for outcome, color in (
            ('passed', term.bold_green),
            ('undefined', term.yellow),
            ('skipped', term.cyan)
        ):
            n = getattr(total, '%s_%s' % (klass, outcome), 0)

            if n < 1:
                continue

            breakdown.append(color(_(u"{n} {outcome}".format(
                n=n, outcome=outcome))))

        ran = getattr(total, '%s_ran' % klass, 0)
        passed = getattr(total, '%s_passed' % klass, 0)

        try:
            # only steps has a failed attribute
            failed = getattr(total, '%s_failed' % klass)
        except AttributeError:
            failed = ran - passed

        if failed:
            breakdown.append(term.bold_red(
                _(u"{n} failed".format(n=failed))
            ))

        return u', '.join(breakdown)

    print

    print u"{total} ({breakdown})".format(
        total=term.bold(N_(u"%d feature",
                           u"%d features",
                           total.features_ran) % total.features_ran),
        breakdown=print_breakdown('features'))

    print u"{total} ({breakdown})".format(
        total=term.bold(N_(u"%d scenario",
                           u"%d scenarios",
                           total.scenarios_ran) % total.scenarios_ran),
        breakdown=print_breakdown('scenarios'))

    print u"{total} ({breakdown})".format(
        total=term.bold(N_(u"%d step",
                           u"%d steps",
                           total.steps_ran) % total.steps_ran),
        breakdown=print_breakdown('steps'))

    if total.proposed_definitions:
        # print a list of undefined sentences
        print
        print u"You can implement step definitions for undefined steps " \
            u"with these snippets:"

        print term.yellow(u"""
# -*- coding: utf-8 -*-
from lettuce import step
""")

        definitions = sorted(
            total.proposed_definitions,
            key = lambda defn: defn.proposed_sentence[1]
        )
        seen_defns = set()
        for step in definitions:
            step_defn, method_name, n_params = step.proposed_sentence

            if step_defn in seen_defns:
                continue

            params = [u'self'] + [
                u'param%d' % (i + 1) for i in xrange(n_params)
            ]

            print term.yellow(u'''@step(ur'%s')''' % step_defn)
            print term.yellow(u'''def %s(%s):''' % (
                method_name,
                u', '.join(params)))
            print term.yellow(u'''    raise NotImplementedError()''')
            print

            seen_defns.add(step_defn)

    if total.failed_scenarios:
        # print list of failed scenarios, with their file and line number
        print
        print term.bold(_(u"List of failed scenarios:"))
        print

        for feature, scenarios in groupby(total.failed_scenarios,
                                          lambda s: s.feature):
            print u' * ' + feature.represented(indent=0, annotate=False,
                                               description=False)

            for scenario in scenarios:
                print term.bright_red(u'    - ' + scenario.represented(
                    indent=0, annotate=False))
                print term.dim_red(u'      (%s:%d)' % (
                    scenario.described_at.file, scenario.described_at.line))

        print
