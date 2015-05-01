# -*- coding: utf-8 -*-
# Lychee - Cucumber runner for Python based on Lettuce and Nose
# Copyright (C) <2010-2012>  Gabriel Falcão <gabriel@nacaolivre.org>
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
from future import standard_library
standard_library.install_aliases()

import re
import unittest
from contextlib import contextmanager

from nose.tools import assert_raises, assert_equal

from lychee.registry import (
    CallbackDecorator,
    CallbackDict,
    StepDict,
)
from lychee.exceptions import StepLoadingError


def test_StepDict_raise_StepLoadingError_if_first_argument_is_not_a_regex():
    """
    lettuce.STEP_REGISTRY.load(step, func) should raise an error if step is
    not a regex
    """
    steps = StepDict()
    with assert_raises(StepLoadingError):
        steps.load("an invalid regex;)", lambda: "")


def test_StepDict_can_load_a_step_composed_of_a_regex_and_a_function():
    """
    lettuce.STEP_REGISTRY.load(step, func) append item(step, func) to
    STEP_REGISTRY
    """
    steps = StepDict()

    def func():
        return ""

    step = "a step to test"
    steps.load(step, func)

    step = re.compile(step, re.I | re.U)
    assert (step in steps)
    assert_equal(steps[step], func)


def test_StepDict_load_a_step_return_the_given_function():
    """
    lettuce.STEP_REGISTRY.load(step, func) returns func
    """
    steps = StepDict()

    def func():
        return ""

    assert_equal(steps.load("another step", func), func)


def test_StepDict_can_extract_a_step_sentence_from_function_name():
    """
    lettuce.STEP_REGISTRY._extract_sentence(func) parse func name and return
    a sentence
    """
    steps = StepDict()

    def a_step_sentence():
        pass
    assert_equal("A step sentence", steps._extract_sentence(a_step_sentence))


def test_StepDict_can_extract_a_step_sentence_from_function_doc():
    """
    lettuce.STEP_REGISTRY._extract_sentence(func) parse func doc and return
    a sentence
    """
    steps = StepDict()

    def a_step_func():
        """A step sentence"""
        pass
    assert_equal("A step sentence", steps._extract_sentence(a_step_func))


def test_StepDict_can_load_a_step_from_a_function():
    """
    lettuce.STEP_REGISTRY.load_func(func) append item(step, func) to
    STEP_REGISTRY
    """
    steps = StepDict()

    def a_step_to_test():
        pass

    steps.load_func(a_step_to_test)

    expected_sentence = re.compile("A step to test", re.I | re.U)
    assert (expected_sentence in steps)
    assert_equal(steps[expected_sentence], a_step_to_test)


def test_StepDict_can_load_steps_from_an_object():
    """
    lettuce.STEP_REGISTRY.load_steps(obj) append all obj methods to
    STEP_REGISTRY
    """
    steps = StepDict()

    class LotsOfSteps(object):

        def step_1(self):
            pass

        def step_2(self):
            """Doing something"""
            pass

    step_list = LotsOfSteps()
    steps.load_steps(step_list)

    expected_sentence1 = re.compile("Step 1", re.I | re.U)
    expected_sentence2 = re.compile("Doing something", re.I | re.U)
    assert (expected_sentence1 in steps)
    assert (expected_sentence2 in steps)
    assert_equal(steps[expected_sentence1], step_list.step_1)
    assert_equal(steps[expected_sentence2], step_list.step_2)


def test_StepDict_can_exclude_methods_when_load_steps():
    """
    lettuce.STEP_REGISTRY.load_steps(obj) don't load exluded attr in
    STEP_REGISTRY
    """
    steps = StepDict()

    class LotsOfSteps(object):
        exclude = ["step_1"]

        def step_1(self):
            pass

        def step_2(self):
            """Doing something"""
            pass

    step_list = LotsOfSteps()
    steps.load_steps(step_list)

    expected_sentence1 = re.compile("Step 1", re.I | re.U)
    expected_sentence2 = re.compile("Doing something", re.I | re.U)
    assert (expected_sentence1 not in steps)
    assert (expected_sentence2 in steps)


def test_StepDict_can_exclude_callable_object_when_load_steps():
    """
    lettuce.STEP_REGISTRY.load_steps(obj) don't load callable objets in
    STEP_REGISTRY
    """
    steps = StepDict()

    class NoStep(object):
        class NotAStep(object):
            def __call__(self):
                pass

    no_step = NoStep()
    steps.load_steps(no_step)

    assert len(steps) == 0


def test_unload_reload():
    """
    Test unloading and then reloading the step.
    """

    def step():
        pass

    class StepDefinition(object):
        sentence = 'My step 1'

    steps = StepDict()

    # Load
    steps.step(r'My step (\d)')(step)

    assert len(steps) == 1
    assert steps.match_step(StepDefinition) == (step, ('1',), {})

    # Unload
    step.unregister()

    assert len(steps) == 0

    # Should be a no-op
    step.unregister()

    assert len(steps) == 0

    # Reload
    steps.step(step.sentence)(step)

    assert len(steps) == 1
    assert steps.match_step(StepDefinition) == (step, ('1',), {})


class CallbackDictTest(unittest.TestCase):
    """
    Test callback dictionary.
    """

    def setUp(self):
        self.callbacks = CallbackDict()

        self.before = CallbackDecorator(self.callbacks, 'before')
        self.around = CallbackDecorator(self.callbacks, 'around')
        self.after = CallbackDecorator(self.callbacks, 'after')

    def test_wrap(self):
        """
        Test wrapping functions.
        """

        sequence = []

        @self.before.all
        def before_call(*args):
            sequence.append(('before',) + args)

        @self.around.all
        @contextmanager
        def around_call(*args):
            sequence.append(('around_before',) + args)
            yield
            sequence.append(('around_after',) + args)

        @self.after.all
        def after_call(*args):
            sequence.append(('after',) + args)

        def wrapped(*args):
            sequence.append(('wrapped',) + args)

        wrap = self.callbacks.wrap('all', wrapped, 'hook_arg1', 'hook_arg2')

        wrap('wrap_arg1', 'wrap_arg2')

        self.assertEqual(sequence, [
            ('before', 'hook_arg1', 'hook_arg2'),
            ('around_before', 'hook_arg1', 'hook_arg2'),
            ('wrapped', 'wrap_arg1', 'wrap_arg2'),
            ('around_after', 'hook_arg1', 'hook_arg2'),
            ('after', 'hook_arg1', 'hook_arg2'),
        ])

    def test_before_after(self):
        """
        Test before_after.
        """

        sequence = []

        @self.before.all
        def before_call(*args):
            sequence.append(('before',) + args)

        @self.around.all
        @contextmanager
        def around_call(*args):
            sequence.append(('around_before',) + args)
            yield
            sequence.append(('around_after',) + args)

        @self.after.all
        def after_call(*args):
            sequence.append(('after',) + args)

        before, after = self.callbacks.before_after('all')

        before('before_arg1', 'before_arg2')
        after('after_arg1', 'after_arg2')

        self.assertEqual(sequence, [
            ('before', 'before_arg1', 'before_arg2'),
            ('around_before', 'before_arg1', 'before_arg2'),
            ('around_after', 'before_arg1', 'before_arg2'),
            ('after', 'after_arg1', 'after_arg2'),
        ])
