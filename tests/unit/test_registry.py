# -*- coding: utf-8 -*-
"""
Test step and callback registry.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import unittest

from nose.tools import (
    assert_equal,
    assert_raises,
)

from aloe.registry import (
    CallbackDecorator,
    CallbackDict,
    PriorityClass,
    StepDict,
)
from aloe.exceptions import (
    StepLoadingError,
    undefined_step,
)

from tests.utils import appender, before_after


class FakeStep(object):
    """A fake step object to use in matching."""

    def __init__(self, sentence):
        self.sentence = sentence


def assert_matches(step_dict, sentence, func_args):
    """
    Assert what a given sentence matches in a step dictionary.

    :param StepDict step_dict: Step dictionary to check
    :param sentence str: Sentence to match
    :param func_args (callable, tuple, dict): Expected function and arguments
    """

    assert_equal(step_dict.match_step(FakeStep(sentence)), func_args)


def assert_no_match(step_dict, sentence):
    """Assert that no match is found for a sentence in a step dictionary."""

    assert_matches(step_dict, sentence, (undefined_step, (), {}))


def test_StepDict_raise_StepLoadingError_if_first_argument_is_not_a_regex():
    """
    aloe.STEP_REGISTRY.load(step, func) should raise an error if step is
    not a regex
    """
    steps = StepDict()
    with assert_raises(StepLoadingError):
        steps.load("an invalid regex;)", lambda: "")


def test_StepDict_can_load_a_step_composed_of_a_regex_and_a_function():
    """
    aloe.STEP_REGISTRY.load(step, func) append item(step, func) to
    STEP_REGISTRY
    """
    steps = StepDict()

    def func():  # pylint:disable=missing-docstring
        return ""

    step = "a step to test"
    steps.load(step, func)

    assert_matches(steps, step, (func, (), {}))


def test_replacing_step():
    """
    Test registering a different step with the same sentence.
    """

    def func1():
        """First function to register as a step."""
        pass

    def func2():
        """Second function to register as a step."""
        pass

    steps = StepDict()

    # This has to be more than re._MAXCACHE; currently 100 on Python 2.7 and
    # 512 on Python 3.5
    step_count = 1024

    sentence = "sentence {0}".format

    # Register some steps
    for num in range(step_count):
        steps.load(sentence(num), func1)

    # Register the same steps again
    for num in range(step_count):
        steps.load(sentence(num), func2)

    # func2 should have replaced func1 everywhere
    for num in range(step_count):
        assert_matches(steps, sentence(num), (func2, (), {}))


def test_StepDict_load_a_step_return_the_given_function():
    """
    aloe.STEP_REGISTRY.load(step, func) returns func
    """
    steps = StepDict()

    def func():  # pylint:disable=missing-docstring
        return ""

    assert_equal(steps.load("another step", func), func)


def test_StepDict_can_extract_a_step_sentence_from_function_name():
    """
    aloe.STEP_REGISTRY.extract_sentence(func) parse func name and return
    a sentence
    """
    steps = StepDict()

    def a_step_sentence():  # pylint:disable=missing-docstring
        pass
    assert_equal("A step sentence", steps.extract_sentence(a_step_sentence))


def test_StepDict_can_extract_a_step_sentence_from_function_doc():
    """
    aloe.STEP_REGISTRY.extract_sentence(func) parse func doc and return
    a sentence
    """
    steps = StepDict()

    def a_step_func():
        """A step sentence"""
        pass
    assert_equal("A step sentence", steps.extract_sentence(a_step_func))


def test_StepDict_can_load_a_step_from_a_function():
    """
    aloe.STEP_REGISTRY.load_func(func) append item(step, func) to
    STEP_REGISTRY
    """
    steps = StepDict()

    def a_step_to_test():  # pylint:disable=missing-docstring
        pass

    steps.load_func(a_step_to_test)

    assert_matches(steps, "A step to test", (a_step_to_test, (), {}))


def test_StepDict_can_load_steps_from_an_object():
    """
    aloe.STEP_REGISTRY.load_steps(obj) append all obj methods to
    STEP_REGISTRY
    """
    steps = StepDict()

    class LotsOfSteps(object):
        """A class defining some steps."""

        def step_1(self):  # pylint:disable=missing-docstring
            pass

        def step_2(self):
            """Doing something"""
            pass

    step_list = LotsOfSteps()
    steps.load_steps(step_list)

    assert_matches(steps, "Step 1", (step_list.step_1, (), {}))
    assert_matches(steps, "Doing something", (step_list.step_2, (), {}))


def test_StepDict_can_exclude_methods_when_load_steps():
    """
    aloe.STEP_REGISTRY.load_steps(obj) don't load exluded attr in
    STEP_REGISTRY
    """
    steps = StepDict()

    class LotsOfSteps(object):
        """A class defining some steps."""
        exclude = ["step_1"]

        def step_1(self):  # pylint:disable=missing-docstring
            pass

        def step_2(self):
            """Doing something"""
            pass

    step_list = LotsOfSteps()
    steps.load_steps(step_list)

    assert_no_match(steps, "Step 1")
    assert_matches(steps, "Doing something", (step_list.step_2, (), {}))


def test_StepDict_can_exclude_callable_object_when_load_steps():
    """
    aloe.STEP_REGISTRY.load_steps(obj) don't load callable objets in
    STEP_REGISTRY
    """
    steps = StepDict()

    class NoStep(object):
        """A class defining something that's not a step."""
        class NotAStep(object):
            """A callable which isn't a step."""
            def __call__(self):
                pass

    no_step = NoStep()
    steps.load_steps(no_step)

    assert len(steps) == 0


def test_unload_reload():
    """
    Test unloading and then reloading the step.
    """

    def step():  # pylint:disable=missing-docstring
        pass

    steps = StepDict()

    # Load
    steps.step(r'My step (\d)')(step)
    steps.step(r'Another step (\d)')(step)

    assert_matches(steps, "My step 1", (step, ('1',), {}))
    assert_matches(steps, "Another step 1", (step, ('1',), {}))

    # Members added to step by registering it
    # pylint:disable=no-member

    # Unload
    step.unregister()

    assert_no_match(steps, "My step 1")
    assert_no_match(steps, "Another step 1")

    # Should be a no-op
    step.unregister()

    assert_no_match(steps, "My step 1")
    assert_no_match(steps, "Another step 1")

    # Reload
    steps.step(r'My step (\d)')(step)

    assert_matches(steps, "My step 1", (step, ('1',), {}))


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

        self.before.all(appender(sequence, 'before'))

        self.around.all(before_after(
            appender(sequence, 'around_before'),
            appender(sequence, 'around_after')
        ))

        self.after.all(appender(sequence, 'after'))

        wrapped = appender(sequence, 'wrapped')

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

        self.before.all(appender(sequence, 'before'))

        self.around.all(before_after(
            appender(sequence, 'around_before'),
            appender(sequence, 'around_after')
        ))

        self.after.all(appender(sequence, 'after'))

        before, after = self.callbacks.before_after('all')

        before('before_arg1', 'before_arg2')
        after('after_arg1', 'after_arg2')

        self.assertEqual(sequence, [
            ('before', 'before_arg1', 'before_arg2'),
            ('around_before', 'before_arg1', 'before_arg2'),
            ('around_after', 'before_arg1', 'before_arg2'),
            ('after', 'after_arg1', 'after_arg2'),
        ])

    @staticmethod
    def before_after_hook(sequence, when):
        """A before/after hook appending to a sequence."""
        return lambda name: appender(sequence, when + name)

    @classmethod
    def around_hook(cls, sequence):
        """An around hook appending to a sequence."""
        return lambda name: before_after(
            cls.before_after_hook(sequence, 'around_before')(name),
            cls.before_after_hook(sequence, 'around_after')(name)
        )

    def test_priority(self):
        """
        Test callback priority.
        """

        self.maxDiff = None

        sequence = []

        for when in ('before', 'after', 'around'):
            add_callback = getattr(self, when).all
            if when == 'around':
                hook = self.around_hook(sequence)
            else:
                hook = self.before_after_hook(sequence, when)

            # Default priority is 0
            add_callback(hook('B1'))
            add_callback(hook('B2'))

            # Explicit lower (=earlier) priority
            add_callback(hook('A1'), priority=-10)
            add_callback(hook('A2'), priority=-10)

            # Explicit higher (=later) priority
            add_callback(hook('C1'), priority=10)
            add_callback(hook('C2'), priority=10)

            # Add a callback with a different priority class
            CallbackDecorator(self.callbacks, when,
                              priority_class=-1).all(hook('Z1'))
            CallbackDecorator(self.callbacks, when,
                              priority_class=1).all(hook('D1'))

        wrap = self.callbacks.wrap('all', appender(sequence, 'wrapped'))

        wrap()

        self.assertEqual([item for (item,) in sequence], [
            'beforeZ1',
            'beforeA1',
            'beforeA2',
            'beforeB1',
            'beforeB2',
            'beforeC1',
            'beforeC2',
            'beforeD1',

            'around_beforeZ1',
            'around_beforeA1',
            'around_beforeA2',
            'around_beforeB1',
            'around_beforeB2',
            'around_beforeC1',
            'around_beforeC2',
            'around_beforeD1',

            'wrapped',

            'around_afterD1',
            'around_afterC2',
            'around_afterC1',
            'around_afterB2',
            'around_afterB1',
            'around_afterA2',
            'around_afterA1',
            'around_afterZ1',

            'afterD1',
            'afterC2',
            'afterC1',
            'afterB2',
            'afterB1',
            'afterA2',
            'afterA1',
            'afterZ1',
        ])

    def test_clear(self):
        """
        Test clearing the registry.
        """

        def prepare_hooks():
            """Set up various hooks to test clearing only some of them."""
            callbacks = CallbackDict()
            sequence = []

            for when in ('before', 'after', 'around'):
                add_callback = CallbackDecorator(callbacks, when).all
                if when == 'around':
                    hook = self.around_hook(sequence)
                else:
                    hook = self.before_after_hook(sequence, when)

                # Default priority class
                add_callback(hook('Default'))

                # Default priority class, specifying a name
                add_callback(hook('Named'), name='named')

                # Different priority classes
                CallbackDecorator(callbacks, when,
                                  priority_class=-1).all(hook('Minus'))
                CallbackDecorator(callbacks, when,
                                  priority_class=1).all(hook('Plus'))

                # Different priority class, specifying a name
                CallbackDecorator(callbacks, when,
                                  priority_class=1).all(hook('PlusNamed'),
                                                        name='named')

            return callbacks, sequence

        # Verify ordering without clearing anything
        callbacks, sequence = prepare_hooks()
        callbacks.wrap('all', appender(sequence, 'wrapped'))()

        self.assertEqual([item for (item,) in sequence], [
            'beforeMinus',
            'beforeDefault',
            'beforeNamed',
            'beforePlus',
            'beforePlusNamed',

            'around_beforeMinus',
            'around_beforeDefault',
            'around_beforeNamed',
            'around_beforePlus',
            'around_beforePlusNamed',

            'wrapped',

            'around_afterPlusNamed',
            'around_afterPlus',
            'around_afterNamed',
            'around_afterDefault',
            'around_afterMinus',

            'afterPlusNamed',
            'afterPlus',
            'afterNamed',
            'afterDefault',
            'afterMinus',
        ])

        # Only clear a particular name from the default priority class
        callbacks, sequence = prepare_hooks()
        callbacks.clear(priority_class=PriorityClass.USER,
                        name='named')
        callbacks.wrap('all', appender(sequence, 'wrapped'))()

        self.assertEqual([item for (item,) in sequence], [
            'beforeMinus',
            'beforeDefault',
            'beforePlus',
            'beforePlusNamed',

            'around_beforeMinus',
            'around_beforeDefault',
            'around_beforePlus',
            'around_beforePlusNamed',

            'wrapped',

            'around_afterPlusNamed',
            'around_afterPlus',
            'around_afterDefault',
            'around_afterMinus',

            'afterPlusNamed',
            'afterPlus',
            'afterDefault',
            'afterMinus',
        ])

        # Only clear the default priority class
        callbacks, sequence = prepare_hooks()
        callbacks.clear(priority_class=PriorityClass.USER)
        callbacks.wrap('all', appender(sequence, 'wrapped'))()

        self.assertEqual([item for (item,) in sequence], [
            'beforeMinus',
            'beforePlus',
            'beforePlusNamed',

            'around_beforeMinus',
            'around_beforePlus',
            'around_beforePlusNamed',

            'wrapped',

            'around_afterPlusNamed',
            'around_afterPlus',
            'around_afterMinus',

            'afterPlusNamed',
            'afterPlus',
            'afterMinus',
        ])

        # Clear all callbacks
        callbacks, sequence = prepare_hooks()
        callbacks.clear()
        callbacks.wrap('all', appender(sequence, 'wrapped'))()

        self.assertEqual([item for (item,) in sequence], [
            'wrapped',
        ])
