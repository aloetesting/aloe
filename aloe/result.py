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

import os
import sys
from contextlib import contextmanager
from functools import wraps

import colorama
from colorama import Cursor
import colors

from aloe.registry import (
    CallbackDecorator,
    CALLBACK_REGISTRY,
    PriorityClass,
)
from aloe.strings import ljust, represent_table
from aloe.tools import hook_not_reentrant
from aloe.utils import memoizedproperty, PY3
from nose.result import TextTestResult

# A decorator to add callbacks which wrap the steps looser than all the other
# callbacks.
# pylint:disable=invalid-name
outer_around = CallbackDecorator(CALLBACK_REGISTRY, 'around',
                                 priority_class=PriorityClass.DISPLAY)
# pylint:enable=invalid-name


# Initialize Colorama to support colored output on Windows.
colorama.init()

# Global reference to the Terminal:
# This exists because the hooks have to be registered before the test is
# started, which is when the stream is passed in.
TERMINAL = [None]


class Terminal(object):
    """
    Output coloring and movement.
    """

    # Coloring of various output parts
    DEFAULT_THEME = {
        'preview': 'grey',
        'pending': 'yellow',
        'failed': 'red',
        'passed': 'green',
        'skipped': 'cyan',
        'comment': 'grey',
        'tag': 'cyan',
    }

    @memoizedproperty
    def theme(self):
        """The color theme, taking CUCUMBER_COLORS into account."""

        theme = self.DEFAULT_THEME.copy()
        for theme_element in os.environ.get('CUCUMBER_COLORS', '').split(':'):
            try:
                element, color = theme_element.split('=')
            except ValueError:
                # Ignore invalid values
                continue

            theme[element] = color

        return theme

    is_a_tty = sys.stdout.isatty()

    move_up = Cursor.UP()

    def __init__(self, kind=None, stream=None, force_styling=False):
        if stream is None:
            stream = sys.__stdout__
        self.stream = stream
        self.does_styling = self.is_a_tty or force_styling

    def __nonzero__(self):
        return True

    def __getattr__(self, attr):
        """Create and return color methods for coloring output."""

        color = self.theme[attr]  # pylint:disable=unsubscriptable-object

        return self.colored(color)

    def colored(self, color):
        """A function to output a string in the given color."""

        if not self.does_styling:
            return lambda s: s

        # Grey is not one of the basic 16 colors
        if color == 'grey':
            color = 243

        return lambda s: colors.color(s, fg=color)

    def write(self, arg='', return_=False):
        """
        Write to the stream.

        :param return_: if True return the cursor back to where it was
            before the write.
        """

        # On Python 2, the default output encoding is ASCII
        self.stream.write(arg if PY3 else arg.encode('utf-8'))

        if return_:
            self.stream.write(self.move_up * arg.count('\n'))

    def writeln(self, arg='', return_=False):
        """Convenience function to write a line to the stream."""
        self.write(arg + '\n', return_=return_)

    @classmethod
    def required(cls, func):
        """Decorate this hook to only execute if term is available"""

        @wraps(func)
        def inner(*args, **kwargs):
            """Wrap func to check for term."""

            def empty_generator():
                """
                Hide the generator in a separate function
                because Python 2 can't support "returning from generators"
                """
                yield

            if not TERMINAL[0]:
                return empty_generator()
            else:
                return func(TERMINAL[0], *args, **kwargs)

        return inner


@outer_around.each_feature
@contextmanager
@Terminal.required
def feature_wrapper(term, feature):
    """Display feature execution."""

    try:
        if feature.tags:
            term.writeln(term.tag(feature.represent_tags()))

        lines = feature.represented().splitlines()
        term.writeln(lines[0])
        term.writeln()
        term.writeln('\n'.join(lines[1:]))
        term.writeln()

        yield
    finally:
        pass


@outer_around.each_example
@contextmanager
@Terminal.required
def example_wrapper(term, scenario, outline, steps):
    """Display scenario execution."""

    try:
        if scenario.tags:
            term.writeln(term.tag(scenario.represent_tags()))

        represented = scenario.represented()
        represented = ljust(represented, scenario.feature.max_length + 2)

        term.write(represented)
        term.writeln(term.comment('# ' + scenario.location))

        if outline:
            term.writeln(represent_table([outline.keys(),
                                          outline.values()],
                                         indent=6))
            term.writeln()

        # write a preview of the steps
        if term.is_a_tty:
            steps_ = []

            if scenario.feature.background:
                steps_ += scenario.feature.background.steps

            steps_ += steps

            term.writeln(
                term.preview('\n'.join(
                    step.represented()
                    for step in steps_
                ) + '\n'),
                return_=True
            )

        yield
    finally:
        term.writeln()


@outer_around.each_step
@contextmanager
@Terminal.required
@hook_not_reentrant  # don't display inner steps called by top-level steps
def step_wrapper(term, step):
    """Display step execution."""

    try:
        if term.is_a_tty:
            term.writeln(
                step.represented(color=term.pending),
                return_=True)

        yield
    finally:
        if step.passed:
            color = term.passed
        elif step.failed:
            color = term.failed
        else:
            color = term.skipped

        term.writeln(
            step.represented(color=color)
        )


class AloeTestResult(TextTestResult):
    """
    Cucumber test progress display (verbosity level 3).
    """
    # pylint:disable=too-many-arguments
    def __init__(self, stream, descriptions, verbosity,
                 config=None, errorClasses=None):
        super().__init__(stream, descriptions, verbosity,
                         config=config, errorClasses=errorClasses)
        self.showAll = verbosity == 2
        self.showSteps = verbosity >= 3  # pylint:disable=invalid-name

        if self.showSteps:
            # Register the global terminal so that it can be accessed by
            # the hooks.
            TERMINAL[0] = Terminal(
                stream=stream,
                force_styling=config.force_color)
        else:
            # unset the global -- primarily for the tests where we're going
            # to create more TestResults with different streams.
            TERMINAL[0] = None
