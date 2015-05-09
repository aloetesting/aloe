# Lychee - Cucumber runner for Python based on Lettuce and Nose
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

"""
Base test class for tests generated from scenarios.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import zip
from builtins import str
from builtins import range
from builtins import super
from future import standard_library
standard_library.install_aliases()

import ast
import unittest
from contextlib import contextmanager
from functools import partial

from lychee.codegen import make_function
from lychee.parser import Feature, Step
from lychee.registry import (
    CallbackDecorator,
    CALLBACK_REGISTRY,
    PriorityClass,
    STEP_REGISTRY,
)
from lychee.utils import always_str


class TestStep(Step):
    """
    A step with additional functions for the callbacks.
    """

    def __init__(self, testclass, *args, **kwargs):
        self.testclass = testclass
        self.failed = None
        self.passed = None
        super().__init__(*args, **kwargs)

    def behave_as(self, string):
        self.testclass.behave_as(self, string)

    def given(self, string):
        self.behave_as('Given ' + string)

    def when(self, string):
        self.behave_as('When ' + string)

    def then(self, string):
        self.behave_as('Then ' + string)


class TestCase(unittest.TestCase):
    """
    The base test class for tests compiled from Gherkin features.
    """

    @classmethod
    def setUpClass(cls):
        cls.before_feature(cls.feature)

    @classmethod
    def tearDownClass(cls):
        cls.after_feature(cls.feature)

    @classmethod
    def block_constructors(cls):
        """
        Constructors for the parsed blocks.
        """

        return {
            'step': partial(TestStep, cls),
        }

    @classmethod
    def behave_as(cls, context_step, string):
        """
        Run the steps described by the given string in the context of the
        step.
        """

        steps = context_step.parse_steps_from_string(
            string,
            constructors=cls.block_constructors(),
        )

        for step in steps:
            # TODO: what attributes do the steps need?
            try:
                step.scenario = context_step.scenario
            except AttributeError:
                step.background = context_step.background

            step, func, args, kwargs = cls.prepare_step(step)

            func(step, *args, **kwargs)

    @classmethod
    def from_file(cls, file):
        """
        Construct a test class from a feature file.
        """

        feature = Feature.from_file(
            file,
            constructors=cls.block_constructors(),
        )

        background = cls.make_background(feature.background)
        scenarios = [
            cls.make_scenario(scenario, i + 1)
            for i, scenario in enumerate(feature.scenarios)
        ]

        before_feature, after_feature = \
            CALLBACK_REGISTRY.before_after('feature')

        members = {
            'feature': feature,
            'background': background,
            'before_feature': staticmethod(before_feature),
            'after_feature': staticmethod(after_feature),
        }

        members.update({
            scenario.__name__: scenario
            for scenario in scenarios
        })

        class_name = always_str(feature.name)

        return type(class_name, (cls,), members)

    @classmethod
    def make_background(cls, background):
        """
        Construct a method running the background steps.
        """

        if background is None:
            result = make_function('def background(self): pass')
        else:
            result = cls.make_steps(background, background.steps)

        return result

    @classmethod
    def make_scenario(cls, scenario, index):
        """
        Construct a method running the scenario steps.

        index is the 1-based number of the scenario in the feature.
        """

        if scenario.outlines:
            source = 'def run_outlines(self):\n' + '\n'.join(
                '    outline{i}(self)'.format(i=i)
                for i in range(len(scenario.outlines))
            )

            context = {
                'outline' + str(i): cls.make_steps(scenario,
                                                   steps,
                                                   call_background=True,
                                                   outline=outline)
                for i, (outline, steps) in enumerate(scenario.evaluated)
            }

            # TODO: Line numbers?
            result = make_function(
                source=source,
                context=context,
                source_file=scenario.feature.described_at.file,
                name=scenario.name,
            )
        else:
            result = cls.make_steps(scenario,
                                    scenario.steps,
                                    call_background=True)

        result.is_scenario = True
        result.scenario_index = index

        return result

    @classmethod
    def prepare_step(cls, step):
        """
        Find a definition for the step.

        Returns a tuple of: (step, func, args, kwargs), where:
        - step is the original step
        - func is the function to run (wrapped in callbacks)
        - args and kwargs are the arguments to pass to the function
        """

        func, args, kwargs = STEP_REGISTRY.match_step(step)
        func = CALLBACK_REGISTRY.wrap('step', func, step)

        return (step, func, args, kwargs)

    @classmethod
    def make_steps(cls, step_container, steps,
                   call_background=False, outline=None):
        """
        Construct a method calling the specified steps.

        The method will have debugging information corresponding to the lines
        in the feature file.
        """

        assert len(steps) > 0

        step_definitions = [
            cls.prepare_step(step)
            for step in steps
        ]

        source = 'def run_steps(self):\n'
        if call_background:
            source += '    self.background()\n'
        source += '\n'.join(
            '    func{i}(step{i}, *args{i}, **kwargs{i})'.format(i=i)
            for i in range(len(step_definitions))
        )
        source = ast.parse(source)

        # Set locations of the steps
        for step, step_call in zip(steps, source.body[0].body[1:]):
            for node in ast.walk(step_call):
                node.lineno = step.described_at.line

        # Supply all the step functions and arguments
        context = {}
        for i, (step, func, args, kwargs) in enumerate(step_definitions):
            context.update({
                k + str(i): v for k, v in {
                    'step': step,
                    'func': func,
                    'args': args,
                    'kwargs': kwargs,
                }.items()
            })

        # Function name
        try:
            func_name = step_container.name
            is_background = False
        except AttributeError:
            # This is a background step
            func_name = 'background'
            is_background = True

        run_steps = make_function(
            source=source,
            context=context,
            source_file=step.described_at.file,
            name=func_name,
        )

        if not is_background:
            run_steps = CALLBACK_REGISTRY.wrap('example', run_steps,
                                               step_container, outline, steps)

        return run_steps


# A decorator to add callbacks which wrap the steps tighter than all the user
# callbacks.
inner_around = CallbackDecorator(CALLBACK_REGISTRY, 'around',
                                 priority_class=PriorityClass.SYSTEM_INNER)


@inner_around.each_step
@contextmanager
def set_passed_failed(step):
    """
    Set the 'failed' property of the step.
    """

    try:
        yield
        step.passed = True
        step.failed = False
    except:
        step.passed = False
        step.failed = True
        raise
