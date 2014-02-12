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

import os
import re
import sys
from contextlib import contextmanager
from cStringIO import StringIO
from gettext import ngettext as N_

from blessings import Terminal

from lettuce import core, strings

from lettuce.terrain import after, before, world


term = Terminal()


_ansi = re.compile(r'\x1b[^m]*m')
strip_ansi = lambda s: _ansi.sub('', s)


class OutputManager(object):
    """
    Handle diversions of stdout/stderr
    """

    real_stdout = sys.stdout
    real_stderr = sys.stderr

    def divert(self):
        self.diverted = True
        sys.stdout = StringIO()
        sys.stderr = StringIO()

    def undivert(self):
        if not self.diverted:
            raise RuntimeError("Not diverted!")

        stdout = sys.stdout.getvalue()
        stderr = sys.stderr.getvalue()

        sys.stdout = self.real_stdout
        sys.stderr = self.real_stderr

        return (stdout, stderr)

    @contextmanager
    def capture_and_count(self):
        """
        Capture the output, then count how many lines were rendered
        """

        self.divert()

        yield

        stdout, _ = self.undivert()

        lines = 0
        for line in stdout.splitlines():
            # print line
            # print "LEN", len(strip_ansi(line))
            # FIXME: I need to strip escape sequences here
            lines += (len(strip_ansi(line)) // (term.width + 1) + 1)

        sys.stdout.write(stdout)

        for _ in xrange(lines):
            sys.stdout.write(term.move_up)

output = OutputManager()


def print_(string, color=term.white, comment_color=term.color(8)):
    # print a string in the given colour, with the reference in grey

    try:
        left, right = string.rsplit('#')

        right = u'#' + right

        if len(string) > term.width:
            print color(left)
            print comment_color(right.rjust(term.width))
        else:
            print color(left) + comment_color(right)
    except ValueError:
        print color(string)


@before.each_step
def print_step_running(step):

    with output.capture_and_count():
        print_(step.represented())
        if step.table:
            print step.represent_hashes()

    output.divert()


@after.each_step
def print_step_ran(step):
    if step.failed:
        color = term.bold_red

    elif step.passed:
        color = term.bold_green

    elif not step.run:
        color = term.cyan

    elif not step.has_definition:
        color = term.yellow

    else:
        raise NotImplementedError("Should not reach here")

    stdout, stderr = output.undivert()

    print_(step.represented(), color=color)

    if step.table:
        print step.represent_hashes(cell_wrap=color)

    sys.stdout.write(stdout)
    sys.stderr.write(stderr)

    if step.failed:
        print color(step.represent_traceback())


@before.each_scenario
def print_scenario_running(scenario):
    print_(scenario.represented(), color=term.bold)


@before.each_example
def print_example_running(scenario, outline):
    if not outline:
        return

    print
    print strings.represent_table([outline.keys(), outline.values()],
                                  indent=4)
    print


@before.each_feature
def print_feature_running(feature):
    s = iter(feature.represented().splitlines())

    print_(next(s), color=term.bold_white)

    for s in s:
        print_(s)

    print


@after.all
def print_summary(total):
    """
    Print the summary
    """

    print

    color = term.bold_green \
        if total.features_passed == total.features_ran \
        else term.bold_red
    print u"{total} ({passed})".format(
        total=term.bold(N_("%d feature",
                           "%d features",
                           total.features_ran) % total.features_ran),
        passed=color("%d passed" % total.features_passed))

    color = term.bold_green \
        if total.scenarios_passed == total.scenarios_ran \
        else term.bold_red
    print u"{total} ({passed})".format(
        total=term.bold(N_("%d scenario",
                           "%d scenarios",
                           total.scenarios_ran) % total.scenarios_ran),
        passed=color("%d passed" % total.scenarios_passed))

    color = term.bold_green \
        if total.steps_passed == total.steps \
        else term.bold_red
    print u"{total} ({passed})".format(
        total=term.bold(N_("%d step",
                           "%d steps",
                           total.steps) % total.steps),
        passed=color("%d passed" % total.steps_passed))

    # steps_details = []
    # kinds_and_colors = {
    #     'failed': '\033[0;31m',
    #     'skipped': '\033[0;36m',
    #     'undefined': '\033[0;33m'
    # }

    # for kind, color in kinds_and_colors.items():
    #     attr = 'steps_%s' % kind
    #     stotal = getattr(total, attr)
    #     if stotal:
    #         steps_details.append("%s%d %s" % (color, stotal, kind))

    # steps_details.append("\033[1;32m%d passed\033[1;37m" % total.steps_passed)
    # word = total.steps > 1 and "steps" or "step"
    # content = "\033[1;37m, ".join(steps_details)

    # word = total.steps > 1 and "steps" or "step"
    # write_out("\033[1;37m%d %s (%s)\033[0m\n" % (
    #     total.steps,
    #     word,
    #     content))

    # if total.proposed_definitions:
    #     wrt("\n\033[0;33mYou can implement step definitions for undefined steps with these snippets:\n\n")
    #     wrt("# -*- coding: utf-8 -*-\n")
    #     wrt("from lettuce import step\n\n")

    #     last = len(total.proposed_definitions) - 1
    #     for current, step in enumerate(total.proposed_definitions):
    #         method_name = step.proposed_method_name
    #         wrt("@step(u'%s')\n" % step.proposed_sentence)
    #         wrt("def %s:\n" % method_name)
    #         wrt("    assert False, 'This step must be implemented'")
    #         if current is last:
    #             wrt("\033[0m")

    #         wrt("\n")

    # if total.failed_scenario_locations:
    #     # print list of failed scenarios, with their file and line number
    #     wrt("\n")
    #     wrt("\033[1;31m")
    #     wrt("List of failed scenarios:\n")
    #     wrt("\033[0;31m")
    #     for scenario in total.failed_scenario_locations:
    #         wrt(scenario)
    #     wrt("\033[0m")
    #     wrt("\n")


def print_no_features_found(where):
    where = core.fs.relpath(where)
    if not where.startswith(os.sep):
        where = '.%s%s' % (os.sep, where)

    write_out('\033[1;31mOops!\033[0m\n')
    write_out(
        '\033[1;37mcould not find features at '
        '\033[1;33m%s\033[0m\n' % where)


@before.each_background
def print_background_running(background):
    print_(background.represented(), color=term.bold_white)


@after.each_background
def print_background_ran(background, results):
    print_("...")
