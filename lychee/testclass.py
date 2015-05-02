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
import unittest

from lychee.codegen import make_function
from lychee.parser import Feature
from lychee.registry import CALLBACK_REGISTRY, STEP_REGISTRY
from lychee.utils import always_str


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
    def from_file(cls, file):
        """
        Construct a test class from a feature file.
        """

        feature = Feature.from_file(file)

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
            result = cls.make_steps(background.steps)

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
        result.scenario_index = index

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
            step_container = first_step.scenario
            func_name = step_container.name
        except AttributeError:
            # This is a background step
            step_container = first_step.background
            func_name = 'background'

        run_steps = make_function(
            source=source,
            context=context,
            source_file=step.described_at.file,
            name=func_name,
        )

        run_steps = CALLBACK_REGISTRY.wrap('example', run_steps,
                                           step_container)

        return run_steps
