"""
Exception classes
"""


class AloeSyntaxError(SyntaxError):
    """A syntax error in a feature file."""
    def __init__(self, filename, string):
        self.filename = filename
        self.string = string

        msg = "Syntax error at: {filename}\n{string}".format(
            filename=filename, string=string)

        super().__init__(msg)


class StepLoadingError(Exception):
    """A step definition cannot be registered."""
    pass


class StepDiscoveryError(Exception):
    """A step definition file cannot be imported."""
    pass


class NoDefinitionFound(Exception):
    """
    Exception raised when there is no suitable step definition for a step.
    """

    def __init__(self, step):
        self.step = step
        super().__init__('The step r"%s" is not defined' % self.step.sentence)


def undefined_step(step, *args, **kwargs):
    """
    A fallback step used when no suitable step definition was found.

    Raises a NoDefinitionFound exception when the scenario is run.
    """
    raise NoDefinitionFound(step)
