import unittest

from lychee.parser import Feature
from lychee.registry import STEP_REGISTRY


def const(value):
    """
    A function accepting any arguments and returning the specified value.
    """

    return lambda *args, **kwargs: value


def rename(name, func):
    """
    Set the function name.
    """

    func.__name__ = name
    # TODO: __qualname__?
    return func


class TestCase(unittest.TestCase):
    """
    The base test class for tests compiled from Gherkin features.
    """

    # TODO: Create a metaclass for this one, so the invocations can be:
    # class MyFeature(feature, TestCase): pass

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

        # TODO: Make a method?
        # TODO: inject line/file information
        return type(feature.name, (cls,), cls.make_members(
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
            result = const(True)
        else:
            result = self.make_steps(background.steps)

        # TODO: inject line/file information
        return rename('background', result)

    @classmethod
    def make_scenario(cls, scenario):
        """
        Construct a method running the scenario steps.
        """

        # TODO: outlines

        result = cls.make_steps(scenario.steps,
                                before=lambda self: self.background())

        # TODO: inject line/file information
        return rename('test_' + scenario.name, result)

    @classmethod
    def make_steps(cls, steps, before=const(None)):
        """
        Construct a method calling the specified steps.
        """

        step_definitions = [
            (step, STEP_REGISTRY.match_step(step))
            for step in steps
        ]

        # TODO: replace with code generation
        def run_steps(self):
            before(self)
            for step, (func, kwargs) in step_definitions:
                # TODO: what does Lettuce pass as 'self'/'step'?
                func(step, **kwargs)

        return run_steps
