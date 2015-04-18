from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import super
from future import standard_library
standard_library.install_aliases()
class LettuceSyntaxError(SyntaxError):
    def __init__(self, filename, string):
        self.filename = filename
        self.string = string

        msg = "Syntax error at: {filename}\n{string}".format(
            filename=filename, string=string)

        super().__init__(msg)


class LettuceSyntaxWarning(SyntaxWarning):
    pass


class StepLoadingError(Exception):
    """Raised when a step cannot be loaded."""
    pass


class NoDefinitionFound(Exception):
    """
    Exception raised when there is no suitable step definition for a step.
    """

    def __init__(self, step):
        self.step = step
        super().__init__('The step r"%s" is not defined' % self.step.sentence)
