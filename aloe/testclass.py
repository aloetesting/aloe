"""
Base test class for tests generated from scenarios.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
# pylint:disable=redefined-builtin
from builtins import zip
from builtins import str
from builtins import range
from builtins import super
# pylint:enable=redefined-builtin

import ast
import unittest
from contextlib import contextmanager

from nose.plugins.attrib import attr

from aloe.codegen import make_function
from aloe.fs import path_to_module_name
from aloe.parser import (
    Background,
    Feature,
    Scenario,
    Step,
)
from aloe.registry import (
    CallbackDecorator,
    CALLBACK_REGISTRY,
    PriorityClass,
    STEP_REGISTRY,
)
from aloe.utils import identifier


class TestStep(Step):
    """
    A step with additional functions for the callbacks.
    """

    @property
    def testclass(self):
        """
        The test class containing this step (in a scenario or a background).
        """
        return self.feature.testclass

    test = None
    """
    The test currently running the step, or None if not currently in a test
    (e.g. in a `before_feature` callback).
    """

    def __init__(self, *args, **kwargs):
        """Initialize the step status."""
        self.failed = None
        self.passed = None
        super().__init__(*args, **kwargs)

    def behave_as(self, string):
        """Run the specified step in the current context."""
        self.test.behave_as(self, string)

    def given(self, string):
        """Run the specified 'Given' step in the current context."""
        self.behave_as(self.step_keyword('given') + string)

    def when(self, string):
        """Run the specified 'When' step in the current context."""
        self.behave_as(self.step_keyword('when') + string)

    def then(self, string):
        """Run the specified 'Then' step in the current context."""
        self.behave_as(self.step_keyword('then') + string)


class TestBackground(Background):
    """A background creating steps for testing."""
    step_class = TestStep


class TestScenario(Scenario):
    """A background creating steps for testing."""
    step_class = TestStep


class TestFeature(Feature):
    """A feature creating steps for testing."""
    background_class = TestBackground
    scenario_class = TestScenario


class TestCase(unittest.TestCase):
    """
    The base test class for tests compiled from Gherkin features.
    """

    feature = None  # Will be supplied when constructing derived classes

    @classmethod
    def before_feature(cls, feature):
        """Call feature-level before callbacks."""
        raise NotImplementedError(
            "This should be supplied when constructing derived classes.")

    @classmethod
    def after_feature(cls, feature):
        """Call feature-level after callbacks."""
        raise NotImplementedError(
            "This should be supplied when constructing derived classes.")

    # Methods for the use of the tested code

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.before_feature(cls.feature)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.after_feature(cls.feature)

    def behave_as(self, context_step, string):
        """
        Run the steps described by the given string in the context of the
        step.
        """

        steps = context_step.parse_steps_from_string(string)

        # Copy necessary attributes onto new steps
        for step in steps:
            step.test = self

            try:
                step.scenario = context_step.scenario
            except AttributeError:
                step.background = context_step.background

            definition = self.prepare_step(step)

            definition['func'](definition['step'],
                               *definition['args'],
                               **definition['kwargs'])

    def shortDescription(self):
        return str(self)

    def __str__(self):
        test_method = getattr(self, self._testMethodName)
        return "%s (%s: %s)" % (
            test_method.scenario.name,
            path_to_module_name(self.feature.filename),
            self.feature.name,
        )

    # Methods for generating test classes

    @classmethod
    def from_file(cls, file_):
        """
        Construct a test class from a feature file.
        """

        feature = TestFeature.from_file(file_)

        background = cls.make_background(feature.background)
        scenarios = [
            example
            for i, scenario in enumerate(feature.scenarios)
            for example in cls.make_examples(scenario, i + 1)
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

        class_name = identifier(feature.name)

        testclass = type(class_name, (cls,), members)
        testclass.feature.testclass = testclass
        return testclass

    @classmethod
    def make_background(cls, background):
        """
        Construct a method running the background steps.
        """

        if background is None:
            result = make_function('def background(self): pass')
        else:
            result = cls.make_steps(background,
                                    background.steps,
                                    is_background=True)

        return result

    @classmethod
    def make_examples(cls, scenario, index):
        """
        Construct methods for running all the examples of a scenario.

        index is the 1-based number of the scenario in the feature.
        """

        if scenario.outlines:
            for i, (outline, steps) in enumerate(scenario.evaluated, 1):
                # Create a function calling the real scenario example to show
                # the right location in the outline
                source = """
def run_example(self):
    outline(self)
                """
                source = ast.parse(source)

                # Set location of the call
                for node in ast.walk(source.body[0].body[0]):
                    node.lineno = outline.line

                context = {
                    'outline': cls.make_steps(scenario,
                                              steps,
                                              is_background=False,
                                              outline=outline)
                }

                yield cls.make_example(
                    make_function(
                        source=source,
                        context=context,
                        source_file=scenario.feature.filename,
                        name='{}: Example {}'.format(scenario.name, i),
                    ),
                    scenario,
                    index,
                )
        else:
            yield cls.make_example(
                cls.make_steps(
                    scenario,
                    scenario.steps,
                    is_background=False,
                ),
                scenario,
                index,
            )

    @classmethod
    def make_example(cls, method, scenario, index):
        """
        Set the method attributes to associate it with given scenario and index.
        """

        method.is_example = True
        method.scenario = scenario
        method.scenario_index = index

        for tag in scenario.tags:
            method = attr(tag)(method)

        return method

    @classmethod
    def prepare_step(cls, step):
        """
        Find a definition for the step.

        Returns a dictionary of: step, func, args, kwargs, where:
        - step is the original step
        - func is the function to run (wrapped in callbacks)
        - args and kwargs are the arguments to pass to the function
        """

        func, args, kwargs = STEP_REGISTRY.match_step(step)
        func = CALLBACK_REGISTRY.wrap('step', func, step)

        return {
            'step': step,
            'func': func,
            'args': args,
            'kwargs': kwargs,
        }

    @classmethod
    def make_steps(cls, step_container, steps,
                   is_background, outline=None):
        """
        Construct either a scenario or a background calling the specified
        steps.

        The method will have debugging information corresponding to the lines
        in the feature file.
        """

        assert len(steps) > 0

        step_definitions = [
            cls.prepare_step(step)
            for step in steps
        ]

        source = 'def run_steps(self):\n'
        if not is_background:
            source += '    self.background()\n'
        source += '\n'.join(
            # This has to be a single statement, in order to set its source
            # location as a whole below
            """
    try:
        step{i}.test = self
        func{i}(step{i}, *args{i}, **kwargs{i})
    finally:
        step{i}.test = None
            """.format(i=i)
            for i in range(len(step_definitions))
        )
        source = ast.parse(source)

        # Set locations of the steps
        step_source = source.body[0].body
        if not is_background:
            # There is no source for the background() call
            step_source = step_source[1:]
        for step, step_call in zip(steps, step_source):
            for node in ast.walk(step_call):
                node.lineno = step.line

        # Supply all the step functions and arguments
        context = {
            k + str(i): v
            for i, definition in enumerate(step_definitions)
            for k, v in definition.items()
        }

        if is_background:
            func_name = 'background'
        else:
            func_name = step_container.name

        run_steps = make_function(
            source=source,
            context=context,
            source_file=step_container.filename,
            name=func_name,
        )

        if not is_background:
            run_steps = CALLBACK_REGISTRY.wrap('example', run_steps,
                                               step_container, outline, steps)

        return run_steps

    @classmethod
    def scenarios(cls):
        """
        Enumerate all the scenario method names in the test class, in the
        order they were declared in the feature, together with their indices.
        """

        scenarios = {
            name: method
            for name, method in cls.__dict__.items()
            if getattr(method, 'is_example', False)
        }

        with_indices = [
            (method.scenario_index, name)
            for name, method in scenarios.items()
        ]

        return sorted(with_indices)


# A decorator to add callbacks which wrap the steps tighter than all the user
# callbacks.
# pylint:disable=invalid-name
inner_around = CallbackDecorator(CALLBACK_REGISTRY, 'around',
                                 priority_class=PriorityClass.SYSTEM_INNER)
# pylint:enable=invalid-name


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
