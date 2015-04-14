import ast
import unittest

from lychee.parser import Feature
from lychee.registry import CALLBACK_REGISTRY, STEP_REGISTRY


def const(value):
    """
    A function accepting any arguments and returning the specified value.
    """

    return lambda *args, **kwargs: value


def rename(name, func):
    """
    Set the function name.
    """

    # TODO: What attributes are actually needed?
    func.__name__ = name
    func.__qualname__ == name
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
            result = rename('background', const(True))
        else:
            result = cls.make_steps(background.steps)

        return result

    @classmethod
    def make_scenario(cls, scenario):
        """
        Construct a method running the scenario steps.
        """

        # TODO: outlines

        result = cls.make_steps(scenario.steps,
                                before=lambda self: self.background())

        result.is_scenario = True

        return result

    @classmethod
    def make_steps(cls, steps, before=const(None)):
        """
        Construct a method calling the specified steps.

        The method will have debugging information corresponding to the lines
        in the feature file.
        """

        assert len(steps) > 0
        first_step = steps[0]

        feature = first_step.feature

        step_definitions = [
            (step, CALLBACK_REGISTRY.wrap('step', func), args, kwargs)
            for step, func, args, kwargs in (
                (step,) + STEP_REGISTRY.match_step(step)
                for step in steps
            )
        ]

        func = ast.parse(
            'def run_steps(self):\n    before(self)\n' + '\n'.join(
                '    func{i}(step{i}, *args{i}, **kwargs{i})'.format(i=i)
                for i in range(len(step_definitions))
            )
        )

        # Set function name and location
        try:
            context = first_step.scenario
            func_name = context.name
        except AttributeError:
            # This is a background step
            func_name = 'background'
        func.body[0].name = func_name

        # Set locations of the steps
        for step, step_call in zip(steps, func.body[0].body[1:]):
            for node in ast.walk(step_call):
                node.lineno = step.described_at.line

        code = compile(func, feature.described_at.file, 'exec')

        # Supply all the step functions and arguments
        glob = {
            'before': before,
        }
        for i, (step, func, args, kwargs) in enumerate(step_definitions):
            glob.update({
                k + str(i): v for k, v in {
                    'step': step,
                    'func': func,
                    'args': args,
                    'kwargs': kwargs,
                }.items()
            })
        eval(code, glob)

        # The result exists in the globals
        run_steps = glob[func_name]

        run_steps = CALLBACK_REGISTRY.wrap('example', run_steps)

        return run_steps
