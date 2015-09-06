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

from contextlib import contextmanager
from functools import wraps

import blessings
from aloe.registry import (
    CallbackDecorator,
    CALLBACK_REGISTRY,
    PriorityClass,
)
from aloe.strings import ljust, represent_table
from aloe.tools import hook_not_reentrant
from nose.result import TextTestResult

# A decorator to add callbacks which wrap the steps looser than all the other
# callbacks.
# pylint:disable=invalid-name
outer_around = CallbackDecorator(CALLBACK_REGISTRY, 'around',
                                 priority_class=PriorityClass.DISPLAY)
# pylint:enable=invalid-name


# Global reference to the Terminal:
# This exists because the hooks have to be registered before the test is
# started, which is when the stream is passed in.
TERMINAL = [None]


class Terminal(blessings.Terminal):
    """
    Wrapped Terminal object for display hooks.

     * Adds additional features: write and writeln.
     * Adds a decorator to require the terminal global being set and
       pass it into hooks.
     * Works around a bug in blessings.Terminal.
    """

    def write(self, arg='', return_=False):
        """
        Write to the stream.

        :param return_: if True return the cursor back to where it was
            before the write.
        """
        self.stream.write(arg)

        if return_:
            self.stream.write(self.move_up * arg.count('\n'))

    def writeln(self, arg='', return_=False):
        """Convenience function to write a line to the stream."""
        self.write(arg + '\n', return_=return_)

    def color(self, color):  # pylint:disable=arguments-differ
        """Wrap Terminal.color() to work if styling is not set"""
        return super(Terminal, self).color(color) if self.does_styling else str

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
            term.writeln(term.cyan(feature.represent_tags()))

        lines = feature.represented().splitlines()
        term.writeln(term.bold_white(lines[0]))
        term.writeln()
        term.writeln(term.white('\n'.join(lines[1:])))
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
            term.writeln(term.cyan(scenario.represent_tags()))

        represented = scenario.represented()
        represented = ljust(represented, scenario.feature.max_length + 2)

        term.write(term.bold_white(represented))
        term.writeln(term.color(8)(scenario.location))

        if outline:
            term.writeln(represent_table([outline.keys(),
                                          outline.values()],
                                         indent=6,
                                         cell_wrap=term.white))
            term.writeln()

        # write a preview of the steps
        if term.is_a_tty:
            steps_ = []

            if scenario.feature.background:
                steps_ += scenario.feature.background.steps

            steps_ += steps

            term.writeln(
                term.color(8)('\n'.join(
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
                step.represented(color=term.color(11)),
                return_=True)

        yield
    finally:
        if step.passed:
            color = term.bold_green
        elif step.failed:
            color = term.bold_red
        else:
            color = term.yellow

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
