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
# Important: cannot use cStringIO because it does not support unicode!
from StringIO import StringIO
from gettext import gettext as _
from itertools import groupby

from blessings import Terminal

from lettuce import core, strings

from lettuce.terrain import after, before, world

from .common_output import *


term = Terminal()


_ansi = re.compile(ur'\x1b[^m]*m', re.U)
strip_ansi = lambda s: _ansi.sub(u'', s)


class OutputManager(object):
    """
    Handle diversions of stdout/stderr
    """

    real_stdout = sys.stdout
    real_stderr = sys.stderr

    def divert(self):
        self.diverted = True

        # FIXME: these should share one buffer, with the stderr coloured
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

        if not term.does_styling:
            yield
            return

        self.divert()

        yield

        stdout, _ = self.undivert()

        lines = 0
        for line in stdout.splitlines():
            lines += (len(strip_ansi(line)) // (term.width + 1) + 1)

        sys.stdout.write(stdout)

        for _ in xrange(lines):
            sys.stdout.write(term.move_up)

output = OutputManager()


def print_(string, color=term.white, comment_color=term.color(8)):
    # print a string in the given colour, with the reference in grey

    if not term.does_styling:
        print string
        return

    left, right = string.rsplit(u'#')

    right = u'#' + right

    if len(string) > term.width:
        print color(left.rstrip())
        print comment_color(right.rjust(term.width))
    else:
        print color(left) + comment_color(right)


@before.each_step
def print_step_running(step):

    with output.capture_and_count():
        print_(step.represented())
        if step.table:
            print step.represent_hashes(cell_wrap=term.white)

    output.divert()


@after.each_step
def print_step_ran(step):
    if step.failed:
        color = term.bold_red

    elif step.passed:
        color = term.bold_green

    elif not step.has_definition:
        color = term.yellow

    elif not step.ran:
        color = term.cyan

    else:
        raise NotImplementedError("Should not reach here")

    stdout, stderr = output.undivert()

    if term.does_styling:
        # don't repeat ourselves
        print_(step.represented(), color=color)

        if step.table:
            print step.represent_hashes(cell_wrap=color)

    if step.failed:
        sys.stdout.write(stdout)
        sys.stderr.write(term.red(stderr))

    if step.failed:
        print term.bright_red(step.represent_traceback())


@before.each_scenario
def print_scenario_running(scenario):
    print
    print u"  #%d" % (scenario.feature.scenarios.index(scenario) + 1), \
        term.cyan(scenario.represent_tags())
    print_(scenario.represented(), color=term.bold)


@before.each_example
def print_example_running(scenario, outline):
    if not outline:
        return

    print
    print " ",
    print term.bold(_(u"Example #%d:" % (
        scenario.outlines.index(outline) + 1)))
    print strings.represent_table([outline.keys(), outline.values()],
                                  indent=4)
    print


@after.each_example
def print_end_of_example(scenario, outline):
    print
    print ' ', term.dim_white('-' * 76)


@before.each_feature
def print_feature_running(feature):
    print

    if feature.tags:
        print term.cyan(feature.represent_tags())

    print_(feature.represented(description=False), color=term.bold_white)

    for line in feature.represent_description().splitlines():
        print_(line, color=term.white)


@before.each_background
def print_background_running(background):
    print
    print_(background.represented(), color=term.bold_white)


@after.each_background
def print_background_ran(background):
    print
    print " ", term.bold_white(_(u"Scenario:"))
