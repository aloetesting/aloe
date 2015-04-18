# -*- coding: utf-8 -*-
# <Lettuce - Behaviour Driven Development for python>
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
from builtins import object
import re

from lychee.registry import StepDict
from lychee.exceptions import StepLoadingError

from nose.tools import assert_raises, assert_equal


def test_StepDict_raise_StepLoadingError_if_load_first_argument_is_not_a_regex():
    u"lettuce.STEP_REGISTRY.load(step, func) should raise an error if step is not a regex"
    steps = StepDict()
    test_load = lambda: steps.load("an invalid regex;)", lambda: "")
    assert_raises(StepLoadingError, test_load)

def test_StepDict_can_load_a_step_composed_of_a_regex_and_a_function():
    u"lettuce.STEP_REGISTRY.load(step, func) append item(step, func) to STEP_REGISTRY"
    steps = StepDict()
    func = lambda: ""
    step = "a step to test"
    steps.load(step, func)

    step = re.compile(step, re.I | re.U)
    assert (step in steps)
    assert_equal(steps[step], func)

def test_StepDict_load_a_step_return_the_given_function():
    u"lettuce.STEP_REGISTRY.load(step, func) returns func"
    steps = StepDict()
    func = lambda: ""
    assert_equal(steps.load("another step", func), func)

def test_StepDict_can_extract_a_step_sentence_from_function_name():
    u"lettuce.STEP_REGISTRY._extract_sentence(func) parse func name and return a sentence"
    steps = StepDict()
    def a_step_sentence():
        pass
    assert_equal("A step sentence", steps._extract_sentence(a_step_sentence))

def test_StepDict_can_extract_a_step_sentence_from_function_doc():
    u"lettuce.STEP_REGISTRY._extract_sentence(func) parse func doc and return a sentence"
    steps = StepDict()
    def a_step_func():
        """A step sentence"""
        pass
    assert_equal("A step sentence", steps._extract_sentence(a_step_func))

def test_StepDict_can_load_a_step_from_a_function():
    u"lettuce.STEP_REGISTRY.load_func(func) append item(step, func) to STEP_REGISTRY"
    steps = StepDict()
    def a_step_to_test():
        pass

    steps.load_func(a_step_to_test)

    expected_sentence = re.compile("A step to test", re.I | re.U)
    assert (expected_sentence in steps)
    assert_equal(steps[expected_sentence], a_step_to_test)

def test_StepDict_can_load_steps_from_an_object():
    u"lettuce.STEP_REGISTRY.load_steps(obj) append all obj methods to STEP_REGISTRY"
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
    u"lettuce.STEP_REGISTRY.load_steps(obj) don't load exluded attr in STEP_REGISTRY"
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
    u"lettuce.STEP_REGISTRY.load_steps(obj) don't load callable objets in STEP_REGISTRY"
    steps = StepDict()
    class NoStep(object):
        class NotAStep(object):
            def __call__(self):
                pass

    no_step = NoStep()
    steps.load_steps(no_step)

    assert len(steps) == 0
