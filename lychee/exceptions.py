class LettuceSyntaxError(SyntaxError):
    def __init__(self, filename, string):
        self.filename = filename
        self.string = string

        msg = "Syntax error at: {filename}\n{string}".format(
            filename=filename, string=string)

        super(LettuceSyntaxError, self).__init__(msg)


class LettuceSyntaxWarning(SyntaxWarning):
    pass


class StepLoadingError(Exception):
    """Raised when a step cannot be loaded."""
    pass
