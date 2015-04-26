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

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import zip
from builtins import str
from builtins import range
from future import standard_library
standard_library.install_aliases()

import ast
import sys
import unittest

from lychee.codegen import make_function
from lychee.parser import Feature
from lychee.registry import CALLBACK_REGISTRY, STEP_REGISTRY


class TestCase(unittest.TestCase):
    """
    The base test class for tests compiled from Gherkin features.
    """

    @classmethod
    def from_file(cls, file):
        """
        Construct a test class from a feature file.
        """

        feature = Feature.from_file(file)

        background = cls.make_background(feature.background)
        scenarios = [
            cls.make_scenario(scenario)
            for scenario in feature.scenarios
        ]

        class_name = feature.name
        if sys.version_info < (3, 0):
            class_name = class_name.encode()

        # TODO: Make a method?
        # TODO: inject line/file information
        return type(class_name, (cls,), cls.make_members(
            [background] + scenarios))

    @classmethod
    def make_members(cls, members):
        """
        Convert a list of test methods to a dictionary suitable for type
        construction.
        """

        return {
            m.__name__: m
            for m in members
        }

    @classmethod
    def make_background(cls, background):
        """
        Construct a method running the background steps.
        """

        if background is None:
            result = make_function('def background(self): pass')
        else:
            result = cls.make_steps(background.steps)

        return result

    @classmethod
    def make_scenario(cls, scenario):
        """
        Construct a method running the scenario steps.
        """

        if scenario.outlines:
            source = 'def run_outlines(self):\n' + '\n'.join(
                '    outline{i}(self)'.format(i=i)
                for i in range(len(scenario.outlines))
            )

            context = {
                'outline' + str(i): cls.make_steps(steps,
                                                   call_background=True)
                for i, (_, steps) in enumerate(scenario.evaluated)
            }

            # TODO: Line numbers?
            result = make_function(
                source=source,
                context=context,
                source_file=scenario.feature.described_at.file,
                name=scenario.name,
            )
        else:
            result = cls.make_steps(scenario.steps,
                                    call_background=True)

        result.is_scenario = True

        return result

    @classmethod
    def make_steps(cls, steps, call_background=False):
        """
        Construct a method calling the specified steps.

        The method will have debugging information corresponding to the lines
        in the feature file.
        """

        assert len(steps) > 0
        first_step = steps[0]

        step_definitions = [
            (step, CALLBACK_REGISTRY.wrap('step', func), args, kwargs)
            for step, func, args, kwargs in (
                (step,) + STEP_REGISTRY.match_step(step)
                for step in steps
            )
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
            func_name = first_step.scenario.name
        except AttributeError:
            # This is a background step
            func_name = 'background'

        run_steps = make_function(
            source=source,
            context=context,
            source_file=step.described_at.file,
            name=func_name,
        )

        run_steps = CALLBACK_REGISTRY.wrap('example', run_steps)

        return run_steps
